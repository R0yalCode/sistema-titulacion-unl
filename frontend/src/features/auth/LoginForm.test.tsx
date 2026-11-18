import { fireEvent, render as rtlRender, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { LoginForm } from './LoginForm'

// LoginForm enlaza a las páginas de restablecimiento con <Link>: requiere un router.
function render(ui: ReactElement) {
  return rtlRender(ui, { wrapper: MemoryRouter })
}

const USUARIO = /^Nombre de usuario/
const ENTRAR = { name: 'Iniciar sesión' }
const REQUERIDO_USUARIO = 'El nombre de usuario es un campo requerido.'
const REQUERIDA_CLAVE = 'La contraseña es un campo requerido.'
const DOMINIO = 'Ingrese un correo institucional válido (@unl.edu.ec).'

function renderForm(onSubmit = vi.fn().mockResolvedValue(true)) {
  render(<LoginForm serverError={null} submitting={false} onSubmit={onSubmit} />)
  return onSubmit
}

describe('LoginForm (correo institucional, mensajes del SAC)', () => {
  it('no muestra errores antes de interactuar', () => {
    renderForm()

    expect(screen.queryByText(REQUERIDO_USUARIO)).not.toBeInTheDocument()
    expect(screen.queryByText(REQUERIDA_CLAVE)).not.toBeInTheDocument()
    expect(screen.getByLabelText(USUARIO)).not.toHaveAttribute('aria-invalid')
  })

  it('con ambos campos vacíos muestra los mensajes exactos y marca los campos', async () => {
    const user = userEvent.setup()
    const onSubmit = renderForm()

    await user.click(screen.getByRole('button', ENTRAR))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText(REQUERIDO_USUARIO)).toBeInTheDocument()
    expect(screen.getByText(REQUERIDA_CLAVE)).toBeInTheDocument()
    expect(screen.getByLabelText(USUARIO)).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText(/^Contraseña/)).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText(USUARIO)).toHaveFocus()
    // El mensaje queda asociado al campo (debajo de él).
    expect(screen.getByLabelText(USUARIO)).toHaveAccessibleDescription(REQUERIDO_USUARIO)
  })

  it.each(['juan_perez@gmail.com', 'juan_perez@hotmail.com', 'juan_perez@unl.edu', 'juan_perez'])(
    'rechaza %s con el mensaje de dominio',
    async (valor) => {
      const user = userEvent.setup()
      const onSubmit = renderForm()

      await user.type(screen.getByLabelText(USUARIO), valor)
      await user.type(screen.getByLabelText(/^Contraseña/), 'clave')
      await user.click(screen.getByRole('button', ENTRAR))

      expect(onSubmit).not.toHaveBeenCalled()
      expect(screen.getByText(DOMINIO)).toBeInTheDocument()
    },
  )

  it('normaliza espacios y mayúsculas y conserva la contraseña exacta', async () => {
    const user = userEvent.setup()
    const onSubmit = renderForm()

    await user.type(screen.getByLabelText(USUARIO), '  Juan_Perez@UNL.edu.EC  ')
    await user.type(screen.getByLabelText(/^Contraseña/), '  Clave Exacta  ')
    await user.click(screen.getByRole('button', ENTRAR))

    expect(onSubmit).toHaveBeenCalledWith({ email: 'juan_perez@unl.edu.ec', password: '  Clave Exacta  ' })
  })

  it('el error desaparece al corregir el valor', async () => {
    const user = userEvent.setup()
    renderForm()

    await user.click(screen.getByRole('button', ENTRAR))
    await user.type(screen.getByLabelText(USUARIO), 'juan_perez@unl.edu.ec')
    await user.type(screen.getByLabelText(/^Contraseña/), 'x')

    expect(screen.queryByText(REQUERIDO_USUARIO)).not.toBeInTheDocument()
    expect(screen.queryByText(DOMINIO)).not.toBeInTheDocument()
    expect(screen.queryByText(REQUERIDA_CLAVE)).not.toBeInTheDocument()
    expect(screen.getByLabelText(USUARIO)).not.toHaveAttribute('aria-invalid')
  })

  it('enfoca la contraseña cuando solo falta ese campo', async () => {
    const user = userEvent.setup()
    const onSubmit = renderForm()

    await user.type(screen.getByLabelText(USUARIO), 'juan_perez@unl.edu.ec')
    await user.click(screen.getByRole('button', ENTRAR))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByLabelText(/^Contraseña/)).toHaveFocus()
    expect(screen.getByText(REQUERIDA_CLAVE)).toBeInTheDocument()
  })

  it('envía el formulario al presionar Enter', async () => {
    const user = userEvent.setup()
    const onSubmit = renderForm()

    await user.type(screen.getByLabelText(USUARIO), 'juan_perez@unl.edu.ec')
    await user.type(screen.getByLabelText(/^Contraseña/), 'clave{Enter}')

    expect(onSubmit).toHaveBeenCalledOnce()
  })

  it('muestra y oculta la contraseña con el botón de alternancia', async () => {
    const user = userEvent.setup()
    renderForm()
    const password = screen.getByLabelText(/^Contraseña/)

    expect(password).toHaveAttribute('type', 'password')
    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }))
    expect(password).toHaveAttribute('type', 'text')
  })

  it('deshabilita el botón y no envía dos veces mientras procesa', () => {
    const onSubmit = vi.fn()
    const { container } = render(<LoginForm serverError={null} submitting onSubmit={onSubmit} />)

    expect(screen.getByRole('button', ENTRAR)).toBeDisabled()
    fireEvent.submit(container.querySelector('form') as HTMLFormElement)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('tras un error del servidor limpia y reenfoca la contraseña', async () => {
    const user = userEvent.setup()
    renderForm(vi.fn().mockResolvedValue(false))

    await user.type(screen.getByLabelText(USUARIO), 'juan_perez@unl.edu.ec')
    await user.type(screen.getByLabelText(/^Contraseña/), 'incorrecta')
    await user.click(screen.getByRole('button', ENTRAR))

    const passwordInput = await screen.findByLabelText(/^Contraseña/)
    expect(passwordInput).toHaveValue('')
    expect(passwordInput).toHaveFocus()
  })

  it('ofrece restablecer la contraseña y el doble factor (2FA)', () => {
    renderForm()

    expect(screen.getByRole('link', { name: /Restablecer contraseña/ })).toHaveAttribute('href', '/recuperar-contrasena')
    expect(screen.getByRole('link', { name: /Restablecer doble factor de autenticación \(2FA\)/ })).toHaveAttribute(
      'href',
      '/restablecer-2fa',
    )
  })

  it('no presenta violaciones de accesibilidad con errores visibles', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <LoginForm serverError="Usuario o contraseña incorrectos." submitting={false} onSubmit={vi.fn()} />,
    )
    await user.click(screen.getByRole('button', ENTRAR))

    expect(await axe(container)).toHaveNoViolations()
  })
})
