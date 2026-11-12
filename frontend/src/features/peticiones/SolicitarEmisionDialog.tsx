import type { PeticionInicializada } from '@/api/endpoints/expedientes'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import styles from './PeticionDialog.module.css'

type SolicitarEmisionDialogProps = {
  peticion: PeticionInicializada | null
  submitting: boolean
  error: string | null
  onClose: () => void
  onConfirm: (peticion: PeticionInicializada) => void
}

/** FE-T502: confirmación explícita antes de `POST /solicitar-emision/`. */
export function SolicitarEmisionDialog({ peticion, submitting, error, onClose, onConfirm }: SolicitarEmisionDialogProps) {
  return (
    <Modal onClose={onClose} open={peticion !== null} title="Solicitar emisión">
      {peticion && (
        <div className={styles.body}>
          <p>
            Se solicitará a <strong>{peticion.dependencia_emisora}</strong> la emisión del documento «
            {peticion.requisito_nombre}». La petición pasará al estado <strong>Solicitado</strong>.
          </p>
          {error && <Alert variant="danger">{error}</Alert>}
          <div className={styles.actions}>
            <Button loading={submitting} onClick={() => onConfirm(peticion)}>
              Confirmar solicitud
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
