---
system: SGT-SIAAF
type: process
area: documentos
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Gestión documental

| Aspecto | Implementación verificada |
|---|---|
| Formato | Solo PDF; `core/adapters/pdf_validation.py` (tamaño ≤ 10 MB, magic bytes `%PDF-`, SHA-256) |
| Almacenamiento | Privado (`core/adapters/local_storage.py`; en desarrollo, `backend/src/media/private/`, ignorado por Git); nunca servido como estático |
| Versionado | `DocumentoEntregado.version` (N+1), `es_vigente`; se conserva el historial (RN-011) |
| Descarga | `GET /peticiones/{id}/documento/` (vigente) y `…/{version}/`; autenticada, con validación manual de ámbito; **sin** comprobar el hash al descargar (VULN-003) |
| Documentos generados | `resoluciones/adapters/pdf_generator.py`: informe "modelo Providencia #590" (borrador y definitivo) |
| Documentos cargados por autoridad | Memorando #162 firmado externamente (Decano/a) |
| Frontend | `features/expediente/DescargaButton.tsx`, `lib/download.ts` (descarga autenticada); `components/ui/FileUpload` |

**Seguridad:** los PDF de `backend/src/media/private/**` son datos de expedientes y **no se copian a la bóveda** ([[SOURCE_CATALOG]] §exclusiones).

## Relacionado

[[REQUESTS_AND_APPLICATIONS]] · [[ELECTRONIC_SIGNATURES]] · [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]]
