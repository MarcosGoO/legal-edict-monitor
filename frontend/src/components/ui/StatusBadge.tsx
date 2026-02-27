import { clsx } from 'clsx'

type StatusVariant = 'success' | 'error' | 'warning' | 'neutral'

const variantClasses: Record<StatusVariant, string> = {
  success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  error:   'bg-red-50 text-red-600 border border-red-200',
  warning: 'bg-amber-50 text-amber-700 border border-amber-200',
  neutral: 'bg-slate-100 text-slate-600 border border-slate-200',
}

const dotClasses: Record<StatusVariant, string> = {
  success: 'dot-glow-green',
  error:   'dot-glow-red',
  warning: 'bg-amber-500 w-1.5 h-1.5 rounded-full flex-shrink-0',
  neutral: 'bg-slate-400 w-1.5 h-1.5 rounded-full flex-shrink-0',
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
