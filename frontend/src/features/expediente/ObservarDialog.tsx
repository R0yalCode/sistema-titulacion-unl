import { useState } from 'react'
import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import styles from './ObservarDialog.module.css'

type ObservarDialogProps = {
  open: boolean
  peticiones: PeticionInicializada[]
  submitting: boolean
  error: string | null
  onClose: () => void
  onConfirm: (payload: { motivo_observacion: string; peticion_id?: string }) => void
}

export function ObservarDialog({ open, peticiones, submitting, error, onClose, onConfirm }: ObservarDialogProps) {
  const [motivo, setMotivo] = useState('')
  const [peticionId, setPeticionId] = useState('')
  const [fieldError, setFieldError] = useState<string | null>(null)

  function handleSubmit() {
    if (!motivo.trim()) {
      setFieldError('Ingrese el motivo de la observación.')
      return
    }
    setFieldError(null)
    onConfirm({ motivo_observacion: motivo.trim(), peticion_id: peticionId || undefined })
  }

  return (
    <Modal onClose={onClose} open={open} title="Registrar observación">
      <div className={styles.body}>
        <Select
          hint="Opcional: seleccione la petición observada, si corresponde a una en particular."
          label="Petición"
          options={peticiones.map((peticion) => ({ value: peticion.id, label: peticion.requisito_nombre }))}
          placeholder="Sin petición específica"
          value={peticionId}
          onChange={(event) => setPeticionId(event.target.value)}
        />
        <Textarea
          error={fieldError ?? undefined}
          label="Motivo de la observación"
          required
          value={motivo}
          onChange={(event) => setMotivo(event.target.value)}
        />
        {error && <Alert variant="danger">{error}</Alert>}
        <div className={styles.actions}>
          <Button loading={submitting} onClick={handleSubmit}>
            Confirmar observación
          </Button>
          <Button disabled={submitting} variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
        </div>
      </div>
    </Modal>
  )
}
