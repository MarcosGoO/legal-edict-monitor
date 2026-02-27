import { clsx } from 'clsx'
import type { ReactNode } from 'react'

interface CardProps {
  className?: string
  children: ReactNode
}

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-ink-900 rounded-xl border border-ink-700/60 shadow-[0_2px_12px_rgba(0,0,0,0.07)] card-gold-hover',
        className,
      )}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  title: string
  description?: string
  action?: ReactNode
}

export function CardHeader({ title, description, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between px-5 pt-5 pb-4 border-b border-ink-700/40">
      <div>
        <h3 className="text-sm font-semibold text-parchment">{title}</h3>
        {description && <p className="text-xs text-ink-600 mt-0.5">{description}</p>}
      </div>
      {action && <div className="ml-4 flex-shrink-0">{action}</div>}
    </div>
  )
}

export function CardBody({ className, children }: CardProps) {
  return <div className={clsx('px-5 py-4', className)}>{children}</div>
}
