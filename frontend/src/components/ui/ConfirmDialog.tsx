import { useCallback, useRef, useState, type ReactNode } from 'react'
import { Button } from './Button'
import { Modal } from './Modal'
import styles from './ConfirmDialog.module.css'

export type ConfirmTone = 'primary' | 'danger'

export type ConfirmOptions = {
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  /** `danger` para operaciones destructivas o irreversibles. */
  tone?: ConfirmTone
}

type ConfirmDialogProps = ConfirmOptions & {
  open: boolean
  onConfirm: () => void
  onCancel: () => void
  /** Deshabilita ambas acciones mientras se procesa (evita dobles envíos). */
  busy?: boolean
}

/**
 * Confirmación accesible (sustituye a `window.confirm`): `alertdialog`, foco
 * inicial en "Cancelar" (la opción segura), Escape cancela y el foco vuelve al
 * elemento que la abrió (lo gestiona `Modal`).
 */
export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  tone = 'primary',
  busy = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Modal
      description={description}
      hideCloseButton
      open={open}
      role="alertdialog"
      size="sm"
      title={title}
      onClose={busy ? () => undefined : onCancel}
    >
      <div className={styles.actions}>
        <Button disabled={busy} variant="secondary" onClick={onCancel}>
          {cancelLabel}
        </Button>
        <Button loading={busy} variant={tone === 'danger' ? 'danger' : 'primary'} onClick={onConfirm}>
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  )
}

/**
 * `const { confirm, dialog } = useConfirm()`; renderizar `{dialog}` y usar
 * `if (!(await confirm({...}))) return`. Resuelve una sola vez por apertura,
 * por lo que un doble clic no confirma dos veces.
 */
export function useConfirm(): { confirm: (options: ConfirmOptions) => Promise<boolean>; dialog: ReactNode } {
  const [options, setOptions] = useState<ConfirmOptions | null>(null)
  const resolverRef = useRef<((value: boolean) => void) | null>(null)

  const settle = useCallback((value: boolean) => {
    const resolve = resolverRef.current
    resolverRef.current = null
    setOptions(null)
    resolve?.(value)
  }, [])

  const confirm = useCallback((next: ConfirmOptions) => {
    resolverRef.current?.(false)
    setOptions(next)
    return new Promise<boolean>((resolve) => {
      resolverRef.current = resolve
    })
  }, [])

  const dialog = (
    <ConfirmDialog
      {...options}
      open={options !== null}
      title={options?.title ?? ''}
      onCancel={() => settle(false)}
      onConfirm={() => settle(true)}
    />
  )

  return { confirm, dialog }
}
