import { useContext } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { NotFoundState } from '@/components/ui/NotFoundState'
import { ArrowLeftIcon, DocumentIcon, InfoIcon } from '@/components/ui/icons'
import { Skeleton } from '@/components/ui/Skeleton'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { DescargaButton, puedeDescargar, useExpedienteDetalle } from '@/features/expediente'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { formatFecha } from '@/lib/dates'
import { nombreRol, presentarEstado } from '@/lib/estados'
import { tieneDocumento } from './accionesPeticion'
import { buscarPeticion, describirEstadoPeticion } from './seguimiento'
import styles from './SeguimientoPeticionPage.module.css'

/**
 * V-06 — Seguimiento de petición (FE-T601…FE-T604).
 * Muestra solo datos reales: la petición sale del detalle del expediente
 * (no existe `GET /peticiones/{id}/`, BE-02), sin historial, sin hitos
 * inferidos y sin versiones inventadas.
 */
export default function SeguimientoPeticionPage() {
  const { id, peticionId } = useParams<{ id: string; peticionId: string }>()
  const auth = useContext(AuthContext)
  const roles = auth?.user?.roles ?? []
  const detalleQuery = useExpedienteDetalle(id ?? '')

  const enlacesSalida = id ? (
    <nav aria-label="Navegación de la petición" className={styles.enlaces}>
      <Link className={styles.enlace} to={`/expedientes/${id}/peticiones`}>
        <ArrowLeftIcon size={16} />
        Volver a las peticiones
      </Link>
      <Link className={styles.enlace} to={`/expedientes/${id}`}>
        Volver al expediente
      </Link>
    </nav>
  ) : null

  if (!id || !peticionId) {
    return <NotFoundState description="No se indicó la petición." title="Petición no encontrada" />
  }

  if (detalleQuery.isLoading) {
    return <Skeleton count={3} label="Cargando petición…" variant="card" />
  }

  if (detalleQuery.isError) {
    const presentation = presentApiError(detalleQuery.error)
    if (presentation.kind === 'not-found') {
      return (
        <NotFoundState
          description="El expediente no existe o no está disponible para su cuenta."
          title="Expediente no encontrado"
        />
      )
    }
    if (presentation.kind === 'forbidden') {
      return <ForbiddenState description={presentation.description} title={presentation.title} />
    }
    return (
      <ErrorState
        description={presentation.description}
        title={presentation.title}
        onRetry={() => detalleQuery.refetch()}
      />
    )
  }

  const expediente = detalleQuery.data
  if (!expediente) {
    return null
  }

  const peticion = buscarPeticion(expediente.peticiones, peticionId)
  if (!peticion) {
    return (
      <div className={styles.page}>
        <NotFoundState
          description="La petición no pertenece a este expediente o no está disponible para su cuenta."
          title="Petición no encontrada"
        />
        {enlacesSalida}
      </div>
    )
  }

  const conDocumento = tieneDocumento(peticion.estado_peticion)

  return (
    <div className={styles.page}>
      {enlacesSalida}
      <header className={styles.header}>
        <p className={styles.eyebrow}>Petición documental · {expediente.numero_expediente}</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>{peticion.requisito_nombre}</h1>
          <StatusBadge dominio="peticion" valor={peticion.estado_peticion} />
        </div>
      </header>

      <Alert title="Historial no disponible">
        El sistema todavía no expone el detalle ni el historial de cada petición (dependencia BE-02). Se muestra
        únicamente su estado actual.
      </Alert>

      <Card icon={<InfoIcon />} title="Resumen de la petición">
        <dl className={styles.datos}>
          <div>
            <dt>Estado actual</dt>
            <dd>{describirEstadoPeticion(peticion.estado_peticion)}</dd>
          </div>
          <div>
            <dt>Requisito</dt>
            <dd>
              {peticion.requisito_nombre} <span className={styles.codigo}>({peticion.requisito_codigo})</span>
            </dd>
          </div>
          <div>
            <dt>Dependencia emisora</dt>
            <dd>{nombreRol(peticion.dependencia_emisora)}</dd>
          </div>
          <div>
            <dt>Expediente</dt>
            <dd>
              {expediente.numero_expediente} · {presentarEstado('expediente', expediente.estado).label}
            </dd>
          </div>
          <div>
            <dt>Fecha de registro</dt>
            <dd>{formatFecha(expediente.fecha_creacion)} (creada junto con el expediente)</dd>
          </div>
        </dl>
      </Card>

      <Card icon={<DocumentIcon />} title="Documento">
        {conDocumento && puedeDescargar(roles) ? (
          <div className={styles.documento}>
            <p>Descargue la versión vigente del documento.</p>
            <DescargaButton
              fallbackFilename={`${expediente.numero_expediente}-${peticion.requisito_codigo}.pdf`}
              peticionId={peticion.id}
            />
          </div>
        ) : (
          <p>
            {conDocumento
              ? 'Su rol no tiene acceso a la descarga de este documento.'
              : 'Todavía no hay un documento cargado para esta petición.'}
          </p>
        )}
        <p className={styles.nota}>
          Las versiones anteriores no se pueden consultar: el sistema no expone el listado de versiones (BE-02).
        </p>
      </Card>
    </div>
  )
}
