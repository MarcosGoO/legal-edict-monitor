import { clsx } from 'clsx'

type StatusVariant = 'success' | 'error' | 'warning' | 'neutral'

const variantClasses: Record<StatusVariant, string> = {
  success: 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40',
  error:   'bg-red-950/60 text-red-400 border border-red-800/40',
  warning: 'bg-amber-950/60 text-amber-400 border border-amber-800/40',
  neutral: 'bg-ink-800 text-ink-600 border border-ink-700/40',
}

const dotClasses: Record<StatusVariant, string> = {
  success: 'dot-glow-green',
  error:   'dot-glow-red',
  warning: 'bg-amber-400 w-1.5 h-1.5 rounded-full flex-shrink-0',
  neutral: 'bg-ink-600 w-1.5 h-1.5 rounded-full flex-shrink-0',
}

interface StatusBadgeProps {
  variant: StatusVariant
  label: string
  dot?: boolean
  className?: string
}

export default function StatusBadge({ variant, label, dot = true, className }: StatusBadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        variantClasses[variant],
        className,
      )}
    >
      {dot && <span className={dotClasses[variant]} />}
      {label}
    </span>
  )
}
