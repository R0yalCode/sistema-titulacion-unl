import '@testing-library/jest-dom/vitest'
import { afterAll, afterEach, beforeAll, expect } from 'vitest'
import * as vitestAxeMatchersModule from 'vitest-axe/matchers'
import { server } from './server'

type AxeMatcherResult = { pass: boolean; message: () => string }

// vitest-axe@0.1.0 ships una `extend-expect.js` vacía y tipa este export como
// type-only por error de empaquetado; se recupera el valor en tiempo de
// ejecución y se registra manualmente contra el `expect` de Vitest.
const { toHaveNoViolations } = vitestAxeMatchersModule as unknown as {
  toHaveNoViolations: (results: unknown) => AxeMatcherResult
}

expect.extend({ toHaveNoViolations })

beforeAll(() => server.listen({ onUnhandledFrame: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
