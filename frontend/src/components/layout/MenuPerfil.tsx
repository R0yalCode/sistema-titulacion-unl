import { useEffect, useId, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ChevronDownIcon, LockIcon, LogoutIcon, UserIcon } from '@/components/ui/icons'
import { iniciales } from './nombreVisible'
import styles from './MenuPerfil.module.css'

/** Mecanismo de recuperación existente (correo con enlace): no hay cambio de contraseña con sesión iniciada. */
export const RUTA_CAMBIAR_CONTRASENA = '/recuperar-contrasena'

export type MenuPerfilProps = {
  /** Primer nombre y primer apellido, o el rol del funcionario. */
  nombre: string
  /** Texto secundario real ("Estudiante", "C.I. …"). */
  detalle: string
  /** Ruta de la página de perfil, si el rol la tiene. */
  perfilTo: string | null
  /** Cierre de sesión existente (con su confirmación). */
  onCerrarSesion: () => void
}

/**
 * Menú desplegable del usuario en la barra superior (AX-C, DK-010).
 *
 * Se ancla al botón (no es un diálogo centrado). Patrón ARIA de botón de menú:
 * `aria-haspopup="menu"`, flechas, Inicio y Fin para moverse, Escape para
 * cerrar devolviendo el foco, y cierre con Tab, al pulsar fuera y al navegar.
 * Solo muestra datos reales: no hay fecha de último acceso ni estado de
 * cuenta en la API, así que no se muestran.
 */
export function MenuPerfil({ nombre, detalle, perfilTo, onCerrarSesion }: MenuPerfilProps) {
  const { pathname } = useLocation()
  // Abierto solo en la ruta donde se abrió: al navegar se cierra sin efectos.
  const [abiertoEn, setAbiertoEn] = useState<string | null>(null)
  const abierto = abiertoEn === pathname
  // Elemento que recibe el foco al abrir: el último si se abrió con flecha arriba.
  const [focoInicial, setFocoInicial] = useState<'primero' | 'ultimo'>('primero')
  const raizRef = useRef<HTMLDivElement>(null)
  const botonRef = useRef<HTMLButtonElement>(null)
  const menuRef = useRef<HTMLUListElement>(null)
  const idMenu = useId()
  const idBoton = useId()

  function elementos(): HTMLElement[] {
    return Array.from(menuRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [])
  }

  function enfocar(indice: number) {
    const lista = elementos()
    if (lista.length === 0) {
      return
    }
    lista[(indice + lista.length) % lista.length]?.focus()
  }

  function cerrar(devolverFoco: boolean) {
    setAbiertoEn(null)
    if (devolverFoco) {
      botonRef.current?.focus()
    }
  }

  useEffect(() => {
    if (!abierto) {
      return
    }
    const lista = Array.from(menuRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [])
    lista[focoInicial === 'primero' ? 0 : lista.length - 1]?.focus()
    function alPulsarFuera(evento: PointerEvent) {
      if (raizRef.current && !raizRef.current.contains(evento.target as Node)) {
        setAbiertoEn(null)
      }
    }
    document.addEventListener('pointerdown', alPulsarFuera)
    return () => document.removeEventListener('pointerdown', alPulsarFuera)
  }, [abierto, focoInicial])

  function abrir(foco: 'primero' | 'ultimo') {
    setFocoInicial(foco)
    setAbiertoEn(pathname)
  }

  function alPulsarTeclaBoton(evento: ReactKeyboardEvent<HTMLButtonElement>) {
    if (evento.key === 'ArrowDown' || evento.key === 'ArrowUp') {
      evento.preventDefault()
      const foco = evento.key === 'ArrowDown' ? 'primero' : 'ultimo'
      if (abierto) {
        enfocar(foco === 'primero' ? 0 : -1)
      } else {
        abrir(foco)
      }
    }
  }

  function alPulsarTeclaMenu(evento: ReactKeyboardEvent<HTMLUListElement>) {
    const lista = elementos()
    const actual = lista.indexOf(document.activeElement as HTMLElement)
    switch (evento.key) {
      case 'ArrowDown':
        evento.preventDefault()
        enfocar(actual + 1)
        break
      case 'ArrowUp':
        evento.preventDefault()
        enfocar(actual - 1)
        break
      case 'Home':
        evento.preventDefault()
        enfocar(0)
        break
      case 'End':
        evento.preventDefault()
        enfocar(-1)
        break
      case 'Escape':
        evento.preventDefault()
        cerrar(true)
        break
      case 'Tab':
        // El foco sigue su orden natural; el menú no debe quedar abierto detrás.
        cerrar(false)
        break
    }
  }

  function cerrarSesion() {
    cerrar(true)
    onCerrarSesion()
  }

  const avatar = iniciales(nombre)
  // Nombre accesible explícito: los <span> contiguos se concatenarían sin
  // separador ("…PruebaEstudiante"). Contiene el texto visible (WCAG 2.5.3).
  const etiqueta = `Menú de usuario: ${nombre}${detalle ? `, ${detalle}` : ''}`

  return (
    <div className={styles.raiz} ref={raizRef}>
      <button
        aria-controls={abierto ? idMenu : undefined}
        aria-expanded={abierto}
        aria-haspopup="menu"
        aria-label={etiqueta}
        className={styles.disparador}
        id={idBoton}
        ref={botonRef}
        type="button"
        onClick={() => (abierto ? cerrar(false) : abrir('primero'))}
        onKeyDown={alPulsarTeclaBoton}
      >
        <span aria-hidden="true" className={styles.avatar}>
          {avatar || <UserIcon size={18} />}
        </span>
        <span aria-hidden="true" className={styles.texto}>
          <span className={styles.nombre}>{nombre}</span>
          {detalle && <span className={styles.detalle}>{detalle}</span>}
        </span>
        <ChevronDownIcon aria-hidden="true" className={styles.flecha} size={16} />
      </button>

      {abierto && (
        <div className={styles.desplegable}>
          <div className={styles.cabecera}>
            <span aria-hidden="true" className={styles.avatarGrande}>
              {avatar || <UserIcon size={20} />}
            </span>
            <span className={styles.identidad}>
              <span className={styles.nombreCabecera}>{nombre}</span>
              {detalle && <span className={styles.detalle}>{detalle}</span>}
            </span>
          </div>
          <ul aria-labelledby={idBoton} className={styles.menu} id={idMenu} ref={menuRef} role="menu" onKeyDown={alPulsarTeclaMenu}>
            {perfilTo && (
              <li role="none">
                <Link className={styles.opcion} role="menuitem" tabIndex={-1} to={perfilTo} onClick={() => cerrar(false)}>
                  <UserIcon size={18} />
                  Mi perfil
                </Link>
              </li>
            )}
            <li role="none">
              <Link className={styles.opcion} role="menuitem" tabIndex={-1} to={RUTA_CAMBIAR_CONTRASENA} onClick={() => cerrar(false)}>
                <LockIcon size={18} />
                Cambiar contraseña
              </Link>
            </li>
            <li className={styles.separador} role="separator" />
            <li role="none">
              <button className={`${styles.opcion} ${styles.salir}`} role="menuitem" tabIndex={-1} type="button" onClick={cerrarSesion}>
                <LogoutIcon size={18} />
                Cerrar sesión
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  )
}
