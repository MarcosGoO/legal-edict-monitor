import { NavLink } from 'react-router-dom'
import { Home, Users, FileText, Shield, X } from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { to: '/', icon: Home, label: 'Inicio' },
  { to: '/clients', icon: Users, label: 'Clientes' },
  { to: '/documents', icon: FileText, label: 'Documentos' },
]

interface SidebarProps {
  onClose?: () => void
}

export default function Sidebar({ onClose }: SidebarProps) {
  return (
    <aside className="h-full w-64 bg-ink-950 border-r border-ink-700/50 flex flex-col">
      <div className="flex items-center justify-between px-5 py-5 border-b border-ink-700/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-gold-900 border border-gold-500/30 flex items-center justify-center flex-shrink-0">
            <Shield className="w-4 h-4 text-gold-500" />
          </div>
          <div>
            <span className="font-display text-parchment font-semibold text-sm tracking-tight block">
              Edict Guardian
            </span>
            <span className="text-xs text-ink-600">Colombia</span>
          </div>
        </div>
        {/* Close button — only visible on mobile */}
        <button
          onClick={onClose}
          className="md:hidden text-ink-600 hover:text-parchment p-1 rounded"
          aria-label="Cerrar menú"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onClose}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-ink-800 text-parchment'
                  : 'text-ink-600 hover:bg-ink-800 hover:text-parchment',
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={clsx(
                    'w-0.5 h-4 rounded-full flex-shrink-0 transition-all',
                    isActive
                      ? 'bg-gold-500 shadow-[0_0_6px_rgba(212,168,67,0.6)]'
                      : 'bg-transparent',
                  )}
                />
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-ink-700/50">
        <p className="text-xs text-ink-600">v0.1.0 · Colombia</p>
      </div>
    </aside>
  )
}
