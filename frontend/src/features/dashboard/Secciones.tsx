import { Link } from 'react-router-dom'
import type { ExpedienteResumen, MovimientoTramite } from '@/api/endpoints/miTramite'
import { Badge, type BadgeVariant } from '@/components/ui/Badge'
import { AlertIcon, ArrowRightIcon, CheckIcon, ClockIcon, DocumentIcon, UploadIcon, XCircleIcon } from '@/components/ui/icons'
import { presentarEstadoPeticion } from '@/features/peticiones'
import { formatFecha, formatFechaHora } from '@/lib/dates'
import type { AccionPendiente } from './presentacion'
import { describirMovimiento } from './presentacion'
import styles from './Secciones.module.css'

// --- Necesitas completar ---------------------------------------------------

export function AccionesPendientes({ acciones }: { acciones: AccionPendiente[] }) {
  if (acciones.length === 0) {
    return (
      <div className={styles.empty} role="status">
        <span className={`${styles.emptyIcon} ${styles.emptyIconSuccess}`}>
          <CheckIcon />
        </span>
        <div>
          <p className={styles.emptyTitle}>No tienes acciones pendientes actualmente.</p>
          <p className={styles.emptyText}>Si se registra una observación sobre tus documentos, aparecerá aquí y en tus notificaciones.</p>
        </div>
      </div>
    )
  }

  return (
    <ul className={styles.actionList}>
      {acciones.map((accion) => (
        <li className={`${styles.action} ${styles[accion.tono]}`} key={accion.id}>
          <span aria-hidden="true" className={styles.actionIcon}>
            {accion.tono === 'warning' ? <AlertIcon size={18} /> : <UploadIcon size={18} />}
          </span>
          <div className={styles.actionBody}>
            <h3 className={styles.actionTitle}>{accion.titulo}</h3>
            <p className={styles.actionText}>{accion.descripcion}</p>
            {accion.motivo && (
              <blockquote className={styles.motivo}>
                <span className={styles.motivoLabel}>Motivo indicado:</span> {accion.motivo}
              </blockquote>
            )}
            {accion.fecha && (
              <p className={styles.actionMeta}>
                Registrada el <time dateTime={accion.fecha}>{formatFecha(accion.fecha)}</time>
              </p>
            )}
            <Link className={styles.actionLink} to={accion.href}>
              {accion.accionLabel} <ArrowRightIcon size={16} />
            </Link>
          </div>
        </li>
      ))}
    </ul>
  )
}

// --- Documentación ---------------------------------------------------------

const ORDEN_ESTADOS = ['OBSERVADO', 'PENDIENTE', 'SOLICITADO', 'CARGADO', 'LEGALIZADO', 'VERIFICADO']

const COLOR_SEGMENTO: Record<BadgeVariant, string> = {
  warning: styles.segWarning as string,
  neutral: styles.segNeutral as string,
  info: styles.segInfo as string,
  success: styles.segSuccess as string,
  danger: styles.segDanger as string,
}

export function DocumentosResumen({ expediente }: { expediente: ExpedienteResumen }) {
  const { peticiones } = expediente
  if (peticiones.length === 0) {
    return <p className={styles.emptyText}>Tu expediente todavía no tiene requisitos documentales registrados.</p>
  }

  const conteo = new Map<string, number>()
  for (const peticion of peticiones) {
    conteo.set(peticion.estado_peticion, (conteo.get(peticion.estado_peticion) ?? 0) + 1)
  }
  const estados = [...conteo.keys()].sort((a, b) => {
    const ia = ORDEN_ESTADOS.indexOf(a)
    const ib = ORDEN_ESTADOS.indexOf(b)
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
  })
  const motivos = new Map(expediente.observaciones_pendientes.map((o) => [o.peticion_id, o.motivo_observacion]))

  return (
    <div className={styles.docs}>
      <div aria-hidden="true" className={styles.stack}>
        {estados.map((estado) => (
          <span
            className={COLOR_SEGMENTO[presentarEstadoPeticion(estado).variant]}
            key={estado}
            style={{ flexGrow: conteo.get(estado) }}
          />
        ))}
      </div>
      <ul aria-label="Resumen por estado" className={styles.legend}>
        {estados.map((estado) => {
          const { label, variant } = presentarEstadoPeticion(estado)
          return (
            <li key={estado}>
              <span aria-hidden="true" className={`${styles.legendDot} ${COLOR_SEGMENTO[variant]}`} />
              {label}: <strong>{conteo.get(estado)}</strong>
            </li>
          )
        })}
      </ul>

      <ul className={styles.docList}>
        {peticiones.map((peticion) => {
          const { label, variant } = presentarEstadoPeticion(peticion.estado_peticion)
          const motivo = motivos.get(peticion.id)
          return (
            <li className={styles.doc} key={peticion.id}>
              <span aria-hidden="true" className={styles.docIcon}>
                <DocumentIcon size={18} />
              </span>
              <div className={styles.docBody}>
                <Link className={styles.docName} to={`/expedientes/${expediente.id}/peticiones/${peticion.id}`}>
                  {peticion.requisito_nombre}
                </Link>
                {motivo && <p className={styles.docMotivo}>Observación: {motivo}</p>}
              </div>
              <Badge variant={variant}>{label}</Badge>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// --- Últimos movimientos ---------------------------------------------------

const MAX_MOVIMIENTOS_VISIBLES = 5

function IconoMovimiento({ movimiento }: { movimiento: MovimientoTramite }) {
  if (movimiento.tipo === 'documento_cargado') {
    return <UploadIcon size={16} />
  }
  if (movimiento.tipo === 'observacion') {
    return <AlertIcon size={16} />
  }
  if (movimiento.estado_nuevo === 'CANCELADA') {
    return <XCircleIcon size={16} />
  }
  if (movimiento.estado_nuevo === 'DECLARADA_APTA') {
    return <CheckIcon size={16} />
  }
  return <ClockIcon size={16} />
}

export function UltimosMovimientos({ movimientos }: { movimientos: MovimientoTramite[] }) {
  if (movimientos.length === 0) {
    return <p className={styles.emptyText}>Aún no hay movimientos registrados en tu trámite.</p>
  }
  return (
    <ol className={styles.feed}>
      {movimientos.slice(0, MAX_MOVIMIENTOS_VISIBLES).map((movimiento, index) => {
        const { titulo, descripcion, tono } = describirMovimiento(movimiento)
        return (
          <li className={styles.feedItem} key={`${movimiento.tipo}-${movimiento.fecha}-${index}`}>
            <span aria-hidden="true" className={`${styles.feedIcon} ${styles[`feed_${tono}`]}`}>
              <IconoMovimiento movimiento={movimiento} />
            </span>
            <div className={styles.feedBody}>
              <p className={styles.feedTitle}>{titulo}</p>
              <p className={styles.feedText}>{descripcion}</p>
            </div>
            <time className={styles.feedDate} dateTime={movimiento.fecha}>
              {formatFechaHora(movimiento.fecha)}
            </time>
          </li>
        )
      })}
    </ol>
  )
}
