import { useCallback, useContext, useState } from 'react'
import type { UseQueryResult } from '@tanstack/react-query'
import type { ChecklistItem } from '@/api/endpoints/checklist'
import type { EstadoExpediente } from '@/api/endpoints/expedientes'
import type { ApiRequestError } from '@/api/errors'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { FileUpload } from '@/components/ui/FileUpload'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Textarea } from '@/components/ui/Textarea'
import { describeAccionError } from '@/features/expediente'
import { formatFecha } from '@/lib/dates'
import { checklistCompleto, puedeDeclararAptitud, puedeEmitirInforme } from './accionesResolucion'
import { useEmitirInforme, useRegistrarDeclaratoria } from './resolucionesQueries'
import styles from './ResolucionesSection.module.css'

type ResolucionesSectionProps = {
  expedienteId: string
  estado: EstadoExpediente
  roles: string[]
  checklistQuery: UseQueryResult<ChecklistItem[], ApiRequestError>
}

type Resultado = { titulo: string; detalle: string }

/**
 * V-08b — Informe de aptitud (FE-T804) y declaratoria (FE-T805).
 * No existe GET de informes ni de declaratorias ni descarga de sus PDF: el
 * resultado solo se muestra con los datos que devuelve la creación.
 */
export function ResolucionesSection({ expedienteId, estado, roles, checklistQuery }: ResolucionesSectionProps) {
  const toast = useContext(ToastContext)
  const informeMutation = useEmitirInforme(expedienteId)
  const declaratoriaMutation = useRegistrarDeclaratoria(expedienteId)

  const [informeAbierto, setInformeAbierto] = useState(false)
  const [fundamentacion, setFundamentacion] = useState('')
  const [declaratoriaAbierta, setDeclaratoriaAbierta] = useState(false)
  const [archivo, setArchivo] = useState<File | null>(null)
  const [numeroMemorando, setNumeroMemorando] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<Resultado | null>(null)

  // `Modal` repite su efecto de foco si cambia `onClose`: debe ser estable para
  // que el foco no salte fuera del campo en cada tecla.
  const cerrar = useCallback(() => {
    setInformeAbierto(false)
    setDeclaratoriaAbierta(false)
    setError(null)
  }, [])

  const mostrarInforme = puedeEmitirInforme(roles, estado)
  const mostrarDeclaratoria = puedeDeclararAptitud(roles, estado)
  if (!mostrarInforme && !mostrarDeclaratoria && !resultado) {
    return null
  }
  const informeHabilitado = checklistCompleto(checklistQuery.data)

  async function confirmarInforme() {
    setError(null)
    try {
      const informe = await informeMutation.mutateAsync(fundamentacion.trim())
      cerrar()
      setResultado({
        titulo: 'Informe de aptitud emitido',
        detalle: `Providencia ${informe.numero_providencia} · dictamen ${informe.dictamen} · ${formatFecha(informe.fecha_emision)}`,
      })
      toast?.showToast('Informe de aptitud emitido.', 'success')
    } catch (accionError) {
      setError(describeAccionError(accionError))
    }
  }

  async function confirmarDeclaratoria() {
    if (!archivo) {
      return
    }
    setError(null)
    try {
      const declaratoria = await declaratoriaMutation.mutateAsync({ archivo, numeroMemorando })
      cerrar()
      setResultado({
        titulo: 'Declaratoria de aptitud registrada',
        detalle: `Memorando ${declaratoria.numero_memorando} · ${formatFecha(declaratoria.fecha_declaratoria)}`,
      })
      toast?.showToast('Declaratoria de aptitud registrada.', 'success')
    } catch (accionError) {
      setError(describeAccionError(accionError))
    }
  }

  return (
    <Card title="Resoluciones">
      <div className={styles.cuerpo}>
        {resultado && (
          <Alert title={resultado.titulo} variant="success">
            {resultado.detalle}. El sistema todavía no permite consultar ni descargar después este documento.
          </Alert>
        )}
        {mostrarInforme && (
          <div className={styles.accion}>
            <Button disabled={!informeHabilitado} onClick={() => setInformeAbierto(true)}>
              Emitir informe de aptitud
            </Button>
            {!informeHabilitado && (
              <p className={styles.nota}>Disponible cuando todos los requisitos del checklist estén verificados.</p>
            )}
          </div>
        )}
        {mostrarDeclaratoria && (
          <Button onClick={() => setDeclaratoriaAbierta(true)}>Registrar declaratoria de aptitud</Button>
        )}
      </div>

      <Modal onClose={cerrar} open={informeAbierto} title="Emitir informe de aptitud">
        <div className={styles.dialogo}>
          <p>
            Dictamen: <strong>APTO</strong>. El sistema solo admite emitir el informe con dictamen apto; el expediente
            pasará a INFORME_EMITIDO.
          </p>
          <Textarea
            label="Fundamentación (opcional)"
            value={fundamentacion}
            onChange={(event) => setFundamentacion(event.target.value)}
          />
          {error && <Alert variant="danger">{error}</Alert>}
          <div className={styles.botones}>
            <Button loading={informeMutation.isPending} onClick={() => void confirmarInforme()}>
              Confirmar informe
            </Button>
            <Button disabled={informeMutation.isPending} variant="ghost" onClick={cerrar}>
              Cancelar
            </Button>
          </div>
        </div>
      </Modal>

      <Modal onClose={cerrar} open={declaratoriaAbierta} title="Registrar declaratoria de aptitud">
        <div className={styles.dialogo}>
          <FileUpload
            hint="Memorando firmado electrónicamente, en PDF de hasta 10 MB."
            label="Memorando firmado"
            onFileSelected={setArchivo}
            onInvalidFile={() => setArchivo(null)}
          />
          <Input
            hint="Opcional: si lo deja vacío, el sistema asigna el número."
            label="Número de memorando"
            value={numeroMemorando}
            onChange={(event) => setNumeroMemorando(event.target.value)}
          />
          {error && <Alert variant="danger">{error}</Alert>}
          <div className={styles.botones}>
            <Button
              disabled={archivo === null}
              loading={declaratoriaMutation.isPending}
              onClick={() => void confirmarDeclaratoria()}
            >
              Confirmar declaratoria
            </Button>
            <Button disabled={declaratoriaMutation.isPending} variant="ghost" onClick={cerrar}>
              Cancelar
            </Button>
          </div>
        </div>
      </Modal>
    </Card>
  )
}
