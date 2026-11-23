import type { FormEvent } from 'react'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { useConfirm } from '@/components/ui/ConfirmDialog'
import styles from './NuevaSolicitudForm.module.css'

export type NuevaSolicitudFormProps = {
  /** Carrera del perfil validado, solo para el texto de confirmación. */
  carreraNombre: string
  submitting: boolean
  serverError: string | null
  onSubmit: () => Promise<boolean>
}

/**
 * Confirmación del inicio del trámite (V-03). No tiene campos: el backend
 * toma la carrera y la facultad del perfil académico validado.
 */
export function NuevaSolicitudForm({ carreraNombre, submitting, serverError, onSubmit }: NuevaSolicitudFormProps) {
  const { confirm, dialog } = useConfirm()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }
    const confirmado = await confirm({
      title: '¿Iniciar el trámite de titulación?',
      description: `Se creará su expediente para la carrera ${carreraNombre}, según su información académica. Solo puede tener un expediente activo a la vez.`,
      confirmLabel: 'Iniciar trámite',
    })
    if (!confirmado) {
      return
    }
    await onSubmit()
  }

  return (
    <form aria-label="Iniciar trámite de titulación" className={styles.form} noValidate onSubmit={handleSubmit}>
      {dialog}
      <p className={styles.texto}>
        Revise que sus datos académicos sean correctos. Si algo no corresponde, no inicie el trámite y comuníquese con la
        Secretaría de su carrera.
      </p>

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <div>
        <Button loading={submitting} type="submit">
          Iniciar trámite
        </Button>
      </div>
    </form>
  )
}
