import type { PerfilAcademico } from '@/api/endpoints/perfilAcademico'
import { Badge } from '@/components/ui/Badge'
import styles from './NuevaSolicitudPage.module.css'

const ESTADO_PERFIL: Record<PerfilAcademico['estado_perfil'], { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  VALIDADO: { label: 'Perfil validado', variant: 'success' },
  NO_ASOCIADO: { label: 'Sin información académica', variant: 'warning' },
  INCOMPLETO: { label: 'Perfil incompleto', variant: 'warning' },
  INCONSISTENTE: { label: 'Datos inconsistentes', variant: 'danger' },
  CARRERA_INACTIVA: { label: 'Carrera no vigente', variant: 'danger' },
}

function texto(valor: string | null | undefined): string {
  return valor && valor.trim() ? valor : 'No registrado'
}

/**
 * Datos académicos del estudiante, de solo lectura. No hay ningún campo
 * editable: la carrera y la facultad las determina el backend.
 */
export function PerfilAcademicoResumen({ perfil }: { perfil: PerfilAcademico }) {
  const estado = ESTADO_PERFIL[perfil.estado_perfil]
  const { estudiante, carrera, facultad, fuente } = perfil
  const nombre = estudiante ? `${estudiante.nombres} ${estudiante.apellidos}`.trim() : ''

  return (
    <div className={styles.resumen}>
      <div className={styles.resumenEstado}>
        <Badge icon variant={estado.variant}>
          {estado.label}
        </Badge>
        {fuente.es_simulada && <Badge variant="info">Datos simulados</Badge>}
      </div>
      <dl className={styles.campos}>
        <div>
          <dt>Estudiante</dt>
          <dd>{texto(nombre)}</dd>
        </div>
        <div>
          <dt>Identificación</dt>
          <dd>{texto(estudiante?.identificacion)}</dd>
        </div>
        <div>
          <dt>Correo institucional</dt>
          <dd>{texto(estudiante?.correo_institucional)}</dd>
        </div>
        <div>
          <dt>Carrera</dt>
          <dd>
            {texto(carrera?.nombre)}
            {carrera && !carrera.activa && <span className={styles.nota}> (no vigente)</span>}
          </dd>
        </div>
        <div className={styles.campoAncho}>
          <dt>Facultad</dt>
          <dd>{texto(facultad?.nombre)}</dd>
        </div>
        <div className={styles.campoAncho}>
          <dt>Fuente de la información</dt>
          <dd>{fuente.nombre}</dd>
        </div>
      </dl>
    </div>
  )
}
