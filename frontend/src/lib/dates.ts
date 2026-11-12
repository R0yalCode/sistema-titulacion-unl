export function formatFecha(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) {
    return '—'
  }
  return date.toLocaleDateString('es-EC', { year: 'numeric', month: '2-digit', day: '2-digit' })
}
