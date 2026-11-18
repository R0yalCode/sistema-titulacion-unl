import { useState } from 'react'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import styles from './components/authForm.module.css'

type RecoveryCodesStepProps = {
  codes: string[]
  onContinue: () => void
}

/**
 * Códigos de recuperación de un solo uso. El backend solo los entrega una vez
 * y guarda su hash; aquí viven únicamente en memoria hasta continuar.
 */
export function RecoveryCodesStep({ codes, onContinue }: RecoveryCodesStepProps) {
  const [saved, setSaved] = useState(false)
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(codes.join('\n'))
      setCopied(true)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className={styles.form}>
      <Alert title="Guárdelos ahora" variant="warning">
        Estos códigos permiten ingresar si pierde su teléfono. Cada uno sirve una sola vez y no volverán a mostrarse.
      </Alert>
      <ol aria-label="Códigos de recuperación" className={styles.codes}>
        {codes.map((code) => (
          <li key={code}>
            <code>{code}</code>
          </li>
        ))}
      </ol>
      <Button variant="secondary" onClick={() => void copy()}>
        {copied ? 'Códigos copiados' : 'Copiar códigos'}
      </Button>
      <Checkbox
        checked={saved}
        label="Guardé mis códigos de recuperación en un lugar seguro"
        onChange={(event) => setSaved(event.target.checked)}
      />
      <Button className={styles.submit} disabled={!saved} size="lg" onClick={onContinue}>
        Continuar al sistema
      </Button>
    </div>
  )
}
