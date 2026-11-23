"""Dataset local de pruebas de SGT-SIAAF (lote `sgt-siaaf-v1`).

Crea, de forma idempotente:

1. El catálogo académico SIMULADO ampliado (2 facultades y 5 carreras activas,
   códigos `MOCK-…`, `es_simulada=True`).
2. 10 cuentas por cada uno de los 8 roles reales (80), con identidades
   claramente ficticias y correos del dominio reservado `sgt-siaaf.example`,
   rol, ámbito (carrera o facultad, según el rol), cuenta activa y **sin MFA**.
   Para iniciar sesión en la interfaz, que solo admite el dominio institucional,
   use `--correo-institucional` en una base local.
3. El perfil MockSGA de los 10 estudiantes.
4. Expedientes en distintos estados, construidos solo con los servicios de
   negocio (creación, carga de documentos, envío, verificación, observación,
   subsanación, informe y declaratoria), con sus documentos y notificaciones.

Garantías:

- No modifica cuentas existentes (contraseña, roles, MFA, ámbito): solo crea
  las que faltan. Un correo, usuario o cédula ya usados no se reutilizan.
- La segunda ejecución no cambia nada y no regenera secretos MFA (este
  comando nunca crea ni toca `MfaDevice`).
- No borra datos. No concede `is_staff` ni `is_superuser`. No crea roles.
- La contraseña inicial se lee de `SEED_DATASET_PASSWORD` (obligatoria solo
  si hay cuentas por crear) y nunca se escribe en la salida.
- Solo escribe en una base registrada como desarrollo o en la temporal de
  pytest (`exigir_entorno_de_demostracion`).
- Se niega a ejecutarse con los settings de producción, si el entorno no
  permite la fuente simulada o si el correo saliente no es local (consola,
  memoria, archivo o nulo): estas cuentas nunca deben recibir mensajes.
- Las cuentas se identifican internamente con `RegistroDatasetSintetico`;
  la interfaz no muestra esa marca.
"""

import io
import os

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academico.adapters.management.commands.seed_mock_sga import uuid_mock
from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)
from apps.academico.services.auditoria import registrar_cambio
from apps.authentication.adapters.models import Role, User, UserRole
from apps.entorno_pruebas import dataset
from apps.entorno_pruebas.adapters.models import RegistroDatasetSintetico
from apps.expedientes.adapters.models import ExpedienteTitulacion
from core.adapters.entorno_demo import exigir_entorno_de_demostracion

ORIGEN = "seed_sgt_siaaf"
VARIABLE_CLAVE = "SEED_DATASET_PASSWORD"
BACKENDS_CORREO_LOCALES = (
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
    "django.core.mail.backends.filebased.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
)


def verificar_entorno():
    """Detiene el comando fuera de un entorno local seguro."""
    modulo = os.environ.get("DJANGO_SETTINGS_MODULE", "") or getattr(
        settings, "SETTINGS_MODULE", ""
    )
    if "production" in (modulo or ""):
        raise CommandError(
            "seed_sgt_siaaf no se ejecuta con los settings de producción."
        )
    if not getattr(settings, "ACADEMIC_PROFILE_MOCK_ALLOWED", False):
        raise CommandError(
            "Este entorno no permite la fuente académica simulada "
            "(ACADEMIC_PROFILE_MOCK_ALLOWED es falso). No se creó nada."
        )
    if getattr(settings, "ACADEMIC_PROFILE_PROVIDER", "") != "mock_sga":
        raise CommandError("ACADEMIC_PROFILE_PROVIDER debe ser 'mock_sga'.")
    if settings.EMAIL_BACKEND not in BACKENDS_CORREO_LOCALES:
        raise CommandError(
            "El correo saliente no es local (EMAIL_BACKEND). Las cuentas del "
            "dataset no se crean mientras el sistema pueda enviar correos reales."
        )


def pdf_ficticio(titulo: str) -> io.BytesIO:
    """PDF mínimo con contenido claramente ficticio y sin datos personales."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    lienzo = canvas.Canvas(buffer, pagesize=A4)
    lienzo.setTitle(titulo)
    lienzo.drawString(72, 770, titulo)
    lienzo.drawString(
        72, 750, "Documento ficticio del entorno local de pruebas de SGT-SIAAF."
    )
    lienzo.drawString(72, 735, "No contiene datos personales ni tiene validez oficial.")
    lienzo.showPage()
    lienzo.save()
    buffer.seek(0)
    buffer.name = f"{titulo.lower().replace(' ', '-')}.pdf"
    return buffer


class Command(BaseCommand):
    help = (
        "Crea el dataset local de pruebas (80 cuentas, perfiles MockSGA y "
        "expedientes en distintos estados). Idempotente; solo desarrollo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sin-escenarios",
            action="store_true",
            help="Solo cuentas, catálogo y perfiles; no crea expedientes.",
        )
        parser.add_argument(
            "--listar",
            action="store_true",
            help="Lista las cuentas del dataset (sin contraseñas) y termina.",
        )
        parser.add_argument(
            "--correo-institucional",
            action="store_true",
            help=(
                "Crea las cuentas nuevas con correo sgtdemo.* del dominio "
                "institucional, necesario para ingresar por la interfaz local."
            ),
        )

    # --- utilidades ---------------------------------------------------------

    def _marca(self, clave):
        return RegistroDatasetSintetico.objects.filter(
            lote=dataset.LOTE, clave=clave
        ).first()

    def _marcar(self, clave, objeto, instancia):
        RegistroDatasetSintetico.objects.create(
            lote=dataset.LOTE, clave=clave, objeto=objeto, objeto_id=str(instancia.pk)
        )

    def _usuario_de(self, persona):
        marca = self._marca(persona.clave)
        if marca is None:
            return None
        return User.objects.filter(pk=marca.objeto_id).first()

    # --- catálogo -----------------------------------------------------------

    def _catalogo(self):
        facultades = {}
        for datos in dataset.FACULTADES:
            facultad, creada = Facultad.objects.get_or_create(
                codigo=datos.codigo,
                defaults={
                    "id": uuid_mock(datos.codigo),
                    "nombre": datos.nombre,
                    "activa": True,
                    "es_simulada": True,
                },
            )
            if creada:
                registrar_cambio(
                    facultad, tipo=EventoCatalogoAcademico.Tipo.CREADO, origen=ORIGEN
                )
                self._marcar(f"facultad:{datos.codigo}", "facultad", facultad)
            facultades[datos.codigo] = facultad
        carreras = {}
        for datos in dataset.CARRERAS:
            carrera, creada = Carrera.objects.get_or_create(
                codigo=datos.codigo,
                defaults={
                    "id": uuid_mock(datos.codigo),
                    "nombre": datos.nombre,
                    "facultad": facultades[datos.facultad],
                    "activa": True,
                    "es_simulada": True,
                },
            )
            if creada:
                registrar_cambio(
                    carrera, tipo=EventoCatalogoAcademico.Tipo.CREADO, origen=ORIGEN
                )
                self._marcar(f"carrera:{datos.codigo}", "carrera", carrera)
            if carrera.facultad.codigo != datos.facultad:
                raise CommandError(
                    f"La carrera {datos.codigo} ya existe en otra facultad; no se "
                    "modifica."
                )
            carreras[datos.codigo] = carrera
        return facultades, carreras

    # --- cuentas ------------------------------------------------------------

    def _correo(self, usuario):
        if self.correo_institucional:
            return (
                f"{dataset.PREFIJO_CORREO_LOCAL}.{usuario}"
                f"@{settings.INSTITUTIONAL_EMAIL_DOMAIN}"
            )
        return f"{usuario}@{dataset.DOMINIO_CORREO}"

    def _identidad_libre(self, persona):
        candidatos = persona.candidatos_usuario()
        candidatos += [f"{candidatos[0]}{n}" for n in range(2, 50)]
        for usuario in candidatos:
            correo = self._correo(usuario)
            if User.objects.filter(username__iexact=usuario).exists():
                continue
            if User.objects.filter(email__iexact=correo).exists():
                continue
            return usuario, correo
        raise CommandError(f"Sin nombre de usuario libre para {persona.clave}.")

    def _cedula_libre(self, persona):
        cedula = persona.cedula
        desplazamiento = 0
        while User.objects.filter(cedula=cedula).exists() or (
            PerfilSGASimulado.objects.filter(identificacion=cedula).exists()
        ):
            desplazamiento += 1000
            cedula = f"99{int(persona.cedula[2:]) + desplazamiento:08d}"
        return cedula

    def _cuentas(self, facultades, carreras, clave):
        roles = {r.name: r for r in Role.objects.filter(name__in=dataset.ROLES)}
        faltantes = sorted(set(dataset.ROLES) - set(roles))
        if faltantes:
            raise CommandError(
                f"Faltan roles en la base de datos: {', '.join(faltantes)}. "
                "Este comando no crea roles (ejecute seed_initial_data)."
            )
        creadas = {rol: 0 for rol in dataset.ROLES}
        reutilizadas = {rol: 0 for rol in dataset.ROLES}
        for persona in dataset.personas():
            if self._usuario_de(persona) is not None:
                reutilizadas[persona.rol] += 1
                continue
            usuario, correo = self._identidad_libre(persona)
            carrera = carreras.get(persona.carrera) if persona.carrera else None
            facultad = facultades.get(persona.facultad) if persona.facultad else None
            user = User(
                username=usuario,
                email=correo,
                first_name=persona.nombres,
                last_name=persona.apellidos,
                cedula=self._cedula_libre(persona),
                carrera_id=carrera.id if carrera else None,
                # La facultad se deriva de la carrera cuando el rol tiene una.
                facultad_id=(
                    carrera.facultad_id
                    if carrera
                    else (facultad.id if facultad else None)
                ),
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            user.set_password(clave)
            user.save()
            UserRole.objects.create(user=user, role=roles[persona.rol])
            self._marcar(persona.clave, "usuario", user)
            creadas[persona.rol] += 1
        return creadas, reutilizadas

    # --- perfiles MockSGA ---------------------------------------------------

    def _perfiles(self, carreras):
        nuevos = 0
        for persona in dataset.personas():
            if persona.rol != "ESTUDIANTE":
                continue
            clave = f"perfil:{persona.clave}"
            if self._marca(clave) is not None:
                continue
            user = self._usuario_de(persona)
            if user is None or not user.cedula:
                continue
            if PerfilSGASimulado.objects.filter(identificacion=user.cedula).exists():
                continue
            carrera = carreras[persona.carrera]
            perfil = PerfilSGASimulado.objects.create(
                identificacion=user.cedula,
                nombres=user.first_name,
                apellidos=user.last_name,
                correo_institucional=user.email,
                codigo_carrera=carrera.codigo,
                codigo_facultad=carrera.facultad.codigo,
                activo=True,
            )
            registrar_cambio(
                perfil, tipo=EventoCatalogoAcademico.Tipo.CREADO, origen=ORIGEN
            )
            self._marcar(clave, "perfil_sga", perfil)
            nuevos += 1
        return nuevos

    # --- escenarios ---------------------------------------------------------

    def _actor(self, rol, *, carrera=None, facultad=None):
        for persona in dataset.personas():
            if persona.rol != rol:
                continue
            if carrera and persona.carrera != carrera:
                continue
            if facultad and persona.facultad != facultad:
                continue
            user = self._usuario_de(persona)
            if user is not None:
                return user
        raise CommandError(f"No hay una cuenta {rol} del dataset para el escenario.")

    def _cargar_documentos(self, expediente, estudiante, secretaria, cantidad=None):
        from apps.peticiones.services import cargar_documento, solicitar_emision

        peticiones = list(
            expediente.peticiones_documentales.select_related("requisito").order_by(
                "requisito__codigo_requisito"
            )
        )
        for peticion in peticiones[:cantidad]:
            solicitar_emision.execute(estudiante, peticion.id)
            # La Secretaría de Carrera carga lo que le corresponde emitir; el
            # resto lo carga el propio estudiante (reglas de cargar_documento).
            autor = (
                secretaria
                if peticion.dependencia_emisora == "SECRETARIA_CARRERA"
                else estudiante
            )
            archivo = pdf_ficticio(f"Requisito {peticion.requisito.codigo_requisito}")
            cargar_documento.execute(autor, peticion.id, archivo, archivo.name)

    def _escenario(self, persona, carreras):
        from apps.expedientes.services import (
            crear_expediente,
            enviar_expediente,
            iniciar_verificacion,
        )

        # En este paquete, `emitir_informe` y `declarar_aptitud` son las
        # funciones `execute` de sus módulos.
        from apps.resoluciones.services import declarar_aptitud, emitir_informe
        from apps.verificacion.services import (
            evaluar_checklist,
            registrar_observacion,
            subsanar_requisito,
        )

        estudiante = self._usuario_de(persona)
        facultad = dataset.FACULTAD_DE[persona.carrera]
        secretaria = self._actor("SECRETARIA_CARRERA", carrera=persona.carrera)
        abogado = self._actor("SECRETARIO_ABOGADO", facultad=facultad)
        decano = self._actor("DECANO", facultad=facultad)
        escenario = persona.escenario
        orden = [
            dataset.BORRADOR,
            dataset.ENVIADA,
            dataset.EN_VERIFICACION,
            dataset.OBSERVADA,
            dataset.SUBSANADA,
        ]

        expediente = crear_expediente.execute(estudiante)
        if escenario == dataset.BORRADOR:
            return expediente
        if escenario == dataset.BORRADOR_CON_DOCUMENTOS:
            self._cargar_documentos(expediente, estudiante, secretaria, cantidad=2)
            return expediente

        self._cargar_documentos(expediente, estudiante, secretaria)
        expediente = enviar_expediente.execute(expediente, actor=estudiante)
        if escenario == dataset.ENVIADA:
            return expediente

        expediente = iniciar_verificacion.execute(expediente.pk, actor=abogado)
        checklist = list(
            expediente.checklist_verificaciones.order_by("requisito__codigo_requisito")
        )
        evaluar_checklist.execute(abogado, checklist[0].id, "VERIFICADO")
        if escenario == dataset.EN_VERIFICACION:
            return expediente

        if escenario in orden[3:]:
            observado = checklist[1]
            peticion = expediente.peticiones_documentales.get(
                requisito=observado.requisito
            )
            registrar_observacion.execute(
                usuario=abogado,
                expediente_id=expediente.id,
                peticion_id=peticion.id,
                motivo_observacion=(
                    "El certificado no muestra la fecha de emisión. Cargue una "
                    "versión que la incluya."
                ),
            )
            if escenario == dataset.OBSERVADA:
                return expediente
            archivo = pdf_ficticio(
                f"Requisito {observado.requisito.codigo_requisito} v2"
            )
            subsanar_requisito.execute(
                usuario=estudiante,
                checklist_verification_id=observado.id,
                archivo=archivo,
                nombre_original=archivo.name,
            )
            return expediente

        for item in expediente.checklist_verificaciones.exclude(
            estado_verificacion="VERIFICADO"
        ):
            evaluar_checklist.execute(abogado, item.id, "VERIFICADO")
        emitir_informe(
            usuario=abogado,
            expediente_id=expediente.id,
            dictamen="APTO",
            fundamentacion="Requisitos del Art. 235 verificados.",
        )
        if escenario == dataset.INFORME_EMITIDO:
            return expediente
        declarar_aptitud(
            usuario=decano,
            expediente_id=expediente.id,
            archivo_memorando=pdf_ficticio("Memorando de declaratoria"),
        )
        return expediente

    def _escenarios(self, carreras):
        creados = 0
        for persona in dataset.personas():
            if (
                persona.rol != "ESTUDIANTE"
                or persona.escenario == dataset.SIN_EXPEDIENTE
            ):
                continue
            clave = f"escenario:{persona.clave}"
            if self._marca(clave) is not None:
                continue
            estudiante = self._usuario_de(persona)
            if estudiante is None:
                continue
            if ExpedienteTitulacion.objects.filter(estudiante=estudiante).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"{persona.clave}: ya tiene expedientes; no se crea el "
                        "escenario."
                    )
                )
                continue
            try:
                with transaction.atomic():
                    expediente = self._escenario(persona, carreras)
                    self._marcar(clave, "expediente", expediente)
            except CommandError:
                raise
            except Exception as error:
                raise CommandError(
                    f"No se pudo construir el escenario {persona.escenario} de "
                    f"{persona.clave}: {type(error).__name__}: {error}"
                ) from error
            creados += 1
        return creados

    # --- salida -------------------------------------------------------------

    def _listar(self):
        nombres_carrera = dict(Carrera.objects.values_list("codigo", "nombre"))
        nombres_facultad = dict(Facultad.objects.values_list("codigo", "nombre"))
        for persona in dataset.personas():
            user = self._usuario_de(persona)
            if user is None:
                continue
            ambito = nombres_carrera.get(persona.carrera) or nombres_facultad.get(
                persona.facultad, "—"
            )
            escenario = persona.escenario or ""
            self.stdout.write(
                f"{persona.rol:<24} {user.get_full_name():<36} {user.email:<40} "
                f"{ambito} {escenario}".rstrip()
            )

    def _resumen(self, creadas, reutilizadas, perfiles, escenarios):
        from apps.notificaciones.adapters.models import NotificacionInterna
        from apps.peticiones.adapters.models import DocumentoEntregado

        ids = list(
            RegistroDatasetSintetico.objects.filter(
                lote=dataset.LOTE, objeto="usuario"
            ).values_list("objeto_id", flat=True)
        )
        expedientes = ExpedienteTitulacion.objects.filter(estudiante_id__in=ids)
        documentos = DocumentoEntregado.objects.filter(
            peticion__expediente__in=expedientes
        )
        self.stdout.write(self.style.SUCCESS(f"Dataset {dataset.LOTE}:"))
        for rol in dataset.ROLES:
            self.stdout.write(
                f"  {rol:<24} creadas {creadas[rol]:>2}  "
                f"ya existentes {reutilizadas[rol]:>2}"
            )
        self.stdout.write(f"  Perfiles MockSGA nuevos: {perfiles}")
        self.stdout.write(f"  Escenarios nuevos: {escenarios}")
        por_estado = {}
        for estado in expedientes.values_list("estado", flat=True):
            por_estado[estado] = por_estado.get(estado, 0) + 1
        self.stdout.write(
            f"  Expedientes del dataset por estado: {dict(sorted(por_estado.items()))}"
        )
        self.stdout.write(
            "  Documentos: "
            f"{documentos.count()}"
            "  Notificaciones a cuentas del dataset: "
            f"{NotificacionInterna.objects.filter(usuario_destino_id__in=ids).count()}"
        )

    # --- entrada ------------------------------------------------------------

    def _clave(self):
        pendientes = [p for p in dataset.personas() if self._usuario_de(p) is None]
        if not pendientes:
            return None
        clave = os.environ.get(VARIABLE_CLAVE, "")
        if not clave.strip():
            raise CommandError(
                f"La variable de entorno {VARIABLE_CLAVE} es obligatoria para crear "
                f"las {len(pendientes)} cuentas pendientes. No se creó nada."
            )
        try:
            validate_password(clave)
        except ValidationError as error:
            raise CommandError(
                f"{VARIABLE_CLAVE} no cumple la política de contraseñas: "
                + " ".join(error.messages)
            ) from None
        return clave

    def handle(self, *args, **options):
        verificar_entorno()
        if options["listar"]:
            self._listar()
            return
        exigir_entorno_de_demostracion("seed_sgt_siaaf")
        self.correo_institucional = options["correo_institucional"]
        clave = self._clave()
        with transaction.atomic():
            facultades, carreras = self._catalogo()
            if clave is None:
                creadas = {rol: 0 for rol in dataset.ROLES}
                reutilizadas = {rol: dataset.CUENTAS_POR_ROL for rol in dataset.ROLES}
            else:
                creadas, reutilizadas = self._cuentas(facultades, carreras, clave)
            perfiles = self._perfiles(carreras)
        escenarios = 0 if options["sin_escenarios"] else self._escenarios(carreras)
        self._resumen(creadas, reutilizadas, perfiles, escenarios)
