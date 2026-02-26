import { NavLink } from 'react-router-dom'
import { Home, Users, FileText, Shield } from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { to: '/', icon: Home, label: 'Inicio' },
  { to: '/clients', icon: Users, label: 'Clientes' },
  { to: '/documents', icon: FileText, label: 'Documentos' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 flex-shrink-0 bg-brand-900 flex flex-col">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-brand-800">
        <Shield className="w-6 h-6 text-brand-100" />
        <span className="text-white font-semibold text-base tracking-tight">
          Edict Guardian
        </span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-800 text-white border-l-2 border-brand-500'
                  : 'text-slate-300 hover:bg-brand-800 hover:text-white',
              )
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 border-t border-brand-800">
        <p className="text-xs text-slate-500">v0.1.0 · Colombia 🇨🇴</p>
      </div>
    </aside>
  )
}
