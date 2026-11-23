import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRightIcon, ExternalLinkIcon, SearchIcon } from '@/components/ui/icons'
import { presentarEstado } from '@/lib/estados'
import { useResumenBandeja } from '../queries'
import styles from './AdminSearch.module.css'

export type DestinoBusqueda = { label: string; to: string; external?: boolean; detalle?: string }

type Resultado = DestinoBusqueda & { id: string; grupo: 'Secciones' | 'Expedientes' }

const MAX_EXPEDIENTES = 8

function normalizar(texto: string): string {
  return texto
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

type Props = { destinos: DestinoBusqueda[]; onClose: () => void }

export default function AdminSearchDialog({ destinos, onClose }: Props) {
  const navigate = useNavigate()
  const baseId = useId()
  const inputRef = useRef<HTMLInputElement>(null)
  const [texto, setTexto] = useState('')
  const [activo, setActivo] = useState(0)
  const bandeja = useResumenBandeja()

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const resultados = useMemo<Resultado[]>(() => {
    const consulta = normalizar(texto)
    const coincide = (valor: string) => consulta === '' || normalizar(valor).includes(consulta)
    const secciones = destinos
      .filter((destino) => coincide(`${destino.label} ${destino.detalle ?? ''}`))
      .map((destino): Resultado => ({ ...destino, id: `s-${destino.to}`, grupo: 'Secciones' }))
    const expedientes = (bandeja.data?.results ?? [])
      .filter((item) => coincide(item.numero_expediente))
      .slice(0, MAX_EXPEDIENTES)
      .map(
        (item): Resultado => ({
          id: `e-${item.id}`,
          grupo: 'Expedientes',
          label: item.numero_expediente,
          detalle: presentarEstado('expediente', item.estado).label,
          to: `/bandeja/${item.id}`,
        }),
      )
    return [...secciones, ...expedientes]
  }, [bandeja.data, destinos, texto])

  const indice = Math.min(activo, Math.max(resultados.length - 1, 0))
  const opcionId = (posicion: number) => `${baseId}-opcion-${posicion}`
  const parcial = bandeja.data && bandeja.data.results.length < bandeja.data.count

  function abrir(resultado: Resultado | undefined) {
    if (!resultado) {
      return
    }
    if (resultado.external) {
      window.location.assign(resultado.to)
      return
    }
    onClose()
    navigate(resultado.to)
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Escape') {
      event.preventDefault()
      onClose()
    } else if (event.key === 'Tab') {
      // El campo es el único elemento enfocable del diálogo modal.
      event.preventDefault()
    } else if (event.key === 'ArrowDown' && resultados.length > 0) {
      event.preventDefault()
      setActivo((indice + 1) % resultados.length)
    } else if (event.key === 'ArrowUp' && resultados.length > 0) {
      event.preventDefault()
      setActivo((indice - 1 + resultados.length) % resultados.length)
    } else if (event.key === 'Enter') {
      event.preventDefault()
      abrir(resultados[indice])
    }
  }

  return (
    <div className={styles.overlay}>
      <button aria-label="Cerrar búsqueda" className={styles.backdrop} tabIndex={-1} type="button" onClick={onClose} />
      <div aria-label="Buscar secciones y expedientes" aria-modal="true" className={styles.dialog} role="dialog">
        <div className={styles.field}>
          <SearchIcon size={18} />
          <input
            aria-activedescendant={resultados.length > 0 ? opcionId(indice) : undefined}
            aria-autocomplete="list"
            aria-controls={`${baseId}-lista`}
            aria-expanded="true"
            aria-label="Texto de búsqueda"
            autoComplete="off"
            className={styles.input}
            placeholder="Buscar por sección o número de expediente…"
            ref={inputRef}
            role="combobox"
            type="text"
            value={texto}
            onChange={(event) => {
              setTexto(event.target.value)
              setActivo(0)
            }}
            onKeyDown={onKeyDown}
          />
          <kbd className={styles.kbd}>Esc</kbd>
        </div>

        <ul aria-label="Resultados" className={styles.list} id={`${baseId}-lista`} role="listbox">
          {resultados.map((resultado, posicion) => (
            <li
              aria-selected={posicion === indice}
              className={posicion === indice ? `${styles.option} ${styles.optionActive}` : styles.option}
              id={opcionId(posicion)}
              key={resultado.id}
              role="option"
              onMouseDown={(event) => {
                // El foco permanece en el campo: el teclado se gestiona allí (aria-activedescendant).
                event.preventDefault()
                abrir(resultado)
              }}
              onMouseEnter={() => setActivo(posicion)}
            >
              <span className={styles.optionGroup}>{resultado.grupo}</span>
              <span className={styles.optionLabel}>{resultado.label}</span>
              {resultado.detalle && <span className={styles.optionDetail}>{resultado.detalle}</span>}
              {resultado.external ? <ExternalLinkIcon size={14} /> : <ArrowRightIcon size={14} />}
            </li>
          ))}
        </ul>

        <div aria-live="polite" className={styles.status} role="status">
          {bandeja.isLoading && 'Cargando expedientes…'}
          {bandeja.isError && (
            <>
              No se pudieron cargar los expedientes.{' '}
              <button className={styles.retry} tabIndex={-1} type="button" onClick={() => void bandeja.refetch()}>
                Reintentar
              </button>
            </>
          )}
          {!bandeja.isLoading && !bandeja.isError && resultados.length === 0 && 'Sin resultados para esta búsqueda.'}
          {!bandeja.isLoading &&
            !bandeja.isError &&
            resultados.length > 0 &&
            (parcial
              ? `Expedientes: se buscan los ${bandeja.data?.results.length} más próximos a vencer de ${bandeja.data?.count}.`
              : `${resultados.length} ${resultados.length === 1 ? 'resultado' : 'resultados'}.`)}
        </div>
      </div>
    </div>
  )
}
