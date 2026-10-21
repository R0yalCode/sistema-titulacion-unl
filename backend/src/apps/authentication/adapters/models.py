import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

ROLE_ESTUDIANTE = "ESTUDIANTE"
ROLE_SECRETARIA_CARRERA = "SECRETARIA_CARRERA"
ROLE_SECRETARIO_ABOGADO = "SECRETARIO_ABOGADO"
ROLE_ANALISTA_APOYO = "ANALISTA_APOYO"
ROLE_DECANO = "DECANO"
ROLE_DIRECTOR_CARRERA = "DIRECTOR_CARRERA"
ROLE_RESPONSABLE_DEPENDENCIA = "RESPONSABLE_DEPENDENCIA"
ROLE_ADMINISTRADOR = "ADMINISTRADOR"

ROLE_CHOICES = [
    (ROLE_ESTUDIANTE, "Estudiante"),
    (ROLE_SECRETARIA_CARRERA, "Secretaria de Carrera"),
    (ROLE_SECRETARIO_ABOGADO, "Secretario/a-Abogado/a"),
    (ROLE_ANALISTA_APOYO, "Analista de Apoyo"),
    (ROLE_DECANO, "Decano/a"),
    (ROLE_DIRECTOR_CARRERA, "Director de Carrera"),
    (ROLE_RESPONSABLE_DEPENDENCIA, "Responsable de Dependencia"),
    (ROLE_ADMINISTRADOR, "Administrador"),
]

cedula_validator = RegexValidator(
    regex=r"^[0-9]+$",
    message="La cédula debe contener únicamente dígitos.",
)


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True, choices=ROLE_CHOICES)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "authentication_role"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )
    role = models.ForeignKey("authentication.Role", on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authentication_userrole"
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_user_role")
        ]

    def __str__(self):
        return f"{self.user} -> {self.role}"


class UserManager(BaseUserManager):
    def create_user(
        self, username, email=None, password=None, cedula=None, **extra_fields
    ):
        user = self.model(
            username=username, email=email or "", cedula=cedula, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email=None, password=None, cedula=None, **extra_fields
    ):
        user = self.create_user(username, email=email, password=password, cedula=cedula)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cedula = models.CharField(
        max_length=20,
        unique=True,
        validators=[cedula_validator],
        null=True,
        blank=True,
    )
    carrera_id = models.UUIDField(null=True, blank=True)
    facultad_id = models.UUIDField(null=True, blank=True)

    objects = UserManager()

    class Meta:
        db_table = "authentication_user"
        indexes = [
            models.Index(fields=["carrera_id"]),
            models.Index(fields=["facultad_id"]),
        ]

    def has_role(self, role_name: str) -> bool:
        return self.role_assignments.filter(role__name=role_name).exists()

    def get_roles(self) -> list[str]:
        return list(self.role_assignments.values_list("role__name", flat=True))
