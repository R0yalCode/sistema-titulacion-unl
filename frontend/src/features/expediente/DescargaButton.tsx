import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { fetchAuthenticatedFile, triggerBlobDownload } from '@/lib/download'
import { describeAccionError } from './errors'

type DescargaButtonProps = {
  peticionId: string
  fallbackFilename: string
}

/** FE-T408: descarga autenticada real; no asume que la respuesta siempre es PDF. */
export function DescargaButton({ peticionId, fallbackFilename }: DescargaButtonProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleDownload() {
    setLoading(true)
    setError(null)
    try {
      const { blob, filename } = await fetchAuthenticatedFile(
        `/api/v1/peticiones/${peticionId}/documento/`,
        fallbackFilename,
      )
      triggerBlobDownload(blob, filename)
    } catch (downloadError) {
      setError(describeAccionError(downloadError))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Button loading={loading} size="sm" variant="secondary" onClick={() => void handleDownload()}>
        Descargar
      </Button>
      {error && (
        <p role="alert">{error}</p>
      )}
    </div>
  )
}
