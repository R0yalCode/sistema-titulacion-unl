import { lazy, Suspense, useContext, useLayoutEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { AuthContext } from '@/auth/AuthContext'
import { RedirectIfAuthenticated, RequireAuth, RequireRole } from '@/auth/guards'
import { getHomeRouteForRoles } from '@/auth/redirect'
import { OPERATIONAL_ROLES } from '@/auth/roles'
import { setUnauthorizedHandler } from '@/api/client'
import { ToastContext } from '@/components/feedback/ToastProvider'
import { queryClient } from '@/lib/queryClient'

const LandingPage = lazy(() => import('@/features/landing/LandingPage'))
const LoginPage = lazy(() => import('@/features/auth/LoginPage'))
const ForgotPasswordPage = lazy(() => import('@/features/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('@/features/auth/ResetPasswordPage'))
const MfaResetRequestPage = lazy(() => import('@/features/auth/MfaResetRequestPage'))
const MfaResetConfirmPage = lazy(() => import('@/features/auth/MfaResetConfirmPage'))
const StudentDashboardPage = lazy(() => import('@/features/dashboard/StudentDashboardPage'))
const NuevaSolicitudPage = lazy(() => import('@/features/solicitud/NuevaSolicitudPage'))
const ExpedientePage = lazy(() => import('@/features/expediente/ExpedientePage'))
const PeticionesPage = lazy(() => import('@/features/peticiones/PeticionesPage'))
const SeguimientoPeticionPage = lazy(() => import('@/features/peticiones/SeguimientoPeticionPage'))
const BandejaPage = lazy(() => import('@/features/bandeja/BandejaPage'))
const DetalleFuncionarioPage = lazy(() => import('@/features/bandeja/DetalleFuncionarioPage'))
const NoHabilitadoPage = lazy(() => import('@/features/no-habilitado/NoHabilitadoPage'))
const NotFoundPage = lazy(() => import('./NotFoundPage'))

function RouteLoadingFallback() {
  return (
    <div aria-live="polite" role="status">
      Cargando…
    </div>
  )
}

/**
 * `/` es pública (AUTH-E): sin sesión muestra la página informativa; con
 * sesión redirige al inicio que corresponde a los roles del JWT.
 */
function HomeRoute() {
  const auth = useContext(AuthContext)
  if (!auth?.isAuthenticated) {
    return <LandingPage />
  }
  return <Navigate replace to={getHomeRouteForRoles(auth.user?.roles ?? [])} />
}

function LoginRoute() {
  const auth = useContext(AuthContext)
  const homeRoute = getHomeRouteForRoles(auth?.user?.roles ?? [])
  return (
    <RedirectIfAuthenticated homeRoute={homeRoute}>
      <LoginPage />
    </RedirectIfAuthenticated>
  )
}

function AuthExpiryBootstrap() {
  const auth = useContext(AuthContext)
  const toast = useContext(ToastContext)
  const navigate = useNavigate()

  // FE-T1001/FE-T1008: useLayoutEffect registra el manejador en el mismo commit
  // que pinta la interfaz, antes de cualquier efecto pasivo (donde se lanzan
  // las consultas), para que ningún 401 llegue sin manejador.
  useLayoutEffect(() => {
    setUnauthorizedHandler(() => {
      auth?.logout()
      queryClient.clear()
      toast?.showToast('Su sesión ha expirado. Inicie sesión nuevamente.', 'warning')
      navigate('/login', { replace: true })
    })

    return () => setUnauthorizedHandler(null)
  }, [auth, toast, navigate])

  return null
}

export function AppRouter() {
  return (
    <>
      {/* Fuera del Suspense: si una ruta lazy suspende, el manejador del 401 no
          debe esperar a que cargue (FE-T1001; ver REGRESSION_TESTS.md). */}
      <AuthExpiryBootstrap />
      <Suspense fallback={<RouteLoadingFallback />}>
        <Routes>
          <Route element={<HomeRoute />} path="/" />
          <Route element={<LoginRoute />} path="/login" />
          {/* Recuperación de contraseña: públicas; no dependen de la sesión. */}
          <Route element={<ForgotPasswordPage />} path="/recuperar-contrasena" />
          <Route element={<ResetPasswordPage />} path="/restablecer-contrasena" />
          {/* Restablecimiento del 2FA (MFA-RST): públicas. */}
          <Route element={<MfaResetRequestPage />} path="/restablecer-2fa" />
          <Route element={<MfaResetConfirmPage />} path="/restablecer-2fa/confirmar" />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route element={<RequireRole roles={['ESTUDIANTE']} />}>
                <Route element={<StudentDashboardPage />} path="/estudiante" />
                <Route element={<NuevaSolicitudPage />} path="/estudiante/solicitud/nueva" />
              </Route>
              <Route element={<ExpedientePage />} path="/expedientes/:id" />
              <Route element={<PeticionesPage />} path="/expedientes/:id/peticiones" />
              <Route
                element={<SeguimientoPeticionPage />}
                path="/expedientes/:id/peticiones/:peticionId"
              />
              <Route element={<RequireRole roles={OPERATIONAL_ROLES} />}>
                <Route element={<BandejaPage />} path="/bandeja" />
                <Route element={<DetalleFuncionarioPage />} path="/bandeja/:id" />
              </Route>
              <Route element={<NoHabilitadoPage />} path="/no-habilitado" />
            </Route>
          </Route>
          <Route element={<NotFoundPage />} path="*" />
        </Routes>
      </Suspense>
    </>
  )
}
