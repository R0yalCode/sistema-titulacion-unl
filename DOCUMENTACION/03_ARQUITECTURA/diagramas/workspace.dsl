workspace "SGT-SIAAF" "Sistema de Gestión del Trámite de Titulación — Backend Fase 1 (Declaratoria de Aptitud Legal)" {

    !identifiers hierarchical

    model {

        estudiante      = person "Estudiante" "Inicia el expediente, solicita certificados internos, adjunta PDF y subsana observaciones." "Rol"
        secretariaCarrera = person "Secretaría de Carrera" "Atiende peticiones de récord académico y certificados de carrera." "Rol"
        secretarioAbogado = person "Secretario/a-Abogado/a" "Evalúa el checklist, registra observaciones y emite el informe legal." "Rol"
        analistaApoyo   = person "Analista de Apoyo" "Prepara borradores de checklist/informe (sin autoridad de emisión)." "Rol"
        decano          = person "Decano/a" "Registra la declaratoria de aptitud con el memorando firmado." "Rol"
        directorCarrera = person "Director/a de Carrera" "Legaliza el certificado de prácticas; supervisa su carrera." "Rol"
        responsableDependencia = person "Responsable de Dependencia" "Representa unidades emisoras (Tesorería, Idiomas, Prácticas)." "Rol"
        administrador   = person "Administrador" "Administra usuarios, roles RBAC y el catálogo de requisitos." "Rol"

        sga = softwareSystem "SGA/SIAAF institucional (simulado)" "Fuente del récord académico. Adaptador mock de solo lectura (core/adapters/mock_sga.py); NO existe conexión real ni separación entre SGA y SIAAF en el código (una sola interfaz ISGALegacyPort)." "Externo, simulado"
        firmaec = softwareSystem "FirmaEC / FirmaGob (externo)" "Software de firma electrónica estatal, usado fuera del sistema por el Decano/a; el memorando ingresa como PDF ya firmado (DEC-04)." "Externo, no integrado"

        sgtsiaaf = softwareSystem "SGT-SIAAF" "Plataforma de gestión del trámite de Declaratoria de Aptitud Legal (Art. 235 RRA-UNL)." {

            webClient = container "Cliente Web (SPA React)" "Interfaz de usuario: login, dashboard, solicitud, expediente, bandeja." "React + TypeScript + Vite" "Cliente"
            nginx     = container "Nginx" "Proxy inverso y servidor de archivos estáticos." "Nginx 1.24"
            django    = container "Backend Django REST Framework" "Monolito modular con arquitectura hexagonal; expone /api/v1/." "Python 3.12 / Django 5.2 / DRF" {

                authApp     = component "authentication" "Usuarios, JWT (SimpleJWT), matriz RBAC de mundo cerrado (RBAC_MATRIX)." "Django app"
                expedApp    = component "expedientes" "Expediente global, máquina de estados, cómputo de plazo de 8 días hábiles." "Django app"
                peticApp    = component "peticiones" "Peticiones documentales, ingestión y versionado de PDF." "Django app"
                verifApp    = component "verificacion" "Checklist digital, observaciones accionables, subsanación." "Django app"
                resolApp    = component "resoluciones" "Informe de aptitud (#590), declaratoria (#162), generación PDF (ReportLab)." "Django app"
                notifApp    = component "notificaciones" "Notificaciones internas y bitácora de auditoría JSONB (vía signals)." "Django app"
                coreDomain  = component "core" "Transversal: ISGALegacyPort (único puerto real), SGAMockAdapter, validación de PDF, almacenamiento privado, filtro de ámbito (IDOR), middleware." "Módulo compartido"

                expedApp -> authApp "Verifica permisos (RBAC_MATRIX)"
                peticApp -> expedApp "Consulta/actualiza estado del expediente"
                peticApp -> authApp "Verifica permisos"
                verifApp -> peticApp "Consulta peticiones y documentos"
                verifApp -> expedApp "Cambia estado (OBSERVADA / EN_VERIFICACION)"
                resolApp -> verifApp "Verifica checklist 100% completo (RN-003)"
                resolApp -> expedApp "Cambia estado (INFORME_EMITIDO / DECLARADA_APTA)"
                notifApp -> expedApp "Escucha cambios de estado (Django signals)"
                notifApp -> verifApp "Escucha observaciones (Django signals)"
                notifApp -> resolApp "Escucha emisión/declaratoria (Django signals)"
                peticApp -> coreDomain "Usa validación de PDF y almacenamiento privado"
                resolApp -> coreDomain "Usa almacenamiento privado"
                expedApp -> coreDomain "Usa SGAMockAdapter (vía ISGALegacyPort) y filtro de ámbito"
            }
            postgres  = container "PostgreSQL 16" "Persistencia relacional, auditoría JSONB." "PostgreSQL 16" "Base de datos"
            fileStorage = container "Almacenamiento privado de archivos" "Volumen Docker montado; sin URL pública (PrivateMediaStorage)." "Volumen Docker"
        }

        estudiante -> sgtsiaaf.webClient "Usa" "HTTPS"
        secretariaCarrera -> sgtsiaaf.webClient "Usa" "HTTPS"
        secretarioAbogado -> sgtsiaaf.webClient "Usa" "HTTPS"
        analistaApoyo -> sgtsiaaf.webClient "Usa" "HTTPS"
        decano -> sgtsiaaf.webClient "Usa" "HTTPS"
        directorCarrera -> sgtsiaaf.webClient "Usa" "HTTPS"
        responsableDependencia -> sgtsiaaf.webClient "Usa" "HTTPS"
        administrador -> sgtsiaaf.webClient "Usa (también Django Admin)" "HTTPS"

        sgtsiaaf -> sga "Consulta récord académico (lectura, mock)" "Python Adapter Interface (ISGALegacyPort)"
        decano -> firmaec "Firma el memorando fuera del sistema" "Aplicación externa"

        sgtsiaaf.webClient -> sgtsiaaf.nginx "Peticiones REST" "HTTPS / JSON"
        sgtsiaaf.nginx -> sgtsiaaf.django "Proxy pass" "HTTP (Gunicorn, 4 workers)"
        sgtsiaaf.django -> sgtsiaaf.postgres "Lee/escribe (transaccional, select_for_update)" "psycopg3 / SQL"
        sgtsiaaf.django -> sgtsiaaf.fileStorage "Almacena/lee PDF validados" "POSIX File I/O"
        sgtsiaaf.django -> sga "Consulta mock (solo lectura)" "Python Adapter Interface"
    }

    views {

        systemContext sgtsiaaf "C1_Contexto" {
            include *
            autoLayout lr
            description "Nivel 1 — Contexto: los 8 roles institucionales y los dos sistemas externos simulados/no integrados."
        }

        container sgtsiaaf "C2_Contenedores" {
            include *
            autoLayout lr
            description "Nivel 2 — Contenedores: SPA React, Nginx, Backend Django (Gunicorn), PostgreSQL 16, almacenamiento privado."
        }

        component sgtsiaaf.django "C3_Componentes" {
            include *
            autoLayout tb
            description "Nivel 3 — Componentes: las 6 apps Django + el módulo core transversal, con sus dependencias reales (verificadas en el código, no solo planificadas)."
        }

        styles {
            element "Rol" { background #dae8fc; shape person }
            element "Externo, simulado" { background #fff2cc }
            element "Externo, no integrado" { background #f8cecc }
            element "Cliente" { background #d5e8d4 }
            element "Base de datos" { shape cylinder background #e1d5e7 }
            element "Django app" { background #ffffff }
            element "Módulo compartido" { background #f5f5f5 }
        }
    }
}
