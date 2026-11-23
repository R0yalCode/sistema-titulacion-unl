import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { NuevaSolicitudForm } from './NuevaSolicitudForm'

function renderForm(props: Partial<Parameters<typeof NuevaSolicitudForm>[0]> = {}) {
  const onSubmit = props.onSubmit ?? vi.fn().mockResolvedValue(true)
  render(
    <NuevaSolicitudForm
      carreraNombre="Computación"
      serverError={null}
      submitting={false}
      {...props}
      onSubmit={onSubmit}
    />,
  )
  return { onSubmit }
}

describe('NuevaSolicitudForm (V-03, sin UUID)', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('no tiene ningún campo editable: ni UUID ni selector de carrera', () => {
    renderForm()
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.queryByText(/UUID/i)).not.toBeInTheDocument()
  })

  it('pide confirmación nombrando la carrera y luego envía', async () => {
    const user = userEvent.setup()
    const { onSubmit } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Iniciar trámite' }))
    const dialogo = await screen.findByRole('alertdialog')
    expect(dialogo).toHaveTextContent(/carrera Computación/)
    await user.click(within(dialogo).getByRole('button', { name: 'Iniciar trámite' }))

    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(onSubmit).toHaveBeenCalledWith()
  })

  it('no envía si el estudiante cancela la confirmación', async () => {
    const user = userEvent.setup()
    const { onSubmit } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Iniciar trámite' }))
    const dialogo = await screen.findByRole('alertdialog')
    await user.click(within(dialogo).getByRole('button', { name: /cancelar/i }))

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('durante el envío el botón queda en carga y no se reenvía', async () => {
    const user = userEvent.setup()
    const { onSubmit } = renderForm({ submitting: true })
    const boton = screen.getByRole('button', { name: /Iniciar trámite/ })
    expect(boton).toBeDisabled()
    await user.click(boton)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('muestra el error del servidor como alerta', () => {
    renderForm({ serverError: 'El servicio no respondió.' })
    expect(screen.getByRole('alert')).toHaveTextContent('El servicio no respondió.')
  })

  it('no tiene violaciones de accesibilidad', async () => {
    const { container } = render(
      <NuevaSolicitudForm carreraNombre="Computación" serverError="Error" submitting={false} onSubmit={vi.fn()} />,
    )
    expect(await axe(container)).toHaveNoViolations()
  })
})
