type LogContext = Record<string, unknown>

function info(message: string, context?: LogContext): void {
  console.info(message, context)
}

function warn(message: string, context?: LogContext): void {
  console.warn(message, context)
}

function error(message: string, context?: LogContext): void {
  console.error(message, context)
}

export const logger = { info, warn, error }
