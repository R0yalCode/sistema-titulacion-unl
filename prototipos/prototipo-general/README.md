# SGT-SIAAF — Prototipo web de titulación

**Nueve vistas implementadas en HTML + CSS + JavaScript, navegables, responsive e interactivas.**  
**Destino:** mostrar al equipo y recoger opiniones, antes de implementar el frontend conectado a Django.

> **IMPORTANTE:** Esta es una **maqueta funcional local** con identidades y registros ficticios. **NO** se conecta al backend Django, PostgreSQL ni a SGA/SIAAF. **NO** tiene login real, envío de documentos, resoluciones de aptitud legal ni notificaciones operativas.

## Abrir en Windows (fácil)

1. Descomprime todo el archivo `.zip` en una carpeta, por ejemplo `Escritorio\SGT_SIAAF_Prototipo_Web`.
2. Haz **doble clic en `index.html`**, o en `INICIAR_WINDOWS.bat`.
3. Selecciona un perfil ficticio y pulsa **Entrar a la demostración**.
4. No hacen falta Docker, Node.js, Python ni paquetes externos para explorar las vistas.

Si el navegador restringe el uso de `sessionStorage` para archivos locales, la interfaz seguirá funcionando pero puede perder los cambios al recargar. Para tener un origen local estable, puedes abrir una terminal dentro de la carpeta y ejecutar:

```powershell
py -m http.server 5500
```

Luego visita **http://localhost:5500**. Este servidor expone solo los archivos de la carpeta en tu computadora; no lo publiques en Internet.

## Las 9 vistas

| N.º | Vista | Cómo acceder | Estado |
|---|---|---|---|
| 01 | Acceso al SGT-SIAAF | Pantalla inicial | **Simulación de perfiles**: no valida contraseñas ni emite JWT |
| 02 | Estudiante no habilitado | Perfil **Diego Demo, 7.º ciclo** | Conceptual: ciclo/créditos ficticios |
| 03 | Inicio del estudiante próximo a egresar | Perfil **Andrea Demo, 9.º ciclo** | Dashboard con cifras calculadas a partir de datos locales ficticios |
| 04 | Nueva solicitud de aptitud legal | **Nueva solicitud** | Formulario guiado, confirmación y generación de 5 requisitos locales |
| 05 | Mi expediente | **Mi expediente** | Estado `BORRADOR`, requisitos `PENDIENTE` / `SOLICITADO` |
| 06 | Nueva petición documental | Expediente → **Solicitar** | Modal interactivo, evita peticiones duplicadas localmente |
| 07 | Seguimiento de petición | **Mis peticiones** → Ver | Detalle registrado; hitos futuros marcados como no implementados |
| 08 | Bandeja del funcionario | Cambiar perfil → **Funcionario** | Filtros, búsqueda y separación de dependencias asignadas |
| 09 | Detalle de petición de funcionario | Bandeja → ícono de ojo | Vista estrictamente de solo lectura |

## Recorrido de prueba recomendado al grupo (3–5 minutos)

1. Entrar con **Andrea Demo** (perfil próximo a egresar).
2. Abrir **Mi expediente**.
3. Hacer clic en **Solicitar** para **Récord académico**. Confirmar la petición.
4. Revisar **Mis peticiones** y el detalle con fecha/hora de Ecuador.
5. Pulsar **Cambiar perfil** → pestaña **Funcionario** → **Entrar a la demostración**.
6. Verificar que la petición recién creada aparece en **Secretaría de Carrera** y abrirla.
7. Cambiar la dependencia a **Tesorería**: aparecerá una indicación de **403 / no asignada** (simulada, solo UI).
8. Cambiar a perfil **Diego Demo** para evaluar la vista de estudiante no habilitado.
9. Para empezar de cero, entrar a **Ayuda (?) → Restablecer datos ficticios**.

**Advertencia:** el perfil `funcionario_demo_a` de la demo original tenía asignaciones a Secretaría de Carrera y Prácticas. Este sitio refleja esa idea pero **no implementa autorización en backend**.

## Estructura

```text
SGT_SIAAF_Prototipo_Web/
├── index.html                 # Documento HTML de entrada
├── styles.css                 # Sistema de diseño responsive
├── app.js                     # Componentes/vistas y flujos de interacción
├── INICIAR_WINDOWS.bat        # Abre el prototipo
├── assets/
│   ├── mark.svg               # Marca conceptual, NO escudo oficial de la UNL
│   └── campus.svg             # Ilustración vectorial original
├── docs/
│   ├── DISENO-Y-ALCANCE.md
│   ├── INTEGRACION-DJANGO.md
│   └── OPINIONES-GRUPO.md
└── README.md
```

## Tecnologías y decisiones

- HTML semántico, CSS responsive y JavaScript sin frameworks ni dependencias externas.
- Nueve vistas reales renderizadas como componentes JavaScript; formularios, modal, tablas, navegación, filtros, cambios de perfil y estados vacíos.
- Identidad **SGT-SIAAF — Sistema de Gestión del Trámite de Titulación**. Inspirada visualmente en UNL; **no** es identidad institucional oficial autorizada.
- Datos ilustrativos de estudiante / funcionario. Los cambios se conservan temporalmente en **`sessionStorage` del navegador**, solo dentro de la pestaña y nunca en un servidor.
- Sin cookies de autenticación ni JWT.
- Incluye `assets/*.svg` como elementos visuales **codificados**. El ZIP no incluye pantallas PNG ni capturas como sustituto de HTML.

## Qué hay que cambiar cuando se implemente en el proyecto original

Consultar `docs/INTEGRACION-DJANGO.md`. La idea es conservar el diseño y reconstruir las vistas en React + TypeScript, consumiendo las API reales con autenticación JWT y validaciones del servidor. El proyecto original estaba todavía en la **feature 001** al definir estas maquetas; no supongas que la feature 002 de la copia demo ya está integrada.

## Comprobaciones realizadas

- Validación sintáctica: `node --check app.js`.
- Prueba de navegador automatizado de flujo completo: acceso → expediente → modal → petición → funcionario → detalle.
- Revisión de los perfiles estudiante de 7.º y 9.º ciclo.
- Revisión responsive en escritorio 1440 px y móvil 390 px.
- Sin errores de JavaScript durante esa prueba.

Las pruebas de esta maqueta **no sustituyen** las pruebas de seguridad, de Django o del navegador de quien la ejecute.
