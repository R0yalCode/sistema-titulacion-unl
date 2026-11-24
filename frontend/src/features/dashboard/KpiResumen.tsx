import { Link } from 'react-router-dom'
import type { ExpedienteResumen } from '@/api/endpoints/miTramite'
import { ArrowRightIcon, ChartIcon, FlagIcon, FolderIcon, ListCheckIcon } from '@/components/ui/icons'
import { KpiCard, KpiText, kpiLinkClass, type KpiTone } from '@/components/ui/KpiCard'
import { KpiGrid } from '@/components/ui/KpiGrid'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { formatFecha } from '@/lib/dates'
import type { AccionPendiente, ProximoHito } from './presentacion'
import { porcentajeProgreso, presentarEstadoExpediente } from './presentacion'
import styles from './KpiResumen.module.css'

type KpiResumenProps = {
  expediente: ExpedienteResumen
  acciones: AccionPendiente[]
  hito: ProximoHito | null
}

const TONO_POR_VARIANTE: Record<string, KpiTone> = {
  warning: 'warning',
  success: 'success',
  danger: 'danger',
}

/** Los cuatro KPI del estudiante, con el KpiCard compartido del Design System. */
export function KpiResumen({ expediente, acciones, hito }: KpiResumenProps) {
  const estado = presentarEstadoExpediente(expediente.estado)
  const porcentaje = porcentajeProgreso(expediente)
  const progreso = expediente.progreso

  return (
    <KpiGrid label="Resumen de tu trámite">
      <KpiCard
        footer={
          <Link className={kpiLinkClass} to={`/expedientes/${expediente.id}`}>
            Ver mi trámite <ArrowRightIcon size={16} />
          </Link>
        }
        icon={<FolderIcon />}
        title="Estado actual"
        tone={TONO_POR_VARIANTE[estado.variant] ?? 'default'}
      >
        <p className={styles.estado}>
          <StatusBadge dominio="expediente" label={estado.label} valor={expediente.estado} />
        </p>
        <KpiText>{estado.descripcion}</KpiText>
      </KpiCard>

      <KpiCard
        icon={<ChartIcon />}
        title="Progreso general"
        variant="glass"
        unit={porcentaje !== null ? '%' : undefined}
        value={porcentaje !== null ? porcentaje : undefined}
      >
        {porcentaje !== null && progreso ? (
          <>
            <ProgressBar
              label="Progreso general del trámite"
              value={porcentaje}
              valueText={`${progreso.etapas_completadas} de ${progreso.etapas_totales} etapas completadas`}
            />
            <KpiText>
              {progreso.etapas_completadas} de {progreso.etapas_totales} etapas completadas
            </KpiText>
          </>
        ) : (
          <KpiText>No aplica: el trámite no avanza en el flujo de titulación.</KpiText>
        )}
      </KpiCard>

      <KpiCard
        footer={
          acciones.length > 0 ? (
            <a className={kpiLinkClass} href="#pendientes">
              Ver qué hacer <ArrowRightIcon size={16} />
            </a>
          ) : undefined
        }
        icon={<ListCheckIcon />}
        title="Acciones pendientes"
        tone={acciones.length > 0 ? 'warning' : 'success'}
        value={acciones.length}
      >
        <KpiText>
          {acciones.length === 0
            ? 'No tienes acciones pendientes actualmente.'
            : acciones.length === 1
              ? 'Hay una acción que requiere tu atención.'
              : `Hay ${acciones.length} acciones que requieren tu atención.`}
        </KpiText>
      </KpiCard>

      <KpiCard
        footer={
          hito ? (
            <a className={kpiLinkClass} href="#seguimiento">
              Ver seguimiento <ArrowRightIcon size={16} />
            </a>
          ) : undefined
        }
        icon={<FlagIcon />}
        title="Próximo hito"
      >
        {hito ? (
          <>
            <p className={styles.hito}>{hito.nombre}</p>
            <KpiText>
              {hito.fecha ? (
                <>
                  {hito.fechaLabel}: <strong>{formatFecha(hito.fecha)}</strong>
                </>
              ) : (
                'Sin fecha registrada.'
              )}
            </KpiText>
          </>
        ) : (
          <KpiText>
            {expediente.estado === 'DECLARADA_APTA'
              ? 'Tu trámite concluyó; no hay hitos pendientes.'
              : 'No hay un próximo hito registrado.'}
          </KpiText>
        )}
      </KpiCard>
    </KpiGrid>
  )
}
