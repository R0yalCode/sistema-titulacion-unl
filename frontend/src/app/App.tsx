import { PanelAccesibilidad } from '@/features/accesibilidad'
import { AppProviders } from './providers'
import { AppRouter } from './router'

function App() {
  return (
    <AppProviders>
      <AppRouter />
      {/* Herramientas de accesibilidad globales (AX-A): en todas las rutas. */}
      <PanelAccesibilidad />
    </AppProviders>
  )
}

export default App
