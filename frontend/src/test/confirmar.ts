import { screen, within } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'

/**
 * Acepta el diálogo de confirmación accesible (`ConfirmDialog`, rol
 * `alertdialog`) que sustituyó a `window.confirm`: pulsa su botón de
 * confirmación (el último del diálogo).
 */
export async function confirmarDialogo(user: UserEvent) {
  const dialogo = await screen.findByRole('alertdialog')
  const botones = within(dialogo).getAllByRole('button')
  await user.click(botones[botones.length - 1] as HTMLElement)
}
