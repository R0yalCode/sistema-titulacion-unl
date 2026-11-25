import { useContext, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Alert } from '@/components/ui/Alert'
import { Breadcrumbs } from '@/components/ui/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useConfirm } from '@/components/ui/ConfirmDialog'
import { ArrowLeftIcon, ClipboardCheckIcon, DocumentIcon, SearchIcon } from '@/components/ui/icons'
import { NotFoundState } from '@/components/ui/NotFoundState'
import { Skeleton } from '@/components/ui/Skeleton'
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
import { presentarEstado } from '@/lib/estados'
import { esEstadoFinal, puedeIniciarVerificacion } from './accionesFuncionario'
import { useIniciarVerificacion, useInvalidarTrasAccion } from './queries'
import { ResolucionesSection } from './ResolucionesSection'
import styles from './DetalleFuncionarioPage.module.css'
import { QueryErrorView } from '@/components/errors/QueryErrorView'

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
  const { confirm, dialog } = useConfirm()

  const volver = (
    <Link className={styles.volver} to="/bandeja">
      <ArrowLeftIcon size={16} />
      Volver a la bandeja
    </Link>
  )

  if (!id) {
    return <NotFoundState description="No se indicó un expediente." title="Expediente no encontrado" />
  }

  if (detalleQuery.isLoading) {
    return <Skeleton count={3} label="Cargando expediente…" variant="card" />
  }

  if (detalleQuery.isError) {
    return (
      <QueryErrorView
        error={detalleQuery.error}
        notFoundMessage="El expediente no existe o está fuera del ámbito de su cuenta."
        notFoundTitle="Expediente no encontrado"
        onRetry={() => detalleQuery.refetch()}
      />
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
    const confirmado = await confirm({
      title: '¿Iniciar la verificación?',
      description: 'El expediente pasará a "En verificación" y se generará su checklist.',
      confirmLabel: 'Iniciar verificación',
    })
    if (!confirmado) {
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

  const estadoLabel = presentarEstado('expediente', expediente.estado).label

  return (
    <div className={styles.page}>
      {dialog}
      <div className={styles.navegacion}>
        <Breadcrumbs items={[{ label: 'Bandeja de trabajo', to: '/bandeja' }, { label: expediente.numero_expediente }]} />
        {volver}
      </div>
      <ExpedienteHeader
        actions={
          mostrarIniciar || mostrarObservar ? (
            <>
              {mostrarIniciar && (
                <Button loading={iniciarMutation.isPending} onClick={() => void iniciar()}>
                  <SearchIcon size={16} />
                  Iniciar verificación
                </Button>
              )}
              {mostrarObservar && (
                <Button variant="secondary" onClick={() => setObservarAbierto(true)}>
                  Observar
                </Button>
              )}
            </>
          ) : undefined
        }
        expediente={expediente}
      />
      {final && (
        <Alert title="Expediente en estado final">
          El expediente está en estado «{estadoLabel}»: solo se permite su consulta.
        </Alert>
      )}
      {!final && !mostrarIniciar && !mostrarObservar && (
        <p className={styles.sinAcciones}>
          No hay acciones de estado disponibles para su rol con el expediente en «{estadoLabel}».
        </p>
      )}
      {accionError && <Alert variant="danger">{accionError}</Alert>}

      {/* Siempre montada: tras la declaratoria el estado pasa a final y el resultado debe seguir visible. */}
      <ResolucionesSection checklistQuery={checklistQuery} estado={expediente.estado} expedienteId={id} roles={roles} />

      <Card icon={<DocumentIcon />} title="Peticiones documentales">
        <PeticionesSection numeroExpediente={expediente.numero_expediente} peticiones={expediente.peticiones} roles={roles} />
      </Card>

      <Card icon={<ClipboardCheckIcon />} title="Checklist de verificación">
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
    </div>
  )
}
