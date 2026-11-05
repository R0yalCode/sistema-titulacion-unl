import { NavLink } from 'react-router-dom'
import styles from './Sidebar.module.css'

export type SidebarItem = {
  to: string
  label: string
  roles: string[]
}

type SidebarProps = {
  items: SidebarItem[]
  roles: string[]
  open: boolean
}

export function Sidebar({ items, roles, open }: SidebarProps) {
  const visibleItems = items.filter((item) => item.roles.some((role) => roles.includes(role)))

  return (
    <nav
      aria-label="Navegación principal"
      className={open ? `${styles.sidebar} ${styles.sidebarOpen}` : styles.sidebar}
    >
      <ul className={styles.list}>
        {visibleItems.map((item) => (
          <li key={item.to}>
            <NavLink
              className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
              to={item.to}
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
