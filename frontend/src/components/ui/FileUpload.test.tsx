import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { describe, expect, it, vi } from 'vitest'
import { FileUpload } from './FileUpload'

function makePdf(name: string, size = 100): File {
  const buffer = new ArrayBuffer(size)
  const view = new Uint8Array(buffer)
  const header = [0x25, 0x50, 0x44, 0x46, 0x2d]
  header.forEach((byte, index) => {
    view[index] = byte
  })
  return new File([buffer], name, { type: 'application/pdf' })
}

describe('FileUpload', () => {
  it('acepta un PDF válido: llama a onFileSelected y muestra nombre/tamaño', async () => {
    const user = userEvent.setup()
    const onFileSelected = vi.fn()
    const { container } = render(<FileUpload label="Documento" onFileSelected={onFileSelected} />)

    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, makePdf('expediente.pdf'))

    expect(onFileSelected).toHaveBeenCalledOnce()
    expect(await screen.findByText(/expediente\.pdf/)).toBeInTheDocument()
  })

  it('rechaza un archivo inválido antes de entregarlo al consumidor y muestra el error', async () => {
    const user = userEvent.setup()
    const onFileSelected = vi.fn()
    const { container } = render(<FileUpload label="Documento" onFileSelected={onFileSelected} />)

    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    // Extensión/MIME correctos (para que userEvent.upload no lo filtre por el
    // atributo accept) pero sin los magic bytes %PDF-: debe rechazarlo igual.
    const invalidFile = new File(['no es realmente un pdf'], 'documento.pdf', { type: 'application/pdf' })
    await user.upload(input, invalidFile)

    expect(await screen.findByRole('alert')).toHaveTextContent('no parece ser un PDF válido')
    expect(onFileSelected).not.toHaveBeenCalled()
  })

  it('es operable por teclado a través del botón "Seleccionar archivo"', async () => {
    const user = userEvent.setup()
    render(<FileUpload label="Documento" onFileSelected={() => undefined} />)

    await user.tab()
    expect(screen.getByRole('button', { name: 'Seleccionar archivo' })).toHaveFocus()
  })

  it('no presenta violaciones de accesibilidad', async () => {
    const { container } = render(<FileUpload hint="PDF, máximo 10 MB." label="Documento" onFileSelected={() => undefined} />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('acepta un PDF soltado por arrastrar y soltar (drag & drop)', async () => {
    const onFileSelected = vi.fn()
    render(<FileUpload label="Documento" onFileSelected={onFileSelected} />)

    const dropzone = screen.getByText('Arrastre un archivo PDF aquí o').parentElement as HTMLElement
    const file = makePdf('arrastrado.pdf')

    fireEvent.dragOver(dropzone, { dataTransfer: { files: [file] } })
    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } })

    expect(await screen.findByText(/arrastrado\.pdf/)).toBeInTheDocument()
    expect(onFileSelected).toHaveBeenCalledOnce()
  })

  it('quita el estado "sobre la zona" al salir con dragLeave sin soltar', () => {
    render(<FileUpload label="Documento" onFileSelected={() => undefined} />)

    const dropzone = screen.getByText('Arrastre un archivo PDF aquí o').parentElement as HTMLElement
    fireEvent.dragOver(dropzone, { dataTransfer: { files: [] } })
    fireEvent.dragLeave(dropzone)

    expect(dropzone.className).not.toMatch(/dropzoneActive/)
  })
})
