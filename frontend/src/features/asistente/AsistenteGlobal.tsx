import { useContext } from 'react'
import { useLocation } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { AsistenteFlotante } from './AsistenteFlotante'
import { PREFIJOS_RUTAS_CON_ASISTENTE } from './configuracion'

/**
 * Monta el asistente (AX-D) solo con sesión iniciada y en las rutas
 * autenticadas principales; las vistas públicas y de error quedan fuera.
 */
export function AsistenteGlobal() {
  const auth = useContext(AuthContext)
  const { pathname } = useLocation()
  if (!auth?.isAuthenticated) {
    return null
  }
  const enRutaPrincipal = PREFIJOS_RUTAS_CON_ASISTENTE.some(
    (prefijo) => pathname === prefijo || pathname.startsWith(`${prefijo}/`),
  )
  return enRutaPrincipal ? <AsistenteFlotante /> : null
}
