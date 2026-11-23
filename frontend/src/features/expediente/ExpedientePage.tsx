import { useContext, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Breadcrumbs } from '@/components/ui/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useConfirm } from '@/components/ui/ConfirmDialog'
import { ArrowLeftIcon, ClipboardCheckIcon, DocumentIcon, SendIcon } from '@/components/ui/icons'
import { ErrorState } from '@/components/ui/ErrorState'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { NotFoundState } from '@/components/ui/NotFoundState'
import { Skeleton } from '@/components/ui/Skeleton'
import { OPERATIONAL_ROLES } from '@/auth/roles'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { ChecklistSection } from './ChecklistSection'
import { ExpedienteHeader } from './ExpedienteHeader'
import { ObservarDialog } from './ObservarDialog'
import { PeticionesSection } from './PeticionesSection'
import { puedeEnviar, puedeObservar } from './accionesPorRolEstado'
import { describeAccionError } from './errors'
import { useChecklist, useEnviarExpediente, useExpedienteDetalle, useObservarExpediente } from './queries'
import styles from './ExpedientePage.module.css'

export default function ExpedientePage() {
  const { id } = useParams<{ id: string }>()
  const auth = useContext(AuthContext)
  const toast = useContext(ToastContext)
  const navigate = useNavigate()
  const roles = auth?.user?.roles ?? []

  const [observarAbierto, setObservarAbierto] = useState(false)
  const [observarError, setObservarError] = useState<string | null>(null)
  const [enviarError, setEnviarError] = useState<string | null>(null)

  const detalleQuery = useExpedienteDetalle(id ?? '')
  const checklistQuery = useChecklist(id ?? '', roles)
  const enviarMutation = useEnviarExpediente(id ?? '')
  const observarMutation = useObservarExpediente(id ?? '')
  const { confirm, dialog } = useConfirm()
  const soloEstudiante = roles.includes('ESTUDIANTE') && !roles.some((rol) => OPERATIONAL_ROLES.includes(rol))

  if (!id) {
    return <NotFoundState description="No se indicó un expediente." title="Expediente no encontrado" />
  }

  if (detalleQuery.isLoading) {
    return <Skeleton count={3} label="Cargando expediente…" variant="card" />
  }

  if (detalleQuery.isError) {
    const presentation = presentApiError(detalleQuery.error)
    if (presentation.kind === 'not-found') {
      return <NotFoundState description="El expediente no existe o no está disponible para su cuenta." title="Expediente no encontrado" />
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

  async function handleEnviar() {
    const confirmado = await confirm({
      title: '¿Enviar el expediente?',
      description: 'Se enviará para su verificación. No podrá modificarlo mientras esté en verificación.',
      confirmLabel: 'Enviar expediente',
    })
    if (!confirmado) {
      return
    }
    setEnviarError(null)
    try {
      await enviarMutation.mutateAsync()
      toast?.showToast('Expediente enviado.', 'success')
    } catch (error) {
      setEnviarError(describeAccionError(error))
    }
  }

  async function handleObservarConfirm(payload: { motivo_observacion: string; peticion_id?: string }) {
    setObservarError(null)
    try {
      await observarMutation.mutateAsync(payload)
      setObservarAbierto(false)
      toast?.showToast('Observación registrada.', 'success')
    } catch (error) {
      setObservarError(describeAccionError(error))
    }
  }

  const mostrarEnviar = puedeEnviar(roles, expediente.estado, true)
  const mostrarObservar = puedeObservar(roles, expediente.estado)

  const migas = soloEstudiante
    ? [{ label: 'Inicio', to: '/estudiante' }, { label: 'Mi trámite' }]
    : [{ label: 'Bandeja de trabajo', to: '/bandeja' }, { label: expediente.numero_expediente }]

  return (
    <div className={styles.page}>
      {dialog}
      <Breadcrumbs items={migas} />
      <ExpedienteHeader
        actions={
          <>
            {mostrarEnviar && (
              <Button loading={enviarMutation.isPending} onClick={() => void handleEnviar()}>
                <SendIcon size={16} />
                Enviar expediente
              </Button>
            )}
            {mostrarObservar && (
              <Button variant="secondary" onClick={() => setObservarAbierto(true)}>
                Observar
              </Button>
            )}
            <Button variant="ghost" onClick={() => navigate(-1)}>
              <ArrowLeftIcon size={16} />
              Volver
            </Button>
          </>
        }
        expediente={expediente}
      />

      {enviarError && (
        <p className={styles.error} role="alert">
          {enviarError}
        </p>
      )}

      <Card icon={<DocumentIcon />} title="Peticiones documentales">
        <PeticionesSection numeroExpediente={expediente.numero_expediente} peticiones={expediente.peticiones} roles={roles} />
      </Card>

      <Card icon={<ClipboardCheckIcon />} title="Checklist de verificación">
        <ChecklistSection
          esPropietario
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
        onConfirm={(payload) => void handleObservarConfirm(payload)}
      />
    </div>
  )
}
