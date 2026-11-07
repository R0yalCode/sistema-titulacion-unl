import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { isValidCarreraId, NuevaSolicitudForm } from './NuevaSolicitudForm'

const VALID_UUID = '11111111-1111-1111-1111-111111111111'

describe('isValidCarreraId', () => {
  it('acepta un UUID con el formato canónico', () => {
    expect(isValidCarreraId(VALID_UUID)).toBe(true)
  })

  it('rechaza cadenas que no son UUID', () => {
    expect(isValidCarreraId('no-es-un-uuid')).toBe(false)
    expect(isValidCarreraId('11111111-1111-1111-1111-11111111111')).toBe(false)
    expect(isValidCarreraId('')).toBe(false)
  })
})

describe('NuevaSolicitudForm', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('no envía con el campo vacío y enfoca el campo', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError={null}
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText('Ingrese el identificador (UUID) de su carrera.')).toBeInTheDocument()
    expect(screen.getByLabelText(/^Identificador de carrera/)).toHaveFocus()
  })

  it('rechaza un UUID con formato inválido', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError={null}
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    await user.type(screen.getByLabelText(/^Identificador de carrera/), 'no-es-un-uuid')
    await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText(/debe tener el formato UUID/i)).toBeInTheDocument()
  })

  it('pide confirmación antes de enviar y envía si se acepta', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError={null}
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    await user.type(screen.getByLabelText(/^Identificador de carrera/), VALID_UUID)
    await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))

    expect(window.confirm).toHaveBeenCalledTimes(1)
    expect(onSubmit).toHaveBeenCalledWith(VALID_UUID)
  })

  it('no envía si se cancela la confirmación', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(true)
    render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError={null}
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    await user.type(screen.getByLabelText(/^Identificador de carrera/), VALID_UUID)
    await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('notifica los cambios del campo para el borrador local', async () => {
    const user = userEvent.setup()
    const onCarreraIdChange = vi.fn()
    render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError={null}
        submitting={false}
        onCarreraIdChange={onCarreraIdChange}
        onSubmit={vi.fn().mockResolvedValue(true)}
      />,
    )

    await user.type(screen.getByLabelText(/^Identificador de carrera/), '1')

    expect(onCarreraIdChange).toHaveBeenCalledWith('1')
  })

  it('restaura el valor inicial (borrador restaurado)', () => {
    render(
      <NuevaSolicitudForm
        initialCarreraId={VALID_UUID}
        serverError={null}
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )

    expect(screen.getByLabelText(/^Identificador de carrera/)).toHaveValue(VALID_UUID)
  })

  it('no permite un segundo envío mientras el primero está en curso', () => {
    const onSubmit = vi.fn()
    const { container } = render(
      <NuevaSolicitudForm
        initialCarreraId={VALID_UUID}
        serverError={null}
        submitting
        onCarreraIdChange={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    expect(screen.getByRole('button', { name: 'Enviar solicitud' })).toBeDisabled()

    fireEvent.submit(container.querySelector('form') as HTMLFormElement)

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('muestra el mensaje de error del servidor', () => {
    render(
      <NuevaSolicitudForm
        initialCarreraId={VALID_UUID}
        serverError="El estudiante ya posee un expediente activo."
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('El estudiante ya posee un expediente activo.')
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(
      <NuevaSolicitudForm
        initialCarreraId=""
        serverError="Error de ejemplo."
        submitting={false}
        onCarreraIdChange={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
