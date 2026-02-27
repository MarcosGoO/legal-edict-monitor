import { clsx } from 'clsx'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-[3px]',
}

export default function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <div
      className={clsx(
        'rounded-full border-ink-700 border-t-gold-500 animate-spin',
        sizeClasses[size],
        className,
      )}
      role="status"
      aria-label="Cargando"
    />
  )
}

export function FullPageSpinner() {
  return (
    <div className="flex items-center justify-center h-40">
      <LoadingSpinner size="lg" />
    </div>
  )
}
