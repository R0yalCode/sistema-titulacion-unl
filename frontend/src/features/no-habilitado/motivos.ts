/**
 * Catálogo cerrado de motivos de V-09 (FE-T901/FE-T902). Los parámetros de la
 * URL (`?motivo=…&dependencia=BE-xx`) se validan contra listas blancas: un
 * valor desconocido se ignora. Nunca se muestra la ruta solicitada ni detalles
 * de la regla de autorización, para no revelar recursos no autorizados.
 */

export type TipoMotivo = 'forbidden' | 'info'

export type MotivoNoHabilitado = {
  tipo: TipoMotivo
  titulo: string
  descripcion: string
  /** Código de referencia para soporte (CA-V09: código de referencia). */
  codigo: string
  dependencia?: { codigo: string; descripcion: string }
}

/** Dependencias de backend no autorizadas (`tasks.md` §2). */
export const DEPENDENCIAS_BACKEND: Record<string, string> = {
  'BE-01': 'Perfil del usuario o datos de carrera y facultad en la sesión.',
  'BE-02': 'Detalle e historial de cada petición documental.',
  'BE-03': 'Renovación de la sesión y cierre de sesión en el servidor.',
  'BE-04': 'Consulta del checklist por parte del estudiante.',
  'BE-05': 'Perfil e historial de expedientes del estudiante.',
  'BE-06': 'Registro de la opción de titulación en el expediente.',
  'BE-07': 'Motivo de la observación en las respuestas del sistema.',
  'BE-08': 'Acceso del navegador a la API desde el origen del frontend (CORS).',
  'BE-09': 'Bandeja para roles sin expedientes y filtros en el servidor.',
  'BE-10': 'Catálogo de carreras.',
  'BE-11': 'Control de conflictos y versiones en formularios (409/412/428).',
}

const ROL_NO_AUTORIZADO: MotivoNoHabilitado = {
  tipo: 'forbidden',
  titulo: 'Acceso restringido',
  descripcion:
    'No cuenta con los permisos necesarios para ver esta sección. Si considera que esto es un error, comuníquese con la dependencia correspondiente.',
  codigo: 'V09-ROL',
}

const SIN_ROL: MotivoNoHabilitado = {
  tipo: 'forbidden',
  titulo: 'Cuenta sin rol habilitado',
  descripcion: 'Su cuenta no tiene un rol habilitado para usar el sistema de titulación.',
  codigo: 'V09-SIN-ROL',
}

type ResolverOpciones = {
  /** `true` si el usuario no tiene ningún rol con página de inicio. */
  sinRolReconocido: boolean
}

/** Resuelve el motivo a mostrar a partir de los parámetros de la URL. */
export function resolverMotivo(params: URLSearchParams, { sinRolReconocido }: ResolverOpciones): MotivoNoHabilitado {
  const motivo = params.get('motivo')

  if (motivo === 'no-disponible') {
    const codigo = params.get('dependencia') ?? ''
    const descripcion = DEPENDENCIAS_BACKEND[codigo]
    return {
      tipo: 'info',
      titulo: 'Funcionalidad no disponible en esta versión',
      descripcion: 'Esta funcionalidad depende de una ampliación del sistema que todavía no está disponible.',
      codigo: descripcion ? `V09-${codigo}` : 'V09-NO-DISPONIBLE',
      dependencia: descripcion ? { codigo, descripcion } : undefined,
    }
  }

  if (motivo === 'sin-rol' || (motivo === null && sinRolReconocido)) {
    return SIN_ROL
  }

  return ROL_NO_AUTORIZADO
}
