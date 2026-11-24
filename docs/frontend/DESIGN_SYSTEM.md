# Design System SGT-SIAAF

> Estado: integrado por bloques el 2026-11-22 (ver `docs/frontend/PLAN_DESIGN_SYSTEM_DK010.md`).
> Fuente única de tokens: `frontend/src/styles/tokens.css`. Estilos base: `frontend/src/styles/global.css`.
> Variante del administrador: `frontend/src/styles/siaaf-modern.css` (§11).
> Autorización: rediseño transversal autorizado expresamente por el responsable del repositorio el 2026-11-19
> (ver «Relación con CLAUDE.md» al final).

## 1. Principios

1. **Identidad institucional UNL**: azul marino `#13294b` y dorado `#c8a333` (login, landing, SAC), azul de interacción `#004c7b`.
2. **Tokens semánticos**: los componentes usan `--color-*`, `--text-*`, `--space-*`…; nunca colores ni tamaños literales.
3. **El estado no depende solo del color** (WCAG 1.4.1): todo estado lleva texto y, en badges/alertas/toasts, icono.
4. **Datos reales**: ningún componente inventa estados, cifras ni fechas. Un valor desconocido se muestra tal cual en tono neutral.
5. **Un `<main>` por pantalla** y jerarquía `h1 → h2 → h3` sin saltos.

## 2. Paleta

### Marca

| Token | Valor | Uso |
|---|---|---|
| `--color-brand` | `#13294b` | Sidebar, títulos (`--color-text-strong`) |
| `--color-brand-strong` | `#0e1f3a` | Degradado de la sidebar, texto sobre dorado |
| `--color-primary` | `#004c7b` | Interacción: botón primario, enlaces, foco, progreso |
| `--color-primary-hover` | `#003a5e` | Hover/activo |
| `--color-primary-subtle` / `-muted` | `#eef5fa` / `#dbe9f4` | Fondos de selección, iconos de KPI, anillo del paso actual |
| `--color-accent` | `#c8a333` | **Solo** sobre azul marino (barra activa, contadores, foco en la sidebar) |
| `--color-accent-text` | `#8a6a12` | Dorado sobre fondo claro (antetítulos) |

### Neutros

| Token | Valor | Uso |
|---|---|---|
| `--color-bg-main` | `#f2f5f8` | Fondo de página |
| `--color-surface` | `#ffffff` | Tarjetas, diálogos |
| `--color-surface-muted` / `-sunken` | `#f8fafc` / `#eef1f4` | Zonas internas, pistas de progreso |
| `--color-text-primary` | `#1f2937` | Texto |
| `--color-text-strong` | `#13294b` | Títulos |
| `--color-text-muted` | `#4b5563` | Descripciones |
| `--color-text-secondary` | `#646d7c` | Metadatos, etiquetas |
| `--color-divider` | `#e5e7eb` | Divisores **decorativos** |
| `--color-border-control` | `#8a94a3` | Bordes de campos y botones secundarios (WCAG 1.4.11) |

### Estados semánticos (fondo / texto / acento sólido)

| Tono | Fondo | Texto | Sólido | Significado en todo el sistema |
|---|---|---|---|---|
| `success` | `#d1fae5` | `#065f46` | `#15803d` | Concluido o validado |
| `info` | `#dbeafe` | `#1e40af` | `#004c7b` | En curso / en manos de la institución |
| `warning` | `#fde68a` | `#92400e` | `#b45309` | Requiere corrección o atención |
| `danger` | `#fee2e2` | `#991b1b` | `#b91c1c` | Cancelado, vencido, error, acción destructiva |
| `neutral` | `#e5e7eb` | `#4b5563` | `#646d7c` | Sin iniciar / pendiente de gestión |

Correspondencia de estados reales (fuente única `frontend/src/lib/estados.ts`):

| Dominio | Valor del backend | Etiqueta | Tono |
|---|---|---|---|
| Expediente | `BORRADOR` · `ENVIADA` · `EN_VERIFICACION` · `OBSERVADA` · `INFORME_EMITIDO` · `DECLARADA_APTA` · `CANCELADA` | Borrador · Enviada · En verificación · Observada · Informe emitido · Declarada apta · Cancelada | neutral · info · info · warning · info · success · danger |
| Petición | `PENDIENTE` · `SOLICITADO` · `CARGADO` · `LEGALIZADO` · `VERIFICADO` · `OBSERVADO` | Pendiente · Solicitado · Cargado · Legalizado · Verificado · Observado | neutral · info · success · success · success · warning |
| Checklist | `PENDIENTE` · `VERIFICADO` · `OBSERVADO` | Pendiente · Verificado · Observado | neutral · success · warning |

El portal del estudiante conserva su lenguaje claro («En preparación», «Con observaciones») con el **mismo tono** (`StatusBadge label=…`).

### Contraste verificado (WCAG 2.2 AA, recalculado el 2026-11-19)

| Par | Colores | Contraste | Requisito | Resultado |
|---|---|---|---|---|
| Texto principal / superficie | `#1f2937` / `#ffffff` | 14,68:1 | 4,5 | Cumple |
| Texto principal / fondo | `#1f2937` / `#f2f5f8` | 13,42:1 | 4,5 | Cumple |
| Título navy / fondo | `#13294b` / `#f2f5f8` | 13,27:1 | 4,5 | Cumple |
| Texto secundario / superficie | `#646d7c` / `#ffffff` | 5,22:1 | 4,5 | Cumple |
| Texto secundario / fondo | `#646d7c` / `#f2f5f8` | 4,77:1 | 4,5 | Cumple |
| Texto secundario / zona hundida | `#646d7c` / `#eef1f4` | 4,61:1 | 4,5 | Cumple |
| Texto atenuado / superficie | `#4b5563` / `#ffffff` | 7,56:1 | 4,5 | Cumple |
| Enlace y botón primario | `#004c7b` / `#ffffff` | 9,05:1 | 4,5 | Cumple |
| Botón primario hover | `#ffffff` / `#003a5e` | 11,89:1 | 4,5 | Cumple |
| Botón de peligro | `#ffffff` / `#b91c1c` | 6,47:1 | 4,5 | Cumple |
| Texto de la sidebar | `#ffffff` / `#13294b` | 14,52:1 | 4,5 | Cumple |
| Dorado sobre navy (acento/foco) | `#c8a333` / `#13294b` | 6,04:1 | 3,0 | Cumple |
| Dorado oscuro sobre superficie | `#8a6a12` / `#ffffff` | 5,06:1 | 4,5 | Cumple |
| Dorado oscuro sobre fondo | `#8a6a12` / `#f2f5f8` | 4,62:1 | 4,5 | Cumple |
| Borde de control | `#8a94a3` / `#ffffff` | 3,07:1 | 3,0 | Cumple |
| Badge neutral / info / advertencia / éxito / peligro | ver tabla de estados | 6,10 / 7,15 / 5,69 / 6,78 / 6,80 | 4,5 | Cumplen |
| Alertas (texto sobre fondo suave) | info / advertencia / éxito / peligro | 7,92 / 6,84 / 7,29 / 7,60 | 4,5 | Cumplen |
| Acentos sólidos (barras, no texto) | ámbar / éxito | 5,02 / 5,02 | 3,0 | Cumplen |

Prohibido: dorado `#c8a333` como texto sobre fondo claro (2,40:1); `#e5e7eb` como borde de un control (1,24:1).

Corrección registrada: el gris secundario pasó de `#6b7280` a `#646d7c` porque daba 4,42:1 sobre el nuevo fondo `#f2f5f8`.

## 3. Tipografía

- Familia: **Inter** (SIL Open Font License 1.1), autoalojada en `frontend/public/assets/fonts/inter/` con su licencia (`OFL.txt`).
  - Origen: paquete npm `@fontsource/inter@5.3.0`, descargado con `npm pack`. Se verificó el `shasum` contra el registro (`866278dc2357659f8be1755c8b67f29d3697b440`).
  - No se añadió como dependencia del proyecto. Sin recursos externos en tiempo de ejecución.
- Subconjuntos `latin` y `latin-ext`, pesos 400, 500, 600 y 700 (`font-display: swap`). Precarga de 400 y 600 en `index.html`.

| Token | Tamaño | Uso |
|---|---|---|
| `--text-xs` | 12 px | Etiquetas, badges, metadatos |
| `--text-sm` | 14 px | Texto base de la aplicación |
| `--text-md` | 16 px | Títulos de tarjeta (h3), subtítulos, campos en móvil |
| `--text-lg` | 20 px | Títulos de sección (h2), diálogos |
| `--text-xl` | 24 px | h1 en móvil |
| `--text-2xl` | 30 px | h1 y cifras KPI |

Excepciones documentadas: el título de la landing (2,125 rem, tamaño de exhibición) y el contador del punto de notificación (11 px).

## 4. Espaciado, radios, sombras y capas

- Espaciado (4 px): `--space-1` 4 · `-2` 8 · `-3` 12 · `-4` 16 · `-5` 20 · `-6` 24 · `-8` 32 · `-10` 40 · `-12` 48 · `-16` 64.
- Radios: `--radius-sm` 4 · `-md` 8 (controles) · `-lg` 12 (tarjetas, badges) · `-xl` 16 (diálogos) · `-full`.
- Elevación: `--elevation-card` (tarjetas) · `--elevation-raised` (hover, toasts) · `--elevation-overlay` (diálogos, panel móvil).
- Capas: `--z-sticky` 10 · `--z-drawer` 30 · `--z-modal` 40 · `--z-toast` 50.

## 5. Interacción

- Duraciones: `--duration-fast` 150 ms (hover), `--duration-base` 200 ms (paneles), `--duration-slow` 250 ms (entradas).
- Curvas: `--ease-standard`, `--ease-out`.
- Foco: contorno de 2 px `--color-primary` (en la sidebar, dorado). Los campos usan además `--focus-ring`.
- Estados:
  - hover: fondo sutil o borde primario;
  - active: desplazamiento de 1 px;
  - disabled: `--opacity-disabled` y `cursor: not-allowed`;
  - loading: `aria-busy` y spinner (el botón queda deshabilitado, sin dobles envíos).
- Animaciones (`sgt-fade-in`, `sgt-shimmer`): solo opacidad y 4 px. `prefers-reduced-motion: reduce` las anula (`global.css`).
- Controles: alto 40 px (escritorio) y **44 px en pantallas táctiles** (`@media (pointer: coarse)`).

## 6. Breakpoints y patrones responsive

| Ancho | Comportamiento |
|---|---|
| > 1280 | KPI en 4 columnas, contenido a dos columnas (3 fr / 2 fr) |
| ≤ 1280 | KPI en 2 columnas |
| ≤ 1024 | Sidebar como panel lateral (botón «Abrir menú», Escape y fondo para cerrar); contenido a una columna; DataList con datos en segunda línea |
| ≤ 768 | Campos a 16 px (evita el zoom de iOS); h1 a 24 px; línea de tiempo horizontal → vertical |
| ≤ 640 | DataList en tarjetas verticales; datos secundarios ocultos; acciones a todo el ancho |
| ≤ 480 | KPI a 1 columna; diálogos como hoja inferior; nombre del perfil solo para lectores de pantalla |

Validado sin scroll horizontal en 320, 360, 390, 768, 1024, 1280, 1440 y 1920 px (ver el informe de la sesión).

## 7. Componentes (`frontend/src/components/ui`)

| Componente | Uso | Notas de accesibilidad |
|---|---|---|
| `Button` | `primary` (una por zona), `secondary`, `ghost`, `danger` (solo destructivas) | `aria-busy` en carga |
| `Input`, `Select`, `Textarea` | Campos con etiqueta, pista y error | `aria-invalid`, `aria-describedby`, asterisco visual + `required` |
| `Card` | Sección con título (`headingLevel` 2/3), icono, descripción y acciones | `id` → `aria-labelledby` y foco al navegar por ancla |
| `KpiCard` + `KpiGrid` | Indicadores clave | La rejilla aporta un `h2` oculto; el tono se acompaña de texto |
| `StatusBadge` / `Badge icon` | Estados reales | Etiqueta + icono + color |
| `DataList` | Sustituye a las tablas rígidas | `<ul>` con `<dl>` por elemento; filas → tarjetas sin desbordar |
| `ConfirmDialog` / `useConfirm()` | Confirmaciones (sustituye a `window.confirm`) | `alertdialog`, foco inicial en «Cancelar», Escape cancela, resuelve una sola vez |
| `Modal` | Diálogos de formulario | Trampa de foco, retorno del foco, `aria-describedby`, hoja inferior en móvil |
| `Breadcrumbs` | Rutas profundas | `nav` + `aria-current="page"` |
| `Skeleton` | Carga con la forma del contenido | `role=status`, `aria-busy` |
| `EmptyState`, `ErrorState` (reintento real), `ForbiddenState`, `NotFoundState` | Estados de interfaz | Icono + título + explicación + acción |
| `Alert`, `ToastProvider` | Mensajes | `role=alert` en advertencia y peligro |
| `ProgressBar` | Progreso real | `role=progressbar` + `aria-valuetext` |
| `BarChart` | Barras horizontales sin librería | `figure` etiquetada; los valores en texto son la alternativa accesible |
| `Timeline` | Etapas (vertical u horizontal) | Estado de cada paso en texto para lectores de pantalla |
| `Checkbox`, `FileUpload` | Selección y carga de archivos | Etiqueta asociada y error descrito |
| `Pagination` | Paginación real del backend | Botones con nombre accesible y estado deshabilitado |
| `Spinner` | Carga breve dentro de un control | Acompañado de texto o `aria-busy` |
| `Table` | Tablas de datos que no usan `DataList` | Encabezados semánticos |
| `icons.tsx` | Juego único de iconos (trazo 1,8, rejilla 24) | Siempre `aria-hidden`; el texto da el significado |
| `HeroPanel` | Encabezado institucional de los paneles (degradado, chips de datos reales, contenido lateral) | Región nombrada por su título (`h1`/`h2`) |
| `ActionCard` | Tarjeta flotante «qué hacer ahora» con CTA real | La tarjeta no es clicable; el CTA es un enlace o botón normal |
| `UrgencyIndicator` | Punto + contador + texto para urgencias verificables | Solo con cantidad > 0; texto y forma además del color; pulso limitado y desactivado con `prefers-reduced-motion` |

Estructura (`frontend/src/components/layout`):
- `AppShell` es el único shell: sidebar institucional (contraíble en escritorio, con la preferencia guardada en `localStorage`), barra superior con notificaciones y perfil, y un único `<main>`. Admite `group` en cada enlace, `visual` para una variante con alcance propio y `topbarSlot` para un control adicional.
- `StudentLayout` y `AppLayout` solo lo configuran con la navegación autorizada de cada rol.

### Ejemplos

```tsx
const { confirm, dialog } = useConfirm()
async function enviar() {
  if (!(await confirm({ title: '¿Enviar el expediente?', confirmLabel: 'Enviar expediente' }))) return
  await mutation.mutateAsync()
}
return <>{dialog}<Button onClick={() => void enviar()}>Enviar expediente</Button></>
```

```tsx
<DataList
  label="Expedientes de la bandeja"
  items={filas}
  getKey={(f) => f.id}
  renderTitle={(f) => f.numero_expediente}
  renderStatus={(f) => <StatusBadge dominio="expediente" valor={f.estado} />}
  fields={[{ key: 'limite', label: 'Fecha límite', render: (f) => formatFecha(f.fecha_limite_atencion) }]}
  renderActions={(f) => <Link to={`/bandeja/${f.id}`}>Abrir</Link>}
/>
```

## 8. Reglas de accesibilidad (obligatorias en código nuevo)

1. Un `<main>` por pantalla (lo aporta `AppShell`; las páginas usan `<div>`).
2. Jerarquía h1 → h2 → h3 (`Card headingLevel`, `KpiGrid` con h2 oculto).
3. Nada de `window.confirm`: usar `useConfirm`.
4. Iconos decorativos con `aria-hidden`; nunca caracteres Unicode como icono.
5. Objetivos táctiles de al menos 44 px en `pointer: coarse`; nunca acciones solo visibles con hover.
6. Pruebas con `vitest-axe` en cada pantalla nueva.

## 9. Pendientes que dependen de terceros (no se simularon)

- **Búsqueda universal**: el backend no ofrece búsqueda ni filtros en la bandeja (BE-09). Requiere un endpoint de búsqueda con alcance por rol. Hoy existen el filtro de la página actual y, solo para el administrador, Ctrl/Cmd + K sobre secciones reales y hasta 50 expedientes de la bandeja.
- **Estadísticas completas**: con más de 50 expedientes en la bandeja, el panel solo muestra el total. Los vencidos y la distribución por estado requieren un endpoint de agregados.
- **Gráficos temporales (tendencias)**: no hay series históricas expuestas por la API.
- **Perfil de funcionarios**: sin endpoint de perfil, solo se muestran la cédula y los roles del token.
- **Responsable de dependencia**: sin celdas RBAC ni ruta de inicio (brecha conocida). Solo ve el estado de su acceso.
- **Exportación**: no existe una operación de exportación autorizada. No se muestra.

## 10. Relación con CLAUDE.md

Cláusulas afectadas y autorización:
- Máxima 3 («tokens de `especificaciones/01`»): los tokens globales cambian de valores.
- Restricción de «no rediseñar otros roles» de tareas previas.
- Máxima 4 («sin dependencias nuevas»): la fuente se incorporó como archivos estáticos, no como dependencia npm.

El responsable autorizó expresamente el rediseño transversal el 2026-11-19, solo para presentación, componentes y navegación. Esa autorización no cubre cambios de reglas de negocio, RBAC, MFA, IDOR ni contratos de API. Los cambios de backend de perfil académico, `mi-tramite` y notificaciones tienen autorizaciones propias del 2026-11-22 y constan en sus bitácoras.

## 11. Variante «SIAAF Modern» (administrador)

- **Alcance:** `AppLayout` aplica `data-visual="siaaf-modern"` solo si el JWT incluye `ADMINISTRADOR`. Los demás roles conservan los tokens base.
- **Tokens:** `siaaf-modern.css` redefine tokens semánticos dentro de ese atributo. Estructura `#25374a`, acción y enlaces `#3d5871` (7,41:1 sobre blanco), fondo `#f4f7fa`, acento `#e1ab1d` y estados verde, ámbar y rojo con texto o icono.
- **Contraste:** `#6597c9` (3,08:1 con blanco) no se usa para texto ni botones con texto blanco.
- **Fuente de la paleta:** `docs/paleta_colores_institucionales/` versiona las tres tablas de color (`palette-tints.png`, `palette-shades.png` y `palette-shades-login.png`). Los valores aplicados quedan en `siaaf-modern.css`.
- **Navegación:** grupos «Menú principal» y «Gestión y control». La consola de administración enlaza a Django admin y exige una cuenta con `is_staff`.
- **Búsqueda:** Ctrl/Cmd + K localiza secciones y expedientes de la bandeja; no usa endpoints nuevos.
- **Panel (`/bandeja`):** indicadores, distribución por estado, atención prioritaria, actividad de la cuenta, accesos rápidos y listado. Con más de 50 expedientes no se muestran cifras parciales de plazos ni la distribución.
- **Responsive:** KPI en 4, 2 y 2 columnas (escritorio, tablet y móvil); el sidebar pasa a panel lateral en ≤ 1024 px.

## 12. Capa Liquid Glass (rediseño de paneles por rol, 2026-11-24)

Referencia visual: `prototipos/vistas_liquid_glass/` (Google Stitch). Se tomó la composición (sidebar flotante, barra superior de vidrio, hero con tarjeta de acción, KPI y hoja de ruta), no su HTML, CSS, JavaScript ni sus datos. Reparto y commits: `docs/frontend/PLAN_LIQUID_GLASS_DK010.md`.

- **Proporción orientativa:** superficies sólidas como base (~65 %), vidrio (~15 %), identidad institucional (~15 %) y movimiento (~5 %).
- **Dónde va el vidrio:** sidebar, barra superior, chips del hero, `ActionCard` y KPI destacados (`KpiCard variant="glass"`). **Nunca** en tablas, formularios, documentos, listados densos ni textos largos.
- **Tokens (`tokens.css`, sección «Capa Liquid Glass»):** `--gradient-brand` (azul marino `#13294b` → `#123d72` → `#2463a6`; blanco sobre `#2463a6` = 6,1:1), `--app-backdrop`, `--glass-blur-*`, `--glass-surface*`, `--glass-border*`, `--glass-highlight` y `--glass-shadow*`. La marca oficial (azul marino, azul de interacción `#004c7b` y dorado) no cambia.
- **Utilidades (`styles/glass.css`):** `glass-surface`, `glass-panel`, `glass-floating`, `glass-on-brand` y `glass-interactive` (elevación de 2 px, 150–250 ms). Un módulo CSS que fije su propio fondo debe repetir el fondo de vidrio (ver `KpiCard.module.css`), porque los módulos se cargan después de la capa global.
- **Shell:** `AppShell glass` → `data-glass="on"`. Es independiente de `visual` (paleta): el administrador combina «siaaf-modern» con el vidrio.
- **Urgencia:** solo con datos verificables. Estudiante: observaciones pendientes (`mi-tramite`). Funcionarios y administrador: expedientes con plazo vencido calculados con la bandeja completa. «Vence hoy» y los pendientes sin urgencia usan el nivel `attention` (anillo estático). Un solo pulso por pantalla; cuatro repeticiones y queda fijo.
- **Accesibilidad y rendimiento:** respaldo opaco sin `backdrop-filter` o con `prefers-reduced-transparency`; sin desplazamientos ni pulsos con `prefers-reduced-motion`; bordes reales con `forced-colors`; desenfoque solo en capas pequeñas o fijas.
- **Fuera de alcance (sin datos reales):** los paneles «Docente» y «Tutor» de los prototipos (el sistema no tiene esos roles), indicadores de usuarios, sesiones, auditoría o integridad del prototipo de administración, y tendencias o series temporales.

