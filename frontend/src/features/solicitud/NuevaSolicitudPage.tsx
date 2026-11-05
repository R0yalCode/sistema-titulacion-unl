import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiRequestError } from '@/api/errors'
import { Button } from '@/components/ui/Button'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { presentApiError } from '@/lib/apiErrorPresentation'
import {
  clearNuevaSolicitudDraft,
  getNuevaSolicitudDraft,
  recordVisitedExpediente,
  saveNuevaSolicitudDraft,
} from '@/lib/storage'
import { NuevaSolicitudForm } from './NuevaSolicitudForm'
import { useCrearExpediente } from './queries'
import styles from './NuevaSolicitudPage.module.css'

const UNAVAILABLE_STATUSES = [500, 502, 503, 504]

type ErrorKind = 'activo-existente' | 'ambiguo' | 'generico'

type ErrorInfo = {
  message: string
  kind: ErrorKind
}

function describeError(error: ApiRequestError): ErrorInfo {
  const { status, isNetworkError, isTimeout, message } = error.error

  if (isNetworkError || isTimeout) {
    return {
      kind: 'ambiguo',
      message:
        'No se pudo confirmar si la solicitud se creó por un problema de conexión. No vuelva a enviarla todavía: revise primero su panel para comprobar si ya tiene un expediente activo.',
    }
  }
  if (status === 400 && message.toLowerCase().includes('activo')) {
    return { kind: 'activo-existente', message }
  }
  if (status === 400 || status === 422) {
    return { kind: 'generico', message }
  }
  if (UNAVAILABLE_STATUSES.includes(status)) {
    return { kind: 'generico', message: presentApiError(error).description }
  }
  return { kind: 'generico', message: 'No se pudo crear la solicitud. Intente nuevamente.' }
}

export default function NuevaSolicitudPage() {
  const navigate = useNavigate()
  const toast = useContext(ToastContext)
  const mutation = useCrearExpediente()
  const [carreraId, setCarreraId] = useState(() => getNuevaSolicitudDraft() ?? '')
  const [errorInfo, setErrorInfo] = useState<ErrorInfo | null>(null)

  function handleCarreraIdChange(value: string) {
    setCarreraId(value)
    if (value.trim()) {
      saveNuevaSolicitudDraft(value)
    } else {
      clearNuevaSolicitudDraft()
    }
  }

  async function handleSubmit(value: string): Promise<boolean> {
    setErrorInfo(null)
    try {
      const expediente = await mutation.mutateAsync(value)
      recordVisitedExpediente(expediente.id, expediente.numero_expediente)
      clearNuevaSolicitudDraft()
      toast?.showToast(`Solicitud creada: ${expediente.numero_expediente}.`, 'success')
      navigate(`/expedientes/${expediente.id}`, { replace: true })
      return true
    } catch (error) {
      if (error instanceof ApiRequestError) {
        if (error.error.status === 403) {
          navigate('/no-habilitado', { replace: true })
          return false
        }
        setErrorInfo(describeError(error))
        return false
      }
      setErrorInfo({ kind: 'generico', message: 'No se pudo crear la solicitud. Intente nuevamente.' })
      return false
    }
  }

  return (
    <main className={styles.page}>
      <h1>Crear solicitud (V-03)</h1>
      <p className={styles.description}>
        Inicie su trámite de titulación. Solo puede tener un expediente activo a la vez.
      </p>

      <NuevaSolicitudForm
        initialCarreraId={carreraId}
        serverError={errorInfo?.message ?? null}
        submitting={mutation.isPending}
        onCarreraIdChange={handleCarreraIdChange}
        onSubmit={handleSubmit}
      />

      {(errorInfo?.kind === 'activo-existente' || errorInfo?.kind === 'ambiguo') && (
        <Button variant="secondary" onClick={() => navigate('/estudiante')}>
          Ir a mi panel
        </Button>
      )}
    </main>
  )
}
