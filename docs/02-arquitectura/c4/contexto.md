---
title: "C4 — Nivel 1: Contexto"
---

# C4 Nivel 1 — Diagrama de contexto

```mermaid
flowchart LR
    subgraph personas["Personas (8 roles)"]
        EST[Estudiante]
        SEC[Secretaría de Carrera]
        JUR[Secretaría-Abogacía<br/>y Analista de Apoyo]
        DEC[Decano]
        DIR[Director de Carrera]
        ADM[Administrador]
    end

    SGT(["Sistema SGT-SIAAF<br/>Gestión del trámite de titulación"])

    SGA[SGA/SIAAF institucional<br/>SIMULADO en Fase 1]
    FIRMA[FirmaEC<br/>SIMULADO en Fase 1]

    EST -->|HTTPS + JWT| SGT
    SEC -->|HTTPS + JWT| SGT
    JUR -->|HTTPS + JWT| SGT
    DEC -->|HTTPS + JWT| SGT
    DIR -->|HTTPS + JWT| SGT
    ADM -->|HTTPS + JWT<br/>+ Django Admin| SGT
    SGT -.consulta récord, mock.-> SGA
    SGT -.recibe PDF firmado, carga manual.-> FIRMA
```

## Elementos

| Tipo | Elemento | Descripción |
|---|---|---|
| Personas | Estudiante, Secretaría de Carrera, Secretaría-Abogacía (con Analista), Decano, Director de Carrera, Administrador | Los 8 roles del código; `RESPONSABLE_DEPENDENCIA` actúa como dependencia emisora dentro del sistema |
| Sistema | SGT-SIAAF | Backend Django + SPA React (ver contenedores) |
| Sistemas externos | SGA/SIAAF, FirmaEC | **Simulados**: adaptador mock de solo lectura y carga manual del PDF firmado (DEC-04). Representarlos como integraciones activas sería falso |

## Límite del sistema

Todo lo demás (almacenamiento privado de PDFs, auditoría, notificaciones in-app, OpenAPI) es interno del sistema.
