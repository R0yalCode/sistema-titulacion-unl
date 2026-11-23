import { useState } from 'react'
import type { UseQueryResult } from '@tanstack/react-query'
import type { ChecklistItem } from '@/api/endpoints/checklist'
import type { ApiRequestError } from '@/api/errors'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { useConfirm } from '@/components/ui/ConfirmDialog'
import { ErrorState } from '@/components/ui/ErrorState'
import { FileUpload } from '@/components/ui/FileUpload'
import { ForbiddenState } from '@/components/ui/ForbiddenState'
import { Skeleton } from '@/components/ui/Skeleton'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Textarea } from '@/components/ui/Textarea'
import { presentApiError } from '@/lib/apiErrorPresentation'
import { puedeEvaluarItem, puedeSubsanarItem, puedeVerChecklist } from './accionesPorRolEstado'
import { describeAccionError } from './errors'
import { useEvaluarChecklist, useSubsanarChecklist } from './queries'
import styles from './ChecklistSection.module.css'

type ChecklistSectionProps = {
  query: UseQueryResult<ChecklistItem[], ApiRequestError>
  roles: string[]
  estadoExpediente: EstadoExpediente
  esPropietario: boolean
  expedienteId: string
}

export function ChecklistSection({ query, roles, estadoExpediente, esPropietario, expedienteId }: ChecklistSectionProps) {
  if (!puedeVerChecklist(roles)) {
    return (
      <ForbiddenState
        description="El checklist de verificación no está disponible para su rol."
        title="No disponible para su rol"
      />
    )
  }

  if (query.isError) {
    const presentation = presentApiError(query.error)
    if (presentation.kind === 'forbidden') {
      return <ForbiddenState description={presentation.description} title={presentation.title} />
    }
    return (
      <ErrorState
        description={presentation.description}
        title={presentation.title}
        onRetry={() => query.refetch()}
      />
    )
  }

  if (query.isLoading) {
    return <Skeleton count={3} label="Cargando checklist…" />
  }

  const items = query.data ?? []
  if (items.length === 0) {
    return <p className={styles.empty}>Este expediente no tiene checklist registrado todavía.</p>
  }

  return (
    <ul className={styles.list}>
      {items.map((item) => (
        <ChecklistRow
          esPropietario={esPropietario}
          estadoExpediente={estadoExpediente}
          expedienteId={expedienteId}
          item={item}
          key={item.id}
          roles={roles}
        />
      ))}
    </ul>
  )
}

type ChecklistRowProps = {
  item: ChecklistItem
  roles: string[]
  estadoExpediente: EstadoExpediente
  esPropietario: boolean
  expedienteId: string
}

function ChecklistRow({ item, roles, estadoExpediente, esPropietario, expedienteId }: ChecklistRowProps) {
  const [observando, setObservando] = useState(false)
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState<string | null>(null)
  const evaluarMutation = useEvaluarChecklist(expedienteId)
  const subsanarMutation = useSubsanarChecklist(expedienteId)
  const { confirm, dialog } = useConfirm()

  const puedeEvaluar = puedeEvaluarItem(roles, estadoExpediente, item.estado_verificacion)
  const puedeSubsanar = puedeSubsanarItem(roles, estadoExpediente, item.estado_verificacion, esPropietario)

  async function handleVerificar() {
    const confirmado = await confirm({
      title: '¿Marcar como verificado?',
      description: `El requisito "${item.requisito_nombre}" quedará como VERIFICADO.`,
      confirmLabel: 'Marcar como verificado',
    })
    if (!confirmado) {
      return
    }
    setError(null)
    try {
      await evaluarMutation.mutateAsync({ id: item.id, payload: { estado_verificacion: 'VERIFICADO' } })
    } catch (mutationError) {
      setError(describeAccionError(mutationError))
    }
  }

  async function handleObservar() {
    if (!motivo.trim()) {
      setError('Ingrese el motivo de la observación.')
      return
    }
    setError(null)
    try {
      await evaluarMutation.mutateAsync({
        id: item.id,
        payload: { estado_verificacion: 'OBSERVADO', motivo_observacion: motivo.trim() },
      })
      setObservando(false)
      setMotivo('')
    } catch (mutationError) {
      setError(describeAccionError(mutationError))
    }
  }

  async function handleSubsanar(archivo: File) {
    setError(null)
    try {
      await subsanarMutation.mutateAsync({ id: item.id, archivo })
    } catch (mutationError) {
      setError(describeAccionError(mutationError))
    }
  }

  return (
    <li className={`${styles.item} ${item.estado_verificacion === 'OBSERVADO' ? styles.observado : ''}`}>
      {dialog}
      <div className={styles.itemHeader}>
        <strong className={styles.nombre}>{item.requisito_nombre}</strong>
        <StatusBadge dominio="checklist" valor={item.estado_verificacion} />
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {puedeEvaluar && !observando && (
        <div className={styles.actions}>
          <Button loading={evaluarMutation.isPending} size="sm" onClick={() => void handleVerificar()}>
            Verificar
          </Button>
          <Button size="sm" variant="secondary" onClick={() => setObservando(true)}>
            Observar
          </Button>
        </div>
      )}

      {puedeEvaluar && observando && (
        <div className={styles.observarForm}>
          <Textarea
            label="Motivo de la observación"
            required
            value={motivo}
            onChange={(event) => setMotivo(event.target.value)}
          />
          <div className={styles.actions}>
            <Button loading={evaluarMutation.isPending} size="sm" onClick={() => void handleObservar()}>
              Confirmar observación
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setObservando(false)}>
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {puedeSubsanar && (
        <FileUpload
          hint="PDF, máximo 10 MB."
          label="Subsanar con un nuevo documento"
          onFileSelected={(file) => void handleSubsanar(file)}
        />
      )}
    </li>
  )
}
