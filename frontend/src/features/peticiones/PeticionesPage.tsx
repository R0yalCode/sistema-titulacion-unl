import { useContext, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { AuthContext } from '@/auth/AuthContext'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { NotFoundState } from '@/components/ui/NotFoundState'
import { Spinner } from '@/components/ui/Spinner'
import { describeAccionError, useExpedienteDetalle } from '@/features/expediente'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { CargarDocumentoDialog } from './CargarDocumentoDialog'
import { PeticionesTabla } from './PeticionesTabla'
import { SolicitarEmisionDialog } from './SolicitarEmisionDialog'
import { useCargarDocumento, useSolicitarEmision } from './queries'
import styles from './PeticionesPage.module.css'

/**
 * V-05 — Gestión de peticiones documentales (FE-T501…FE-T505).
 * Las peticiones llegan anidadas en `GET /expedientes/{id}/` (no existe
 * `GET /peticiones/{id}/`, BE-02) y se crean automáticamente con el
 * expediente: la vista no ofrece "crear petición" (CA-V05-05).
 */
export default function PeticionesPage() {
  const { id } = useParams<{ id: string }>()
  const auth = useContext(AuthContext)
  const toast = useContext(ToastContext)
  const roles = auth?.user?.roles ?? []

  const [aSolicitar, setASolicitar] = useState<PeticionInicializada | null>(null)
  const [aCargar, setACargar] = useState<PeticionInicializada | null>(null)
  const [solicitarError, setSolicitarError] = useState<string | null>(null)
  const [cargarError, setCargarError] = useState<string | null>(null)

  const detalleQuery = useExpedienteDetalle(id ?? '')
  const solicitarMutation = useSolicitarEmision(id ?? '')
  const cargarMutation = useCargarDocumento(id ?? '')

  if (!id) {
    return <NotFoundState description="No se indicó un expediente." title="Expediente no encontrado" />
  }

  if (detalleQuery.isLoading) {
    return <Spinner label="Cargando peticiones…" />
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

  function abrirSolicitud(peticion: PeticionInicializada) {
    setSolicitarError(null)
    setASolicitar(peticion)
  }

  function abrirCarga(peticion: PeticionInicializada) {
    setCargarError(null)
    setACargar(peticion)
  }

  async function confirmarSolicitud(peticion: PeticionInicializada) {
    setSolicitarError(null)
    try {
      await solicitarMutation.mutateAsync(peticion.id)
      setASolicitar(null)
      toast?.showToast(`Emisión solicitada: ${peticion.requisito_nombre}.`, 'success')
    } catch (error) {
      setSolicitarError(describeAccionError(error))
    }
  }

  async function confirmarCarga(peticion: PeticionInicializada, archivo: File) {
    setCargarError(null)
    try {
      const documento = await cargarMutation.mutateAsync({ peticionId: peticion.id, archivo })
      setACargar(null)
      toast?.showToast(`Documento cargado (versión ${documento.version}).`, 'success')
    } catch (error) {
      setCargarError(describeAccionError(error))
    }
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Peticiones documentales</h1>
        <p className={styles.subtitle}>
          Expediente <strong>{expediente.numero_expediente}</strong> · estado {expediente.estado}
        </p>
      </header>

      <Alert title="Las peticiones se generan automáticamente">
        Cada expediente se crea con sus peticiones documentales; no es posible crear peticiones manualmente.{' '}
        <Link to={`/expedientes/${id}`}>Volver al expediente</Link>
      </Alert>

      <h2 className="sr-only">Listado de peticiones</h2>
      <Card title="Requisitos y peticiones">
        <PeticionesTabla
          estadoExpediente={expediente.estado}
          expedienteId={id}
          numeroExpediente={expediente.numero_expediente}
          peticiones={expediente.peticiones}
          roles={roles}
          onCargar={abrirCarga}
          onSolicitar={abrirSolicitud}
        />
      </Card>

      <SolicitarEmisionDialog
        error={solicitarError}
        peticion={aSolicitar}
        submitting={solicitarMutation.isPending}
        onClose={() => setASolicitar(null)}
        onConfirm={(peticion) => void confirmarSolicitud(peticion)}
      />
      <CargarDocumentoDialog
        key={aCargar?.id ?? 'cerrado'}
        error={cargarError}
        peticion={aCargar}
        submitting={cargarMutation.isPending}
        onClose={() => setACargar(null)}
        onConfirm={(peticion, archivo) => void confirmarCarga(peticion, archivo)}
      />
    </main>
  )
}
