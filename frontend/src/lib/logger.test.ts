import { describe, expect, it, vi } from 'vitest'
import { logger } from '@/lib/logger'

describe('logger (alias import @/lib/logger)', () => {
  it('delega en console con el contexto dado', () => {
    const infoSpy = vi.spyOn(console, 'info').mockImplementation(() => undefined)

    logger.info('mensaje', { origen: 'test' })

    expect(infoSpy).toHaveBeenCalledWith('mensaje', { origen: 'test' })
    infoSpy.mockRestore()
  })
})
