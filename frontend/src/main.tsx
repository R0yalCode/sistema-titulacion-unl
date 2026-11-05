import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/tokens.css'
import './styles/global.css'
import './styles/utilities.css'
import App from './app/App.tsx'
import { EnvError, getEnv } from './lib/env'

const root = createRoot(document.getElementById('root')!)

try {
  getEnv()
  root.render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
} catch (error) {
  const message =
    error instanceof EnvError ? error.message : 'Error de configuración desconocido.'

  root.render(
    <StrictMode>
      <div role="alert">
        <h1>Error de configuración</h1>
        <p>{message}</p>
      </div>
    </StrictMode>,
  )
}
