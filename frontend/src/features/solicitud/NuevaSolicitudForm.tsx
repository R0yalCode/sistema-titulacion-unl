import { useState, type FormEvent } from 'react'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import styles from './NuevaSolicitudForm.module.css'

const CARRERA_ID_FIELD_ID = 'nueva-solicitud-carrera-id'
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export function isValidCarreraId(value: string): boolean {
  return UUID_PATTERN.test(value.trim())
}

export type NuevaSolicitudFormProps = {
  initialCarreraId: string
  submitting: boolean
  serverError: string | null
  onCarreraIdChange: (value: string) => void
  onSubmit: (carreraId: string) => Promise<boolean>
}

export function NuevaSolicitudForm({
  initialCarreraId,
  submitting,
  serverError,
  onCarreraIdChange,
  onSubmit,
}: NuevaSolicitudFormProps) {
  const [carreraId, setCarreraId] = useState(initialCarreraId)
  const [fieldError, setFieldError] = useState<string | undefined>(undefined)

  function handleChange(value: string) {
    setCarreraId(value)
    onCarreraIdChange(value)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) {
      return
    }

    const trimmed = carreraId.trim()
    if (!trimmed) {
      setFieldError('Ingrese el identificador (UUID) de su carrera.')
      document.getElementById(CARRERA_ID_FIELD_ID)?.focus()
      return
    }
    if (!isValidCarreraId(trimmed)) {
      setFieldError('El identificador debe tener el formato UUID, por ejemplo: 11111111-1111-1111-1111-111111111111.')
      document.getElementById(CARRERA_ID_FIELD_ID)?.focus()
      return
    }
    setFieldError(undefined)

    const confirmado = window.confirm(
      '¿Confirma el envío de la solicitud de titulación con este identificador de carrera? Solo puede tener un expediente activo a la vez.',
    )
    if (!confirmado) {
      return
    }

    await onSubmit(trimmed)
  }

  return (
    <form className={styles.form} noValidate onSubmit={handleSubmit}>
      <Input
        disabled={submitting}
        error={fieldError}
        hint="Use el identificador (UUID) de su carrera proporcionado por la institución. No existe todavía un catálogo de carreras en el sistema."
        id={CARRERA_ID_FIELD_ID}
        label="Identificador de carrera (UUID)"
        name="carrera_id"
        placeholder="11111111-1111-1111-1111-111111111111"
        required
        value={carreraId}
        onChange={(event) => handleChange(event.target.value)}
      />

      {serverError && <Alert variant="danger">{serverError}</Alert>}

      <Button loading={submitting} type="submit">
        Enviar solicitud
      </Button>
    </form>
  )
}
