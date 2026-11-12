import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import styles from './BandejaFilters.module.css'

export type FiltrosBandeja = {
  estado: string
  numero: string
}

type BandejaFiltersProps = {
  filtros: FiltrosBandeja
  estadosDisponibles: string[]
  visibles: number
  totalPagina: number
  onChange: (filtros: FiltrosBandeja) => void
}

/**
 * FE-T703: filtros **de la página actual**. El backend no admite filtros ni
 * búsqueda en la bandeja (BE-09), así que no se ofrece una búsqueda global.
 */
export function BandejaFilters({ filtros, estadosDisponibles, visibles, totalPagina, onChange }: BandejaFiltersProps) {
  return (
    <section aria-label="Filtros de la página actual" className={styles.filtros}>
      <p className={styles.aviso} id="bandeja-filtros-alcance">
        Estos filtros solo actúan sobre la página actual ({visibles} de {totalPagina} expedientes visibles); no
        buscan en toda la bandeja.
      </p>
      <div className={styles.campos}>
        <Select
          aria-describedby="bandeja-filtros-alcance"
          label="Estado (página actual)"
          options={estadosDisponibles.map((estado) => ({ value: estado, label: estado }))}
          placeholder="Todos los estados"
          value={filtros.estado}
          onChange={(event) => onChange({ ...filtros, estado: event.target.value })}
        />
        <Input
          aria-describedby="bandeja-filtros-alcance"
          label="Número de expediente (página actual)"
          value={filtros.numero}
          onChange={(event) => onChange({ ...filtros, numero: event.target.value })}
        />
      </div>
    </section>
  )
}

export function aplicarFiltros<T extends { estado: string; numero_expediente: string }>(
  filas: T[],
  filtros: FiltrosBandeja,
): T[] {
  const numero = filtros.numero.trim().toLowerCase()
  return filas.filter(
    (fila) =>
      (filtros.estado === '' || fila.estado === filtros.estado) &&
      (numero === '' || fila.numero_expediente.toLowerCase().includes(numero)),
  )
}
