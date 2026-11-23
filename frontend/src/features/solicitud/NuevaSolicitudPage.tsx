import { useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { PerfilAcademico } from '@/api/endpoints/perfilAcademico'
import { ApiRequestError } from '@/api/errors'
import { Alert } from '@/components/ui/Alert'
import { Breadcrumbs } from '@/components/ui/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { Skeleton } from '@/components/ui/Skeleton'
import { FolderIcon, UserIcon } from '@/components/ui/icons'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { clearNuevaSolicitudDraft, recordVisitedExpediente } from '@/lib/storage'
import { NuevaSolicitudForm } from './NuevaSolicitudForm'
import { PerfilAcademicoResumen } from './PerfilAcademicoResumen'
import { useCrearExpediente, usePerfilAcademico } from './queries'
import styles from './NuevaSolicitudPage.module.css'

const UNAVAILABLE_STATUSES = [500, 502, 503, 504]
const MOTIVO_EXPEDIENTE_ACTIVO = 'expediente_activo_existente'

type ErrorKind = 'activo-existente' | 'ambiguo' | 'perfil' | 'generico'

type ErrorInfo = {
  message: string
  kind: ErrorKind
}

/** `code` estable del cuerpo `{"detail", "code"}` de los errores de dominio. */
function codigoDominio(error: ApiRequestError): string | null {
  const raw = error.error.raw
  if (typeof raw === 'object' && raw !== null && typeof (raw as { code?: unknown }).code === 'string') {
    return (raw as { code: string }).code
  }
  return null
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
  const codigo = codigoDominio(error)
  if (codigo === MOTIVO_EXPEDIENTE_ACTIVO || (status === 400 && message.toLowerCase().includes('activo'))) {
    return { kind: 'activo-existente', message }
  }
  if (status === 422) {
    return { kind: 'perfil', message }
  }
  if (status === 400) {
    return { kind: 'generico', message }
  }
  if (status === 503 && codigo) {
    return { kind: 'generico', message }
  }
  if (UNAVAILABLE_STATUSES.includes(status)) {
    return { kind: 'generico', message: presentApiError(error).description }
  }
  return { kind: 'generico', message: 'No se pudo crear la solicitud. Intente nuevamente.' }
}

const TITULO_BLOQUEO: Record<PerfilAcademico['estado_perfil'], string> = {
  VALIDADO: 'No puede iniciar un trámite nuevo',
  NO_ASOCIADO: 'No encontramos su información académica',
  INCOMPLETO: 'Su información académica está incompleta',
  INCONSISTENTE: 'Su información académica no es coherente',
  CARRERA_INACTIVA: 'Su carrera no está vigente',
}

export default function NuevaSolicitudPage() {
  const navigate = useNavigate()
  const toast = useContext(ToastContext)
  const perfilQuery = usePerfilAcademico()
  const mutation = useCrearExpediente()
  const [errorInfo, setErrorInfo] = useState<ErrorInfo | null>(null)

  const perfilProhibido = perfilQuery.error?.error.status === 403
  useEffect(() => {
    if (perfilProhibido) {
      navigate('/no-habilitado', { replace: true })
    }
  }, [perfilProhibido, navigate])

  async function handleSubmit(): Promise<boolean> {
    setErrorInfo(null)
    try {
      const expediente = await mutation.mutateAsync()
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

  function renderContenido() {
    if (perfilQuery.isLoading || perfilProhibido) {
      return (
        <Card icon={<UserIcon />} title="Sus datos académicos">
          <Skeleton count={4} label="Consultando su información académica…" variant="text" />
        </Card>
      )
    }
    // Con datos previos (p. ej. falla la recarga tras un error de red al
    // crear) se sigue mostrando el perfil y el aviso de la creación.
    if (perfilQuery.isError && !perfilQuery.data) {
      const presentacion = presentApiError(perfilQuery.error)
      const codigo = codigoDominio(perfilQuery.error)
      return (
        <ErrorState
          description={codigo ? perfilQuery.error.error.message : presentacion.description}
          title="No se pudo consultar su información académica"
          onRetry={() => void perfilQuery.refetch()}
        />
      )
    }

    const perfil = perfilQuery.data
    if (!perfil) {
      return null
    }
    const expedienteActivo = perfil.motivos_bloqueo.some((m) => m.codigo === MOTIVO_EXPEDIENTE_ACTIVO)
    const motivosPerfil = perfil.motivos_bloqueo.filter((m) => m.codigo !== MOTIVO_EXPEDIENTE_ACTIVO)

    return (
      <>
        {perfil.fuente.es_simulada && (
          <Alert title="Información académica simulada" variant="info">
            Estos datos provienen de una simulación de demostración del SGA ({perfil.fuente.nombre}). Todavía no existe
            conexión con el sistema académico institucional.
          </Alert>
        )}

        <Card icon={<UserIcon />} title="Sus datos académicos">
          <PerfilAcademicoResumen perfil={perfil} />
        </Card>

        {perfil.puede_iniciar_tramite && perfil.carrera ? (
          <Card icon={<FolderIcon />} title="Iniciar trámite">
            <NuevaSolicitudForm
              carreraNombre={perfil.carrera.nombre}
              serverError={errorInfo?.message ?? null}
              submitting={mutation.isPending}
              onSubmit={handleSubmit}
            />
          </Card>
        ) : !perfil.perfil_validado ? (
          <Alert title={TITULO_BLOQUEO[perfil.estado_perfil]} variant="warning">
            <ul className={styles.motivos}>
              {motivosPerfil.map((motivo) => (
                <li key={motivo.codigo}>{motivo.mensaje}</li>
              ))}
            </ul>
            <p className={styles.notaBloqueo}>
              No es posible iniciar el trámite hasta que su información académica se corrija. No necesita ingresar ningún
              identificador.
            </p>
          </Alert>
        ) : expedienteActivo ? (
          <Alert title="Ya tiene un trámite en curso" variant="info">
            Solo puede tener un expediente de titulación activo a la vez. Consulte su avance desde su panel.
          </Alert>
        ) : null}

        {errorInfo && !perfil.puede_iniciar_tramite && (errorInfo.kind === 'ambiguo' || errorInfo.kind === 'generico') && (
          <Alert variant="danger">{errorInfo.message}</Alert>
        )}

        <div className={styles.acciones}>
          {(expedienteActivo || errorInfo?.kind === 'activo-existente' || errorInfo?.kind === 'ambiguo') && (
            <Button variant="secondary" onClick={() => navigate('/estudiante')}>
              Ir a mi panel
            </Button>
          )}
          {!perfil.perfil_validado && (
            <Button
              loading={perfilQuery.isFetching}
              variant="secondary"
              onClick={() => {
                setErrorInfo(null)
                void perfilQuery.refetch()
              }}
            >
              Volver a consultar
            </Button>
          )}
        </div>
      </>
    )
  }

  return (
    <div className={styles.page}>
      <Breadcrumbs items={[{ label: 'Inicio', to: '/estudiante' }, { label: 'Nueva solicitud' }]} />
      <header className={styles.header}>
        <p className={styles.eyebrow}>Trámite de titulación</p>
        <h1 className={styles.title}>Nueva solicitud de titulación</h1>
        <p className={styles.description}>
          Su carrera y facultad se obtienen de su información académica institucional. Solo puede tener un expediente
          activo a la vez.
        </p>
      </header>

      {renderContenido()}
    </div>
  )
}
