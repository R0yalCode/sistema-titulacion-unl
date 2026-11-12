import { describe, expect, it } from 'vitest'
import { MAX_PDF_SIZE_BYTES, validatePdfFile } from './files'

function makePdfBytes(size: number): ArrayBuffer {
  const buffer = new ArrayBuffer(size)
  const view = new Uint8Array(buffer)
  const header = [0x25, 0x50, 0x44, 0x46, 0x2d] // %PDF-
  header.forEach((byte, index) => {
    view[index] = byte
  })
  return buffer
}

function makeFile(name: string, bytes: ArrayBuffer, type: string): File {
  return new File([bytes], name, { type })
}

describe('validatePdfFile', () => {
  it('acepta un PDF válido (extensión, MIME, tamaño y magic bytes correctos)', async () => {
    const file = makeFile('expediente.pdf', makePdfBytes(100), 'application/pdf')

    expect(await validatePdfFile(file)).toEqual({ valid: true })
  })

  it('rechaza una extensión distinta de .pdf', async () => {
    const file = makeFile('expediente.docx', makePdfBytes(100), 'application/pdf')

    const result = await validatePdfFile(file)
    expect(result).toMatchObject({ valid: false, error: 'INVALID_EXTENSION' })
  })

  it('rechaza un MIME distinto de application/pdf', async () => {
    const file = makeFile('expediente.pdf', makePdfBytes(100), 'image/png')

    const result = await validatePdfFile(file)
    expect(result).toMatchObject({ valid: false, error: 'INVALID_MIME' })
  })

  it('rechaza un archivo vacío', async () => {
    const file = makeFile('expediente.pdf', new ArrayBuffer(0), 'application/pdf')

    const result = await validatePdfFile(file)
    expect(result).toMatchObject({ valid: false, error: 'EMPTY_FILE' })
  })

  it('rechaza un archivo de más de 10 MB', async () => {
    const file = makeFile('expediente.pdf', makePdfBytes(MAX_PDF_SIZE_BYTES + 1), 'application/pdf')

    const result = await validatePdfFile(file)
    expect(result).toMatchObject({ valid: false, error: 'FILE_TOO_LARGE' })
  })

  it('rechaza un archivo con extensión/MIME de PDF pero sin los magic bytes %PDF-', async () => {
    const file = makeFile('expediente.pdf', new ArrayBuffer(100), 'application/pdf')

    const result = await validatePdfFile(file)
    expect(result).toMatchObject({ valid: false, error: 'INVALID_MAGIC_BYTES' })
  })
})
