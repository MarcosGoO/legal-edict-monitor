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
    <aside className="h-full w-60 bg-brand-900 flex flex-col">
      <div className="flex items-center justify-between px-5 py-5 border-b border-brand-800">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand-100 flex-shrink-0" />
          <span className="text-white font-semibold text-sm tracking-tight">
            Edict Guardian
          </span>
        </div>
        {/* Close button — only visible on mobile */}
        <button
          onClick={onClose}
          className="md:hidden text-slate-400 hover:text-white p-1 rounded"
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
                  ? 'bg-brand-700 text-white'
                  : 'text-slate-400 hover:bg-brand-800 hover:text-white',
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={clsx(
                    'w-0.5 h-4 rounded-full flex-shrink-0',
                    isActive ? 'bg-brand-500' : 'bg-transparent',
                  )}
                />
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-brand-800">
        <p className="text-xs text-slate-600">v0.1.0 · Colombia</p>
      </div>
    </aside>
  )
}
