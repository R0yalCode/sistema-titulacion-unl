import { useState } from 'react'
import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { FileUpload } from '@/components/ui/FileUpload'
import { Modal } from '@/components/ui/Modal'
import styles from './PeticionDialog.module.css'

type CargarDocumentoDialogProps = {
  peticion: PeticionInicializada | null
  submitting: boolean
  error: string | null
  onClose: () => void
  onConfirm: (peticion: PeticionInicializada, archivo: File) => void
}

/**
 * FE-T503: carga de un PDF validado en el cliente (`lib/files`: extensión,
 * MIME, tamaño ≤ 10 MB y magic bytes). Un archivo inválido nunca se envía.
 * El cliente usa `fetch`, que no expone el progreso de subida: se muestra el
 * estado "Subiendo…" del botón en lugar de un porcentaje inventado.
 */
export function CargarDocumentoDialog({ peticion, submitting, error, onClose, onConfirm }: CargarDocumentoDialogProps) {
  const [archivo, setArchivo] = useState<File | null>(null)

  return (
    <Modal onClose={onClose} open={peticion !== null} title="Cargar documento">
      {peticion && (
        <div className={styles.body}>
          <p>
            Documento para el requisito <strong>{peticion.requisito_nombre}</strong>. Si ya existe un documento,
            se registrará como una nueva versión vigente.
          </p>
          <FileUpload
            hint="Solo archivos PDF de hasta 10 MB."
            label="Documento PDF"
            onFileSelected={setArchivo}
            onInvalidFile={() => setArchivo(null)}
          />
          {error && <Alert variant="danger">{error}</Alert>}
          <div className={styles.actions}>
            <Button
              disabled={archivo === null}
              loading={submitting}
              onClick={() => archivo && onConfirm(peticion, archivo)}
            >
              {submitting ? 'Subiendo…' : 'Cargar documento'}
            </Button>
            <Button disabled={submitting} variant="ghost" onClick={onClose}>
              Cancelar
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}
