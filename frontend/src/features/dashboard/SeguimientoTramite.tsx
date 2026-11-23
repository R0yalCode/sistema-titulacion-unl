import type { ReactNode } from 'react'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import type { EtapaTramite, ExpedienteResumen } from '@/api/endpoints/miTramite'
import { AwardIcon, CheckIcon, ClockIcon, DocumentIcon, FlagIcon, SearchIcon, SendIcon } from '@/components/ui/icons'
import { formatFecha } from '@/lib/dates'
import type { ProximoHito } from './presentacion'
import { presentarEstadoExpediente } from './presentacion'
import styles from './SeguimientoTramite.module.css'

const ICONO_ETAPA: Partial<Record<EstadoExpediente, ReactNode>> = {
  BORRADOR: <DocumentIcon size={18} />,
  ENVIADA: <SendIcon size={18} />,
  EN_VERIFICACION: <SearchIcon size={18} />,
  INFORME_EMITIDO: <FlagIcon size={18} />,
  DECLARADA_APTA: <AwardIcon size={18} />,
}

const SITUACION_TEXTO: Record<EtapaTramite['situacion'], string> = {
  completada: 'Completada',
  actual: 'Etapa actual',
  pendiente: 'Pendiente',
}

type SeguimientoTramiteProps = {
  expediente: ExpedienteResumen
  hito: ProximoHito | null
}

/**
 * Línea de tiempo con las etapas reales que devuelve el backend (orden de
 * `TRANSICIONES_PERMITIDAS`). Fechas solo cuando existen en el historial.
 */
export function SeguimientoTramite({ expediente, hito }: SeguimientoTramiteProps) {
  const observada = expediente.estado === 'OBSERVADA'
  const estado = presentarEstadoExpediente(expediente.estado)
  const siguientePendiente = expediente.etapas.find((etapa) => etapa.situacion === 'pendiente')

  return (
    <>
      {expediente.estado === 'CANCELADA' && (
        <p className={styles.notice} role="note">
          Este trámite fue cancelado. Se muestran solo las etapas que llegó a completar.
        </p>
      )}
      <ol className={styles.timeline}>
        {expediente.etapas.map((etapa) => {
          const esActual = etapa.situacion === 'actual'
          const esHito = hito !== null && etapa === siguientePendiente
          return (
            <li
              aria-current={esActual ? 'step' : undefined}
              className={`${styles.step} ${styles[etapa.situacion]} ${esActual && observada ? styles.observada : ''}`}
              key={etapa.codigo}
            >
              <span aria-hidden="true" className={styles.marker}>
                {etapa.situacion === 'completada' ? <CheckIcon size={16} /> : ICONO_ETAPA[etapa.codigo] ?? <ClockIcon size={16} />}
              </span>
              <div className={styles.content}>
                <div className={styles.row}>
                  <h3 className={styles.name}>{etapa.nombre}</h3>
                  <span className={styles.status}>
                    {esActual && observada ? 'En pausa: con observaciones' : SITUACION_TEXTO[etapa.situacion]}
                  </span>
                </div>
                {etapa.fecha && (
                  <p className={styles.date}>
                    {etapa.situacion === 'actual' ? 'Desde el ' : ''}
                    <time dateTime={etapa.fecha}>{formatFecha(etapa.fecha)}</time>
                  </p>
                )}
                {esActual && (
                  <div className={styles.detail}>
                    <p>{estado.descripcion}</p>
                    {observada && expediente.observaciones_pendientes.length > 0 && (
                      <p>
                        <a href="#pendientes">
                          {expediente.observaciones_pendientes.length === 1
                            ? 'Revisa la observación pendiente'
                            : `Revisa las ${expediente.observaciones_pendientes.length} observaciones pendientes`}
                        </a>
                      </p>
                    )}
                  </div>
                )}
                {esHito && hito && (
                  <div className={styles.hito}>
                    <span className={styles.hitoTag}>Próximo hito</span>
                    {hito.contexto && <p>{hito.contexto}</p>}
                    {hito.fecha && (
                      <p>
                        {hito.fechaLabel}: <strong><time dateTime={hito.fecha}>{formatFecha(hito.fecha)}</time></strong>
                      </p>
                    )}
                  </div>
                )}
              </div>
            </li>
          )
        })}
      </ol>
      {expediente.fecha_actualizacion && (
        <p className={styles.updated}>
          Última actualización del expediente:{' '}
          <time dateTime={expediente.fecha_actualizacion}>{formatFecha(expediente.fecha_actualizacion)}</time>
        </p>
      )}
    </>
  )
}
