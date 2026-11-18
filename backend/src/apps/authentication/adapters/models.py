import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower

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
        constraints = [
            # Acceso por correo institucional: un correo identifica a una sola
            # cuenta, sin distinguir mayúsculas. Los correos vacíos (cuentas
            # sin correo) quedan fuera de la restricción.
            models.UniqueConstraint(
                Lower("email"),
                condition=~models.Q(email=""),
                name="unique_user_email_ci",
            )
        ]

    def has_role(self, role_name: str) -> bool:
        return self.role_assignments.filter(role__name=role_name).exists()

    def get_roles(self) -> list[str]:
        return list(self.role_assignments.values_list("role__name", flat=True))


# --- Segundo factor TOTP y confianza del dispositivo (AUTH-B) -------------
# Ver docs/autenticacion/politica-2fa.md. Ningún modelo guarda material
# secreto en claro: el secreto TOTP va cifrado (Fernet) y los tokens de
# reto, de confianza y los códigos de recuperación, solo como hash.


class MfaDevice(models.Model):
    """Autenticador TOTP (Google Authenticator u otra app RFC 6238)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "authentication.User", on_delete=models.CASCADE, related_name="mfa_device"
    )
    # Secreto base32 cifrado con MultiFernet (MFA_ENCRYPTION_KEYS).
    secret_encrypted = models.TextField()
    # Nulo mientras el registro no se ha confirmado con un primer código.
    confirmed_at = models.DateTimeField(null=True, blank=True)
    # Último periodo TOTP aceptado: impide reutilizar un código.
    last_used_step = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authentication_mfadevice"

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None

    def __str__(self):
        estado = "activo" if self.is_confirmed else "pendiente"
        return f"Autenticador de {self.user} ({estado})"


class MfaRecoveryCode(models.Model):
    """Código de recuperación de un solo uso (hash de Django)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="mfa_recovery_codes",
    )
    code_hash = models.CharField(max_length=256)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authentication_mfarecoverycode"


class MfaChallenge(models.Model):
    """Reto emitido tras validar la contraseña y antes del segundo factor."""

    class Proposito(models.TextChoices):
        SETUP = "SETUP", "Registro del autenticador"
        VERIFY = "VERIFY", "Verificación del segundo factor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="+"
    )
    # SHA-256 del token aleatorio entregado al cliente.
    token_hash = models.CharField(max_length=64, unique=True)
    purpose = models.CharField(max_length=8, choices=Proposito.choices)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "authentication_mfachallenge"


class TrustedDevice(models.Model):
    """Dispositivo de confianza: omite el TOTP hasta `expires_at`.

    El navegador solo guarda un token aleatorio en una cookie HttpOnly; la
    fecha de expiración y la revocación viven aquí y React no puede
    alterarlas.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="trusted_devices",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "authentication_trusteddevice"
        indexes = [models.Index(fields=["user", "expires_at"])]


class EventoAutenticacion(models.Model):
    """Bitácora de seguridad de autenticación (sin secretos ni códigos)."""

    class Tipo(models.TextChoices):
        LOGIN_FALLIDO = "LOGIN_FALLIDO", "Credenciales rechazadas"
        LOGIN_EXITOSO = "LOGIN_EXITOSO", "Sesión iniciada"
        MFA_REGISTRO_INICIADO = "MFA_REGISTRO_INICIADO", "Registro TOTP iniciado"
        MFA_REGISTRO_COMPLETADO = (
            "MFA_REGISTRO_COMPLETADO",
            "Registro TOTP completado",
        )
        MFA_VERIFICACION_FALLIDA = (
            "MFA_VERIFICACION_FALLIDA",
            "Código de segundo factor rechazado",
        )
        MFA_BLOQUEO = "MFA_BLOQUEO", "Segundo factor bloqueado temporalmente"
        MFA_RECUPERACION_USADA = (
            "MFA_RECUPERACION_USADA",
            "Código de recuperación utilizado",
        )
        MFA_RESTABLECIDO = "MFA_RESTABLECIDO", "Segundo factor restablecido"
        DISPOSITIVO_CONFIABLE_CREADO = (
            "DISPOSITIVO_CONFIABLE_CREADO",
            "Dispositivo de confianza registrado",
        )
        DISPOSITIVO_CONFIABLE_USADO = (
            "DISPOSITIVO_CONFIABLE_USADO",
            "Ingreso con dispositivo de confianza",
        )
        DISPOSITIVO_CONFIABLE_REVOCADO = (
            "DISPOSITIVO_CONFIABLE_REVOCADO",
            "Confianza de dispositivo revocada",
        )
        LOGOUT = "LOGOUT", "Cierre de sesión"
        CONTRASENA_RESTABLECIDA = (
            "CONTRASENA_RESTABLECIDA",
            "Contraseña restablecida por enlace",
        )
        MFA_RESTABLECIMIENTO_SOLICITADO = (
            "MFA_RESTABLECIMIENTO_SOLICITADO",
            "Restablecimiento del 2FA solicitado",
        )
        MFA_RESTABLECIMIENTO_RECHAZADO = (
            "MFA_RESTABLECIMIENTO_RECHAZADO",
            "Restablecimiento del 2FA rechazado",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=32, choices=Tipo.choices, db_index=True)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "authentication_eventoautenticacion"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "tipo", "created_at"])]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.tipo} {self.user or '-'}"
