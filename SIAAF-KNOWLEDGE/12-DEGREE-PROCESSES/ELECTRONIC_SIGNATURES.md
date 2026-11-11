---
system: SGT-SIAAF
type: process
area: firmas
status: verified
source: verified-code + specify-001
last_verified: 2026-11-11
---

# Firmas electrónicas y autógrafas

| Documento | Tipo de firma | En el sistema |
|---|---|---|
| Memorando #162 (declaratoria) | Electrónica **externa** (FirmaEC) | Se carga un PDF ya firmado; **no se verifica** la firma (DEC-04 de la spec 001; VULN-010) |
| Informe #590 (Providencia) | Firmas del Secretario/a-Abogado/a y del Analista (plantilla) | El sistema genera un PDF modelo; sin firma digital |
| Acta de sustentación (Fase 2) | **Autógrafa física obligatoria** (RN-006) | No implementado; el sistema solo registraría notas |

Integración futura y propuesta técnica: [[FIRMA_EC]].
