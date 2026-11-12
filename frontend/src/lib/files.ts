export const MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024

const PDF_MAGIC_BYTES = [0x25, 0x50, 0x44, 0x46, 0x2d]

export type FileValidationErrorCode =
  | 'INVALID_EXTENSION'
  | 'INVALID_MIME'
  | 'FILE_TOO_LARGE'
  | 'EMPTY_FILE'
  | 'INVALID_MAGIC_BYTES'

export type FileValidationResult =
  | { valid: true }
  | { valid: false; error: FileValidationErrorCode; message: string }

function hasValidExtension(file: File): boolean {
  return file.name.toLowerCase().endsWith('.pdf')
}

function hasValidMimeType(file: File): boolean {
  return file.type === 'application/pdf'
}

async function hasValidMagicBytes(file: File): Promise<boolean> {
  const header = await file.slice(0, PDF_MAGIC_BYTES.length).arrayBuffer()
  const bytes = new Uint8Array(header)

  if (bytes.length < PDF_MAGIC_BYTES.length) {
    return false
  }

  return PDF_MAGIC_BYTES.every((expected, index) => bytes[index] === expected)
}

/**
 * Validación de PDF en el cliente. No sustituye los controles de seguridad
 * del servidor: solo evita subidas evidentemente inválidas.
 */
export async function validatePdfFile(file: File): Promise<FileValidationResult> {
  if (!hasValidExtension(file)) {
    return { valid: false, error: 'INVALID_EXTENSION', message: 'El archivo debe tener extensión .pdf.' }
  }

  if (!hasValidMimeType(file)) {
    return { valid: false, error: 'INVALID_MIME', message: 'El archivo debe ser de tipo PDF.' }
  }

  if (file.size === 0) {
    return { valid: false, error: 'EMPTY_FILE', message: 'El archivo está vacío.' }
  }

  if (file.size > MAX_PDF_SIZE_BYTES) {
    return { valid: false, error: 'FILE_TOO_LARGE', message: 'El archivo debe pesar como máximo 10 MB.' }
  }

  if (!(await hasValidMagicBytes(file))) {
    return { valid: false, error: 'INVALID_MAGIC_BYTES', message: 'El archivo no parece ser un PDF válido.' }
  }

  return { valid: true }
}
