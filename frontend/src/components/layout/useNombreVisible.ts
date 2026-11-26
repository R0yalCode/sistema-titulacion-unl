import { useContext } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getMiTramite, type MiTramite } from '@/api/endpoints/miTramite'
import { getPerfilAcademico, type PerfilAcademico } from '@/api/endpoints/perfilAcademico'
import type { ApiRequestError } from '@/api/errors'
import { AuthContext } from '@/auth/AuthContext'
import { OPERATIONAL_ROLES } from '@/auth/roles'
import { MI_TRAMITE_QUERY_KEY } from '@/features/dashboard'
import { PERFIL_ACADEMICO_QUERY_KEY } from '@/features/solicitud'
import { nombreRol } from '@/lib/estados'
import { nombreEstudiante } from './nombreVisible'

export type NombreVisible = {
  /** Texto principal: primer nombre y primer apellido, o el rol del funcionario. */
  nombre: string
  /** Texto secundario real: "Estudiante" o la cédula del funcionario. */
  detalle: string
  esEstudiante: boolean
}

/** El nombre cambia poco: sin esta pausa se pediría el perfil en cada navegación. */
const VIGENCIA_PERFIL_MS = 5 * 60_000

/**
 * Nombre visible del usuario autenticado (AX-C). Reutilizable por el menú de
 * perfil y, más adelante, por el saludo del asistente (AX-D).
 *
 * Comparte la caché con `usePerfilAcademico` (V-03) y `useMiTramite` (V-02)
 * mediante las mismas claves; el `staleTime` es de cada observador, así que
 * V-03 sigue releyendo el perfil en cada visita (`staleTime: 0`).
 */
export function useNombreVisible(): NombreVisible {
  const auth = useContext(AuthContext)
  const roles = auth?.user?.roles ?? []
  const esEstudiante = roles.includes('ESTUDIANTE') && !roles.some((rol) => OPERATIONAL_ROLES.includes(rol))

  const perfil = useQuery<PerfilAcademico, ApiRequestError>({
    queryKey: PERFIL_ACADEMICO_QUERY_KEY,
    queryFn: getPerfilAcademico,
    enabled: esEstudiante,
    staleTime: VIGENCIA_PERFIL_MS,
    retry: false,
  })
  const miTramite = useQuery<MiTramite, ApiRequestError>({
    queryKey: MI_TRAMITE_QUERY_KEY,
    queryFn: getMiTramite,
    enabled: esEstudiante,
    retry: false,
  })

  if (esEstudiante) {
    const nombre = nombreEstudiante({
      perfil: perfil.data?.estudiante ?? null,
      nombreCompleto: miTramite.data?.estudiante.nombre_completo ?? null,
    })
    return { nombre: nombre ?? auth?.user?.cedula ?? 'Estudiante', detalle: 'Estudiante', esEstudiante }
  }

  const rolPrincipal = roles.find((rol) => rol !== 'ESTUDIANTE') ?? roles[0]
  return {
    nombre: rolPrincipal ? nombreRol(rolPrincipal) : 'Usuario',
    detalle: auth?.user?.cedula ? `C.I. ${auth.user.cedula}` : '',
    esEstudiante,
  }
}
