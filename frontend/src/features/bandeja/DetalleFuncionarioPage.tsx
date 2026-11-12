import { useContext, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { NotFoundState } from '@/components/ui/NotFoundState'
import { Spinner } from '@/components/ui/Spinner'
import {
  ChecklistSection,
  ExpedienteHeader,
  ObservarDialog,
  PeticionesSection,
  describeAccionError,
  puedeObservar,
  useChecklist,
  useExpedienteDetalle,
  useObservarExpediente,
} from '@/features/expediente'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { esEstadoFinal, puedeIniciarVerificacion } from './accionesFuncionario'
import { useIniciarVerificacion, useInvalidarTrasAccion } from './queries'
import { ResolucionesSection } from './ResolucionesSection'
import styles from './DetalleFuncionarioPage.module.css'

/**
 * V-08 — Detalle del funcionario. Bloque V-08a (FE-T801…FE-T803, FE-T806…FE-T809):
 * reutiliza los componentes reales de V-04 con las acciones del funcionario
 * que el backend permite por rol y estado.
 */
export default function DetalleFuncionarioPage() {
  const { id } = useParams<{ id: string }>()
  const auth = useContext(AuthContext)
  const toast = useContext(ToastContext)
  const roles = auth?.user?.roles ?? []

  const [observarAbierto, setObservarAbierto] = useState(false)
  const [observarError, setObservarError] = useState<string | null>(null)
  const [accionError, setAccionError] = useState<string | null>(null)

  const detalleQuery = useExpedienteDetalle(id ?? '')
  const checklistQuery = useChecklist(id ?? '', roles)
  const observarMutation = useObservarExpediente(id ?? '')
  const iniciarMutation = useIniciarVerificacion(id ?? '')
  const invalidar = useInvalidarTrasAccion(id ?? '')

  const volver = (
    <Link className={styles.volver} to="/bandeja">
      Volver a la bandeja
    </Link>
  )

  if (!id) {
    return <NotFoundState description="No se indicó un expediente." title="Expediente no encontrado" />
  }

  if (detalleQuery.isLoading) {
    return <Spinner label="Cargando expediente…" />
  }

  if (detalleQuery.isError) {
    const presentation = presentApiError(detalleQuery.error)
    if (presentation.kind === 'not-found') {
      return (
        <NotFoundState
          action={volver}
          description="El expediente no existe o está fuera del ámbito de su cuenta."
          title="Expediente no encontrado"
        />
      )
    }
    if (presentation.kind === 'forbidden') {
      return (
        <ForbiddenState
          action={<Link to="/no-habilitado?motivo=rol-no-autorizado">Más información</Link>}
          description={presentation.description}
          title={presentation.title}
        />
      )
    }
    return (
      <ErrorState description={presentation.description} title={presentation.title} onRetry={() => detalleQuery.refetch()} />
    )
  }

  const expediente = detalleQuery.data
  if (!expediente) {
    return null
  }

  const final = esEstadoFinal(expediente.estado)
  const mostrarIniciar = !final && puedeIniciarVerificacion(roles, expediente.estado)
  const mostrarObservar = !final && puedeObservar(roles, expediente.estado)

  async function iniciar() {
    if (!window.confirm('¿Confirma el inicio de la verificación? Se generará el checklist del expediente.')) {
      return
    }
    setAccionError(null)
    try {
      await iniciarMutation.mutateAsync()
      toast?.showToast('Verificación iniciada.', 'success')
    } catch (error) {
      setAccionError(describeAccionError(error))
    }
  }

  async function observar(payload: { motivo_observacion: string; peticion_id?: string }) {
    setObservarError(null)
    try {
      await observarMutation.mutateAsync(payload)
      invalidar()
      setObservarAbierto(false)
      toast?.showToast('Observación registrada.', 'success')
    } catch (error) {
      setObservarError(describeAccionError(error))
    }
  }

  return (
    <main className={styles.page}>
      {volver}
      <ExpedienteHeader expediente={expediente} />

      {final && (
        <Alert title="Expediente en estado final">
          El expediente está en estado {expediente.estado}: solo se permite su consulta.
        </Alert>
      )}

      <h2 className="sr-only">Acciones del expediente</h2>
      <div className={styles.acciones}>
        {mostrarIniciar && (
          <Button loading={iniciarMutation.isPending} onClick={() => void iniciar()}>
            Iniciar verificación
          </Button>
        )}
        {mostrarObservar && (
          <Button variant="secondary" onClick={() => setObservarAbierto(true)}>
            Observar
          </Button>
        )}
        {!final && !mostrarIniciar && !mostrarObservar && (
          <p className={styles.sinAcciones}>
            No hay acciones de estado disponibles para su rol con el expediente en {expediente.estado}.
          </p>
        )}
      </div>
      {accionError && <Alert variant="danger">{accionError}</Alert>}

      {/* Siempre montada: tras la declaratoria el estado pasa a final y el resultado debe seguir visible. */}
      <ResolucionesSection checklistQuery={checklistQuery} estado={expediente.estado} expedienteId={id} roles={roles} />

      <Card title="Peticiones documentales">
        <PeticionesSection numeroExpediente={expediente.numero_expediente} peticiones={expediente.peticiones} roles={roles} />
      </Card>

      <Card title="Checklist de verificación">
        <ChecklistSection
          esPropietario={false}
          estadoExpediente={expediente.estado}
          expedienteId={id}
          query={checklistQuery}
          roles={roles}
        />
      </Card>

      <ObservarDialog
        error={observarError}
        open={observarAbierto}
        peticiones={expediente.peticiones}
        submitting={observarMutation.isPending}
        onClose={() => setObservarAbierto(false)}
        onConfirm={(payload) => void observar(payload)}
      />
    </main>
  )
}
