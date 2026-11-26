import { useContext } from 'react'
import { AccesibilidadContext, type AccesibilidadContextValue } from './AccesibilidadContext'

export function useAccesibilidad(): AccesibilidadContextValue {
  const contexto = useContext(AccesibilidadContext)
  if (!contexto) {
    throw new Error('useAccesibilidad debe usarse dentro de <AccesibilidadProvider>.')
  }
  return contexto
}
