import type { ReactNode, SVGProps } from 'react'

type IconProps = Omit<SVGProps<SVGSVGElement>, 'children'>

function Icon({ children, ...rest }: IconProps & { children: ReactNode }) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      focusable="false"
      height="20"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      viewBox="0 0 24 24"
      width="20"
      {...rest}
    >
      {children}
    </svg>
  )
}

export function EyeIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </Icon>
  )
}

export function EyeOffIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M10.6 5.1A10.6 10.6 0 0 1 12 5c6.4 0 10 7 10 7a17.6 17.6 0 0 1-3 3.9" />
      <path d="M6.5 6.6C3.6 8.5 2 12 2 12s3.6 7 10 7a10 10 0 0 0 5.4-1.6" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
      <path d="m3 3 18 18" />
    </Icon>
  )
}

export function LockIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <rect height="10" rx="2" width="16" x="4" y="11" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </Icon>
  )
}

export function ArrowLeftIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M19 12H5" />
      <path d="m11 6-6 6 6 6" />
    </Icon>
  )
}

export function CheckCircleIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12.5 2.8 2.8L16 9.8" />
    </Icon>
  )
}

export function MailIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <rect height="14" rx="2" width="18" x="3" y="5" />
      <path d="m3.5 7 8.5 6 8.5-6" />
    </Icon>
  )
}

export function AlertCircleIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5.5" />
      <path d="M12 16.5h.01" />
    </Icon>
  )
}

export function CircleIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="9" />
    </Icon>
  )
}
