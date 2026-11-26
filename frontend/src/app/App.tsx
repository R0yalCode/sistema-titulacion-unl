import { PanelAccesibilidad } from '@/features/accesibilidad'
import { AsistenteGlobal } from '@/features/asistente'
import { AppProviders } from './providers'
import { AppRouter } from './router'

function App() {
  return (
    <AppProviders>
      <AppRouter />
      {/* Herramientas de accesibilidad globales (AX-A): en todas las rutas. */}
      <PanelAccesibilidad />
      {/* Asistente institucional (AX-D): solo con sesión, en las rutas principales. */}
      <AsistenteGlobal />
    </AppProviders>
  )
}

export default App
