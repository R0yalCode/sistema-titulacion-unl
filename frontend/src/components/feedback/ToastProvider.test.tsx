import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useContext } from 'react'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { ToastContext, ToastProvider } from './ToastProvider'

function Consumer() {
  const toast = useContext(ToastContext)

  return (
    <div>
      <button onClick={() => toast?.showToast('Expediente enviado correctamente.', 'success')} type="button">
        Disparar éxito
      </button>
      <button onClick={() => toast?.showToast('No se pudo enviar el expediente.', 'danger')} type="button">
        Disparar error
      </button>
    </div>
  )
}

describe('ToastProvider', () => {
  it('muestra un toast con role="status" para variantes no críticas', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))

    expect(screen.getByRole('status')).toHaveTextContent('Expediente enviado correctamente.')
  })

  it('muestra un toast con role="alert" para variantes críticas', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar error' }))

    expect(screen.getByRole('alert')).toHaveTextContent('No se pudo enviar el expediente.')
  })

  it('se cierra automáticamente al vencer el plazo configurado', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider autoDismissMs={30}>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))
    expect(screen.getByRole('status')).toBeInTheDocument()

    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument())
  })

  it('se puede cerrar manualmente antes del cierre automático', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))
    await user.click(screen.getByRole('button', { name: 'Cerrar notificación' }))

    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('no duplica el mismo mensaje si ya está en cola', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))
    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))

    expect(screen.getAllByText('Expediente enviado correctamente.')).toHaveLength(1)
  })

  it('no bloquea la interacción con el resto de la página', async () => {
    const user = userEvent.setup()
    render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))
    await user.click(screen.getByRole('button', { name: 'Disparar error' }))

    expect(screen.getByRole('alert')).toHaveTextContent('No se pudo enviar el expediente.')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const user = userEvent.setup()
    const { baseElement } = render(
      <ToastProvider>
        <Consumer />
      </ToastProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'Disparar éxito' }))

    expect(await axe(baseElement)).toHaveNoViolations()
  })
})
