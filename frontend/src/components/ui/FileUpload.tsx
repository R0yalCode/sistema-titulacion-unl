import { useId, useRef, useState, type ChangeEvent, type DragEvent } from 'react'
import { validatePdfFile } from '@/lib/files'
import { Button } from './Button'
import styles from './FileUpload.module.css'

export type FileUploadProps = {
  label: string
  hint?: string
  onFileSelected: (file: File) => void
  /** Se invoca cuando el archivo elegido no supera la validación, para que el consumidor descarte uno previo. */
  onInvalidFile?: (message: string) => void
}

function formatSize(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export function FileUpload({ label, hint, onFileSelected, onInvalidFile }: FileUploadProps) {
  const inputId = useId()
  const errorId = `${inputId}-error`
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  async function handleFile(file: File) {
    const result = await validatePdfFile(file)

    if (!result.valid) {
      setError(result.message)
      setSelectedFile(null)
      onInvalidFile?.(result.message)
      return
    }

    setError(null)
    setSelectedFile(file)
    onFileSelected(file)
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (file) {
      void handleFile(file)
    }
    event.target.value = ''
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setIsDragOver(false)
    const file = event.dataTransfer.files[0]
    if (file) {
      void handleFile(file)
    }
  }

  return (
    <div className={styles.field}>
      <span className={styles.label} id={`${inputId}-label`}>
        {label}
      </span>
      {hint && <p className={styles.hint}>{hint}</p>}
      <div
        className={[styles.dropzone, isDragOver && styles.dropzoneActive].filter(Boolean).join(' ')}
        onDragLeave={() => setIsDragOver(false)}
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragOver(true)
        }}
        onDrop={handleDrop}
      >
        <p>Arrastre un archivo PDF aquí o</p>
        <Button aria-describedby={error ? errorId : undefined} onClick={() => inputRef.current?.click()} size="sm" variant="secondary">
          Seleccionar archivo
        </Button>
        <input
          accept="application/pdf,.pdf"
          aria-hidden="true"
          className="sr-only"
          id={inputId}
          onChange={handleInputChange}
          ref={inputRef}
          tabIndex={-1}
          type="file"
        />
      </div>
      {selectedFile && !error && (
        <p className={styles.fileInfo}>
          {selectedFile.name} ({formatSize(selectedFile.size)})
        </p>
      )}
      {error && (
        <p className={styles.error} id={errorId} role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
