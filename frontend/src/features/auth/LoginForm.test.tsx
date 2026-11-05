import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  it('no envía con campos vacíos y enfoca el usuario primero', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)

    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByLabelText(/^Usuario/)).toHaveFocus()
    expect(screen.getByText('Ingrese su usuario.')).toBeInTheDocument()
  })

  it('enfoca la contraseña cuando solo falta ese campo', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/^Usuario/), 'estudiante.demo')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByLabelText(/^Contraseña/)).toHaveFocus()
    expect(screen.getByText('Ingrese su contraseña.')).toBeInTheDocument()
  })

  it('recorta espacios del usuario pero conserva la contraseña exacta', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/^Usuario/), '  estudiante.demo  ')
    await user.type(screen.getByLabelText(/^Contraseña/), '  demo-valida  ')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(onSubmit).toHaveBeenCalledWith({ username: 'estudiante.demo', password: '  demo-valida  ' })
  })

  it('envía el formulario al presionar Enter', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/^Usuario/), 'estudiante.demo')
    await user.type(screen.getByLabelText(/^Contraseña/), 'demo-valida{Enter}')

    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('muestra y oculta la contraseña con el botón de alternancia', async () => {
    const user = userEvent.setup()
    render(<LoginForm serverError={null} submitting={false} onSubmit={vi.fn().mockResolvedValue(true)} />)

    const passwordInput = screen.getByLabelText(/^Contraseña/)
    expect(passwordInput).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }))
    expect(passwordInput).toHaveAttribute('type', 'text')

    await user.click(screen.getByRole('button', { name: 'Ocultar contraseña' }))
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('no permite un segundo envío mientras el primero está en curso', () => {
    const onSubmit = vi.fn().mockResolvedValue(true)
    const { container } = render(<LoginForm serverError={null} submitting onSubmit={onSubmit} />)

    expect(screen.getByRole('button', { name: 'Ingresar' })).toBeDisabled()

    // El botón deshabilitado ya evita el clic, pero el handler también
    // ignora un evento submit directo (p. ej. disparado por Enter) mientras
    // `submitting` sea true, como segunda barrera contra el doble envío.
    const form = container.querySelector('form') as HTMLFormElement
    fireEvent.submit(form)

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('al recibir un error del servidor limpia y reenfoca la contraseña', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(false)
    render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/^Usuario/), 'estudiante.demo')
    await user.type(screen.getByLabelText(/^Contraseña/), 'incorrecta')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    const passwordInput = await screen.findByLabelText(/^Contraseña/)
    expect(passwordInput).toHaveValue('')
    expect(passwordInput).toHaveFocus()
  })

  it('muestra el mensaje de error del servidor', () => {
    render(<LoginForm serverError="Usuario o contraseña incorrectos." submitting={false} onSubmit={vi.fn()} />)

    expect(screen.getByRole('alert')).toHaveTextContent('Usuario o contraseña incorrectos.')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(
      <LoginForm serverError="Usuario o contraseña incorrectos." submitting={false} onSubmit={vi.fn()} />,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
