# Sistema de páginas de error (SGT-SIAAF, Liquid Glass)

> Implementado el 2026-11-24 en `feat/siaaf-error-pages-liquid-glass` (bloques ER-A…ER-E, ver `PLAN_ERRORES_DK010.md`).
> Referencia visual: `prototipos/vistas-errores-unl/` (Google Stitch). Se tomó la composición, los textos y la mascota. No se copiaron su HTML ni su CSS, ni sus datos inventados: nodos, IDs de incidencia, «15 minutos», TLS o latencias.

## 1. Arquitectura

Las ocho vistas son **configuraciones de un único componente**. No hay ocho páginas ni ocho hojas de estilo.

| Pieza | Archivo | Responsabilidad |
|---|---|---|
| Catálogo | `components/errors/errorCatalog.ts` | Textos aprobados, código HTTP real, etiquetas de acciones y mascota de cada variante |
| Clasificador | `components/errors/classifyError.ts` | `ApiRequestError` → variante; `backendDetail` extrae el `detail` textual del backend |
| Vista | `components/errors/ErrorView.tsx` + `.module.css` | Estructura, semántica, acciones y estilo Liquid Glass (`page` o `inline`) |
| Página | `components/errors/ErrorPage.tsx` + `.module.css` | Cabecera institucional, panel `glass-floating` y pie. No usa el router |
| Error de consulta | `components/errors/QueryErrorView.tsx` | Error de la consulta principal de una vista, dentro de su layout |
| Recuperación | `useControlledRetry.ts`, `useOnlineStatus.ts` | Reintento manual con espera progresiva; estado de red del navegador |
| Rutas | `app/NotFoundPage.tsx`, `app/SessionExpiredPage.tsx`, `auth/sessionExpiry.ts` | 404 real, vista 401 y marca de sesión expirada |
| Límite global | `components/feedback/ErrorBoundary.tsx` | Excepciones de renderizado → página 500 |

## 2. Clasificación (`classifyError`)

La fuente es el cliente HTTP real (`api/client.ts`): estado HTTP, `isTimeout` (AbortController, 30 s) e `isNetworkError`.

| Condición | Variante | Dónde se muestra |
|---|---|---|
| 401 | `unauthorized` | Manejador global → `/sesion-expirada` (página) |
| 403 | `forbidden` | En la vista (`QueryErrorView`); la ruta sin rol sigue en V-09 (`/no-habilitado`) |
| 404 de ruta | `not-found` | Página (`path="*"`) |
| 404 de un recurso | `not-found` | En la vista, con título de contexto («Expediente no encontrado») |
| `isTimeout`, 408, 504 | `timeout` | En la vista |
| Error de red y `navigator.onLine === false` | `offline` | En la vista |
| Error de red con red en el dispositivo, 502, 503 | `unavailable` | En la vista |
| 500 y demás 5xx | `server` | En la vista; el ErrorBoundary también usa esta vista |
| Resto (4xx de datos, respuestas inesperadas, errores ajenos a la API) | `data` | En la vista |

`navigator.onLine` solo decide entre «sin conexión» y «servicio no disponible». **Nunca** se presenta como conexión restablecida: eso solo lo confirma una petición real.

## 3. Comportamiento por variante

- **404:** la ruta comodín muestra la página y no redirige.
  - «Ir al inicio»: lleva al panel del rol o, sin sesión, a la página pública.
  - «Intentar nuevamente»: recarga la misma dirección.
  - No revela si un recurso pertenece a otra cuenta.
- **401 (DEC-17):**
  - Ante cualquier 401 de la API, el manejador global marca la sesión como expirada y la cierra. Después, `RequireAuth` lleva a `/sesion-expirada` conservando la ruta (`returnTo`).
  - «Iniciar sesión» abre el login real; «Ir al inicio» lleva a `/`.
  - **Sin bucles:**
    - La vista es pública y no hace peticiones.
    - Varios 401 seguidos solo repiten operaciones idempotentes.
    - El retorno solo acepta rutas internas: nunca `//…`, `/login` ni la propia vista.
  - La marca se limpia al montar y al desmontar la vista, y al volver a autenticarse.
  - Sin 401 previo (salida manual, enlace sin sesión), las rutas protegidas siguen yendo a `/login`.
- **403:**
  - No cierra la sesión ni se trata como 401.
  - «Volver a mi panel» usa `getHomeRouteForRoles`; «Ir al inicio» lleva a `/`.
  - Incluye el enlace «Más información sobre tu acceso» a V-09.
  - No muestra la regla del backend.
- **500:** reintento manual de la consulta. Se muestra el `detail` textual del backend si existe, porque varias reglas de negocio responden 500 (INC-21). Nunca se muestran trazas. No hay identificador de incidencia: el backend no expone uno seguro.
- **503:** reintento manual con espera creciente de 5, 10, 20 y 40 s, hasta un máximo de 60 s, y cuenta atrás visible. No hay reintentos automáticos ni estados de mantenimiento inventados.
- **Sin conexión:** informa lo que dice el dispositivo. «Reintentar conexión» vuelve a consultar.
- **Timeout:** distinto de 500, 503 y sin conexión. Una cancelación que no viene del temporizador del cliente se clasifica como error de red, no como timeout (`api/client.ts`).
- **Error de datos:** «Volver a cargar» repite solo esa consulta, sin recargar la aplicación. No reemplaza 401, 403 ni 404.
- **ErrorBoundary:**
  - Captura solo excepciones de renderizado de React y muestra la página 500.
  - «Intentar nuevamente» reinicia el límite; «Ir al inicio» es un enlace de documento, porque el límite está fuera del router.
  - Registra con `logger.error`.
  - No muestra el mensaje ni la pila.

**Reintentos:** `useControlledRetry` solo actúa a petición del usuario e ignora pulsaciones mientras hay un intento en curso. Se usa únicamente para lecturas (`refetch`): las escrituras (POST/PATCH) mantienen su manejo local y nunca se repiten desde estas vistas.

**Alcance de la integración:** la consulta principal de `StudentDashboardPage`, `ExpedientePage`, `PeticionesPage`, `SeguimientoPeticionPage` y `DetalleFuncionarioPage`. Los errores de tarjetas, listados secundarios, formularios y diálogos conservan su contexto local (`ErrorState`, `InlineAlert`), como pide la spec 08.

## 4. Diseño, mascota y animación

- **Tokens y utilidades:** los del rediseño Liquid Glass (`tokens.css`, `glass.css`). No hay estilos paralelos.
- **Página:**
  - Cabecera con el degradado institucional y el logotipo oficial ya versionado (`public/assets/auth/logo-unl.png`).
  - Panel de vidrio y pie institucional.
- **Mascota:** los cinco PNG autorizados en DEC-15. Los prototipos de Stitch usan exactamente esas cinco imágenes con este reparto:

  | Variantes | PNG |
  |---|---|
  | 404 y datos | `mascota-404` |
  | 500 y sin conexión | `mascota-500` |
  | 503 y tiempo agotado | `mascota-503` |
  | 401 | `mascota-401` |
  | 403 | `mascota-403` |

  - Es decorativa (`alt=""`) y no lleva ningún texto que la etiquete.
  - Sus fondos opacos se funden con `mix-blend-mode: multiply` y una máscara radial, sin modificar los archivos.
  - El resto de texto del borde del PNG del 404 se recorta con `clip-path`.
- **Animación:**
  - Entrada del panel y del contenido escalonada, de 250 ms como máximo.
  - Balanceo breve de la mascota: dos ciclos, luego queda quieta.
  - Hover y pressed en los botones.
  - Con `prefers-reduced-motion` se desactiva todo.
- **Respaldos:** superficie opaca sin `backdrop-filter` o con `prefers-reduced-transparency`; bordes reales con `forced-colors`.
- **Responsive:**
  - Dos columnas en escritorio; una columna centrada en ≤ 768 px.
  - Acciones a ancho completo en ≤ 480 px.
  - Comprobado a 1440, 1280, 820 y 390 px.

## 5. Accesibilidad

- **Encabezados y foco:**
  - Página: `h1` que recibe el foco al montarse, para que se anuncie el cambio.
  - En línea: `h2` dentro de una región viva (`alert`; `status` para 403).
- **Teclado:** orden del título a la acción primaria, luego la secundaria. Foco visible con los anillos del sistema.
- **Estado:** el estado vivo (espera, conexión) está en `aria-live="polite"`.
- **Contraste:** chip de categoría #8a6a12 sobre su fondo, ≈ 4,7:1; texto blanco sobre el degradado ≥ 6,1:1.
- **Comprobación:** axe sin violaciones en `ErrorView`, `ErrorPage`, `NotFoundPage` y `SessionExpiredPage`.

## 6. Pruebas

| Archivo | Pruebas | Qué cubre |
|---|---:|---|
| `components/errors/ErrorView.test.tsx` | 19 | Clasificación, ocho variantes, foco, roles vivos, acciones, detalle y axe |
| `components/errors/ErrorPage.test.tsx` | 3 | Estructura, logotipo y axe |
| `components/errors/recovery.test.tsx` | 9 | Espera progresiva, sin dobles intentos ni reintentos automáticos, listeners, timeout, sin conexión, 503, datos y 401 |
| `app/NotFoundPage.test.tsx` | 7 | 404 real: textos, foco, «Ir al inicio» con y sin sesión, recarga, teclado y axe |
| `app/SessionExpiredPage.test.tsx` | 6 | Vista 401, login real con retorno, retorno externo descartado, marca limpia al salir |
| `components/feedback/ErrorBoundary.test.tsx` | 3 | Página 500 sin detalles técnicos, registro, reinicio y recuperación |
| `app/router.auth-expiry*.test.tsx` | — | 401 → vista 401 → login; varios 401 sin bucle; 401 durante la carga lazy |
| `app/router.errores.test.tsx` | 5 | 403 sin cierre de sesión, 404 de recurso en su layout, 500 sin recarga, ruta protegida sin 401 → login, vista 401 pública |

## 7. Limitaciones

- **No reproducidos en la aplicación real** (Docker, `:8000`): 403, 500, 503, timeout, sin conexión y error de datos. Requieren sesión con MFA o fallos del backend que no se provocaron, y no se configura MFA en cuentas demo. Están cubiertos por las pruebas automáticas y se revisaron visualmente con un arnés local no versionado.
- **Sí verificados en la aplicación real:** la 404 y la 401 (`/sesion-expirada`), que son públicas.
- **Peso de `mascota-404.png`:** 650 KB, frente a ~100 KB de las demás. En conexiones lentas el halo aparece antes que la mascota. Optimizarlo (WebP o reescalado) requiere decidir sobre el recurso autorizado (DEC-15).
- **Identificador de incidencia:** sin identificador seguro en el backend, no se muestra ninguno.
