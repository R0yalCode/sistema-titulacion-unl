# Inventario de assets — Mascotas (FE-T1214)

Ilustraciones gráficas complementarias de la identidad visual de SGT-SIAAF, integradas en el frontend con autorización expresa del usuario del proyecto (2026-11-05). **No son archivos de marca oficial de la Universidad Nacional de Loja**: son ilustraciones generadas a partir de referencias aportadas, según la advertencia conservada en el `README.md` del prototipo de origen. No se usan como logotipo institucional.

## Procedencia

- **Origen:** `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/assets/img/` (prototipo B, referencia visual no normativa — DEC-11).
- **Copia:** idéntica byte a byte al original (verificada con `sha256sum`); sin recompresión ni edición.
- **Autorización de uso:** explícita del usuario, 2026-11-05 (ver `README.md` actualizado del prototipo B, sección "Autorización de uso en SGT-SIAAF").

## Inventario

| Archivo | Ubicación en frontend | Dimensiones | Peso | Estado | Uso | Decorativa/informativa |
|---|---|---|---|---|---|---|
| `mascota-401.png` | `public/assets/mascotas/mascota-401.png` | 246×242 | 96.9 KB | Copiado, **no integrado visualmente** | Ninguno: 401 no es página independiente (DEC-13, ERR-01) | — |
| `mascota-403.png` | `public/assets/mascotas/mascota-403.png` | 237×248 | 95.6 KB | Integrado | `NoHabilitadoPage` (destino de guardas de rol, V-09) | Decorativa (`alt=""`) |
| `mascota-404.png` | `public/assets/mascotas/mascota-404.png` | 693×664 | 634.3 KB | Integrado | `NotFoundPage` (FE-T1211) | Decorativa (`alt=""`) |
| `mascota-500.png` | `public/assets/mascotas/mascota-500.png` | 240×271 | 105.0 KB | Copiado, **no integrado visualmente todavía** | Reservado para cuando exista una vista real que presente `ErrorState` de forma prominente (fuera de alcance F2.5: "no crear páginas independientes para 500") | — |
| `mascota-503.png` | `public/assets/mascotas/mascota-503.png` | 227×277 | 104.6 KB | Copiado, **no integrado visualmente todavía** | Igual que 500 | — |

## Por qué 500/503 no se integraron visualmente en este lote

`ErrorState` es un componente genérico y reutilizable (usado también en contextos pequeños, p. ej. un panel de reintento dentro de una sección). FE-T1212 prohíbe explícitamente crear páginas independientes para 500/503. Forzar la mascota dentro de `ErrorState` la mostraría en todos sus usos, incluidos los inline/pequeños, lo cual no es apropiado. Los archivos ya están disponibles y documentados; su integración visual corresponde a cuando una vista real (F3+) presente un error 500/503 de forma prominente a nivel de página.

## Accesibilidad

- Ambas mascotas integradas (`403`, `404`) son **decorativas**: `alt=""`, el contenido informativo lo aportan `ForbiddenState`/`NotFoundState` en texto.
- No transmiten información exclusivamente por ilustración o color.
- No se removió el flujo de teclado ni se afectó el contraste del texto.

## Optimización

No se aplicó compresión destructiva (instrucción expresa de la autorización). `mascota-404.png` es sensiblemente más pesada (634 KB) que el resto; se conserva así por ser el archivo original. Si el peso afecta el rendimiento percibido en una auditoría posterior (FE-T1006), la decisión de recomprimir requiere autorización separada, ya que podría alterar la identidad gráfica.

## Restricciones respetadas

- No se usa el logo «unl» recreado conceptualmente.
- No se afirma licencia, derecho de autor o autorización institucional formal no documentada.
- No se sustituyó `Spinner` por ninguna mascota (loading).
- No se usó ninguna imagen genérica como reemplazo.
