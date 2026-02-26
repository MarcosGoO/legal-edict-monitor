import { clsx } from 'clsx'

type StatusVariant = 'success' | 'error' | 'warning' | 'neutral'

const variantClasses: Record<StatusVariant, string> = {
  success: 'bg-emerald-100 text-emerald-700',
  error: 'bg-red-100 text-red-700',
  warning: 'bg-amber-100 text-amber-700',
  neutral: 'bg-slate-100 text-slate-600',
}

const dotClasses: Record<StatusVariant, string> = {
  success: 'bg-emerald-500',
  error: 'bg-red-500',
  warning: 'bg-amber-500',
  neutral: 'bg-slate-400',
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
      {dot && (
        <span className={clsx('w-1.5 h-1.5 rounded-full flex-shrink-0', dotClasses[variant])} />
      )}
      {label}
    </span>
  )
}
