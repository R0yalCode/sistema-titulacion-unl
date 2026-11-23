import { presentarEstado, type DominioEstado } from '@/lib/estados'
import { Badge } from './Badge'

type StatusBadgeProps = {
  dominio: DominioEstado
  valor: string
  /** Sustituye la etiqueta oficial (p. ej. lenguaje claro para el estudiante) sin cambiar el tono. */
  label?: string
}

/** Badge de estado con etiqueta + icono + color de la fuente única (`lib/estados`). */
export function StatusBadge({ dominio, valor, label }: StatusBadgeProps) {
  const estado = presentarEstado(dominio, valor)
  return (
    <Badge icon variant={estado.variant}>
      {label ?? estado.label}
    </Badge>
  )
}
