import { act, render, renderHook, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiRequestError, networkApiError, normalizeApiError, timeoutApiError } from '@/api/errors'
import { QueryErrorView } from './QueryErrorView'
import { esperaTrasIntento, useControlledRetry } from './useControlledRetry'
import { useOnlineStatus } from './useOnlineStatus'

function setOnline(valor: boolean) {
  Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => valor })
}

afterEach(() => {
  setOnline(true)
  vi.useRealTimers()
})

describe('useControlledRetry', () => {
  it('la espera crece 5, 10, 20, 40 s y se limita a 60 s', () => {
    expect([1, 2, 3, 4, 5, 9].map(esperaTrasIntento)).toEqual([5, 10, 20, 40, 60, 60])
  })

  it('no reintenta por su cuenta ni duplica un intento en curso', async () => {
    let resolver: () => void = () => undefined
    const retry = vi.fn(() => new Promise<void>((r) => (resolver = r)))
    const { result } = renderHook(() => useControlledRetry(retry))
    expect(retry).not.toHaveBeenCalled()

    act(() => result.current.run())
    await act(async () => undefined)
    expect(result.current.pending).toBe(true)
    act(() => result.current.run())
    expect(retry).toHaveBeenCalledTimes(1)

    await act(async () => resolver())
    expect(result.current.pending).toBe(false)
  })

  it('con backoff bloquea el siguiente intento durante la espera', async () => {
    vi.useFakeTimers()
    const retry = vi.fn(() => Promise.resolve())
    const { result } = renderHook(() => useControlledRetry(retry, { backoff: true }))

    await act(async () => result.current.run())
    expect(result.current.waitSeconds).toBe(5)
    act(() => result.current.run())
    expect(retry).toHaveBeenCalledTimes(1)

    for (let i = 0; i < 5; i += 1) {
      await act(async () => vi.advanceTimersByTime(1000))
    }
    expect(result.current.waitSeconds).toBe(0)
    await act(async () => result.current.run())
    expect(retry).toHaveBeenCalledTimes(2)
    expect(result.current.waitSeconds).toBe(10)
  })
})

describe('useOnlineStatus', () => {
  it('sigue los eventos online/offline y retira sus listeners al desmontar', () => {
    const quitar = vi.spyOn(window, 'removeEventListener')
    const { result, unmount } = renderHook(() => useOnlineStatus())
    expect(result.current).toBe(true)

    setOnline(false)
    act(() => {
      window.dispatchEvent(new Event('offline'))
    })
    expect(result.current).toBe(false)

    unmount()
    expect(quitar).toHaveBeenCalledWith('online', expect.any(Function))
    expect(quitar).toHaveBeenCalledWith('offline', expect.any(Function))
    quitar.mockRestore()
  })
})

function renderVista(error: unknown, onRetry = vi.fn()) {
  render(
    <MemoryRouter>
      <QueryErrorView error={error} onRetry={onRetry} />
    </MemoryRouter>,
  )
  return onRetry
}

describe('QueryErrorView', () => {
  it('timeout del cliente: vista de tiempo agotado con reintento de la consulta', async () => {
    const user = userEvent.setup()
    const onRetry = renderVista(new ApiRequestError(timeoutApiError()))
    expect(screen.getByRole('heading', { name: 'La solicitud está tardando demasiado' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Intentar nuevamente' }))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('sin red en el dispositivo: vista sin conexión que no promete reconexión', () => {
    setOnline(false)
    renderVista(new ApiRequestError(networkApiError()))
    expect(screen.getByRole('heading', { name: 'Sin conexión' })).toBeInTheDocument()
    expect(screen.getByText('Tu dispositivo indica que no hay conexión de red.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reintentar conexión' })).toBeEnabled()
    expect(screen.queryByText(/restablecida|recuperada/i)).not.toBeInTheDocument()
  })

  it('503: tras un intento impone una espera visible antes de permitir otro', async () => {
    const user = userEvent.setup()
    const onRetry = renderVista(new ApiRequestError(normalizeApiError(503, null)), vi.fn(() => Promise.resolve()))
    expect(screen.getByRole('heading', { name: 'El servicio no está disponible' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Reintentar' }))
    expect(await screen.findByText('Podrás reintentar en 5 s.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reintentar' })).toBeDisabled()
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('error de datos (422): vista de carga con el detalle real del backend', () => {
    renderVista(new ApiRequestError(normalizeApiError(422, { detail: 'El perfil académico no está validado.' })))
    expect(screen.getByRole('heading', { name: 'No pudimos cargar la información' })).toBeInTheDocument()
    expect(screen.getByText('El perfil académico no está validado.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Volver a cargar' })).toBeInTheDocument()
  })

  it('401: no reintenta; ofrece el login real (el manejador global ya cerró la sesión)', () => {
    renderVista(new ApiRequestError(normalizeApiError(401, { detail: 'Token expirado.' })))
    expect(screen.getByRole('heading', { name: 'Necesitas iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /intentar|reintentar|cargar/i })).not.toBeInTheDocument()
  })
})
