/**
 * Vista 401 (DEC-17, 2026-11-24). El manejador global de 401 marca la sesión
 * como expirada y cierra la sesión; RequireAuth —la única pieza que redirige
 * desde rutas protegidas— consulta la marca para decidir entre la vista 401
 * y el login. Así no compiten dos navegaciones (la del manejador y la de la
 * guarda) y no hay bucles: la vista es pública y no hace peticiones.
 */
export const SESSION_EXPIRED_PATH = '/sesion-expirada'

let expirada = false

export function marcarSesionExpirada(): void {
  expirada = true
}

export function sesionExpiradaPendiente(): boolean {
  return expirada
}

export function limpiarSesionExpirada(): void {
  expirada = false
}

/** Solo rutas internas de la SPA, nunca la propia vista ni el login. */
export function rutaDeRetorno(valor: unknown): string | null {
  if (typeof valor !== 'string' || !valor.startsWith('/') || valor.startsWith('//')) {
    return null
  }
  if (valor === SESSION_EXPIRED_PATH || valor === '/login') {
    return null
  }
  return valor
}
