# ADR-001: Arquitectura Hexagonal con Monolito Modular

## Estado
Aceptado

## Contexto
El SGT-SIAAF requiere una arquitectura que permita:
- Separación clara entre dominio de negocio y detalles técnicos
- Testabilidad aislada del dominio
- Evolución independiente de módulos
- Cumplimiento de principios de arquitectura limpia

## Decisión
Se adopta **Arquitectura Hexagonal (Ports & Adapters)** combinada con **Monolito Modular** para el MVP (Fase 1 - Aptitud Legal, Art. 235 RRA-UNL).

### Estructura de paquetes
```
src/
├── core/
│   ├── domain/          # Entidades, value objects, servicios de dominio puros
│   ├── ports/           # Interfaces (puertos de entrada/salida)
│   └── adapters/        # Implementaciones técnicas (PDF, Mock SGA, Storage, etc.)
├── apps/
│   ├── authentication/  # JWT, RBAC, Usuarios
│   ├── expedientes/     # Expedientes, plazos, bandeja
│   ├── peticiones/      # Peticiones, documentos, PDF
│   ├── verificacion/    # Checklist, observaciones, subsanación
│   ├── resoluciones/    # Informes, declaratorias, PDF generator
│   └── notificaciones/  # In-app notifications, auditoría
└── config/              # Settings, URLs, WSGI
```

### Principios
1. **Dominio puro**: Sin dependencias de Django, BD, frameworks externos
2. **Puertos definidos por el dominio**: El dominio define qué necesita (ej. `ISGALegacyPort`)
3. **Adaptadores intercambiables**: Mock SGA → SGA real sin tocar dominio
3. **Inyección de dependencias**: Los adaptadores se inyectan en servicios de dominio
4. **Módulos Django como adaptadores de entrada**: Views, serializers, models = adaptadores

## Alternativas consideradas
1. **Arquitectura en capas tradicional**: Rechazada - fuerte acoplamiento a Django/BD
2. **Microservicios**: Rechazada - complejidad operacional excesiva para MVP académico
3. **Clean Architecture pura**: Similar, pero Hexagonal define mejor los puertos

## Consecuencias
- ✅ Testabilidad: Dominio testeable sin BD ni Django
- ✅ Mantenibilidad: Cambios en BD/Framework no afectan dominio
- ✅ Evolución: Preparado para Fase 2/3 sin reescritura
- ⚠️ Curva de aprendizaje: Equipo debe entender Puertos/Adaptadores
- ⚠️ Boilerplate inicial: Más archivos/estructuras iniciales

## Referencias
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Monolito Modular (Simon Brown)](https://simonbrown.je/modular-monolith/)
- `constitucion.md` Principios C-002, C-003, C-017, C-019
- `plan.md` § 11, § 13, § 21