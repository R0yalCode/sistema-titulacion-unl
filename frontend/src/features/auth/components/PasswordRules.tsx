import type { PasswordRule } from '../validation'
import { CheckCircleIcon, CircleIcon } from '@/components/ui/icons'
import styles from './authForm.module.css'

type PasswordRulesProps = {
  id: string
  rules: PasswordRule[]
}

/** Indicador de cumplimiento de los requisitos de la nueva contraseña. */
export function PasswordRules({ id, rules }: PasswordRulesProps) {
  return (
    <ul aria-label="Requisitos de la contraseña" className={styles.rules} id={id}>
      {rules.map((rule) => (
        <li className={[styles.rule, rule.met && styles.ruleMet].filter(Boolean).join(' ')} key={rule.id}>
          {rule.met ? <CheckCircleIcon /> : <CircleIcon />}
          <span>
            {rule.label}
            <span className={styles.srOnly}>{rule.met ? ' (cumplido)' : ' (pendiente)'}</span>
          </span>
        </li>
      ))}
    </ul>
  )
}
