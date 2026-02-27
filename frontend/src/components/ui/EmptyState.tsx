import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-ink-800 border border-ink-700/40 flex items-center justify-center mb-3">
        <Icon className="w-6 h-6 text-ink-600" />
      </div>
      <p className="text-sm font-semibold text-parchment/70">{title}</p>
      {description && <p className="text-xs text-ink-600 mt-1 max-w-xs">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
