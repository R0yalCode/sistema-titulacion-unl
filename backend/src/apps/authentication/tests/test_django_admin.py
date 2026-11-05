"""Smoke tests de la consola administrativa de Django (S1-T04, ADR-0009).

Verifica que Django Admin carga con la configuración aprobada y que los
modelos inmutables del dominio son de solo consulta en la consola.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

URLS_ADMIN = [
    ("index", None),
    ("authentication_user_changelist", None),
    ("authentication_role_changelist", None),
    ("expedientes_expedientetitulacion_changelist", None),
    ("expedientes_historialestado_changelist", None),
    ("peticiones_catalogodocumental_changelist", None),
    ("peticiones_peticiondocumental_changelist", None),
    ("peticiones_documentoentregado_changelist", None),
    ("verificacion_checklistverification_changelist", None),
    ("verificacion_observacionaccionable_changelist", None),
    ("resoluciones_informeaptitud_changelist", None),
    ("resoluciones_declaratoriaaptitud_changelist", None),
    ("notificaciones_notificacioninterna_changelist", None),
    ("notificaciones_eventoauditoria_changelist", None),
]


class AdminSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superusuario = User.objects.create_superuser(
            "admin_smoke",
            "admin_smoke@example.com",
            "PasswordSeguro123!",
        )

    def setUp(self):
        self.client.force_login(self.superusuario)

    def test_admin_index_carga(self):
        resp = self.client.get(reverse("admin:index"))
        self.assertEqual(resp.status_code, 200)

    def test_modelos_registrados_cargan_changelist(self):
        for nombre, _ in URLS_ADMIN[1:]:
            with self.subTest(url=nombre):
                resp = self.client.get(reverse(f"admin:{nombre}"))
                self.assertEqual(resp.status_code, 200)

    def test_modelos_inmutables_no_tienen_agregar(self):
        urls_add = [
            "admin:expedientes_expedientetitulacion_add",
            "admin:peticiones_documentoentregado_add",
            "admin:resoluciones_informeaptitud_add",
            "admin:resoluciones_declaratoriaaptitud_add",
            "admin:verificacion_observacionaccionable_add",
            "admin:expedientes_historialestado_add",
        ]
        for nombre in urls_add:
            with self.subTest(url=nombre):
                resp = self.client.get(reverse(nombre))
                # devuelve 200 con formulario deshabilitado o 403: nunca debe permitir guardar
                if resp.status_code == 200:
                    self.assertContains(resp, "disabled")
                else:
                    self.assertEqual(resp.status_code, 403)

    def test_usuarios_screen_usa_admin_personalizado(self):
        resp = self.client.get(reverse("admin:authentication_user_changelist"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "admin_smoke")
