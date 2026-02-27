import { useLocation, Link } from 'react-router-dom'
import { Menu, ChevronRight } from 'lucide-react'

interface Crumb {
  label: string
  to?: string
}

function useBreadcrumbs(): Crumb[] {
  const { pathname } = useLocation()
  const segments = pathname.split('/').filter(Boolean)

  if (segments.length === 0) return [{ label: 'Inicio' }]

  const crumbs: Crumb[] = [{ label: 'Inicio', to: '/' }]

  const labels: Record<string, string> = {
    clients: 'Clientes',
    new: 'Nuevo',
    edit: 'Editar',
    documents: 'Documentos',
  }

  segments.forEach((seg, i) => {
    const isLast = i === segments.length - 1
    const label = labels[seg] ?? seg
    const to = '/' + segments.slice(0, i + 1).join('/')
    crumbs.push(isLast ? { label } : { label, to })
  })

  return crumbs
}

interface TopBarProps {
  onMenuClick: () => void
}

export default function TopBar({ onMenuClick }: TopBarProps) {
  const crumbs = useBreadcrumbs()

  return (
    <header className="h-14 bg-ink-900 border-b border-ink-700/50 flex items-center px-4 gap-3 flex-shrink-0">
      {/* Hamburger — only on mobile */}
      <button
        onClick={onMenuClick}
        className="md:hidden p-1.5 rounded-md text-ink-600 hover:bg-ink-800"
        aria-label="Abrir menú"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm">
        {crumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1">
            {i > 0 && <ChevronRight className="w-3.5 h-3.5 text-ink-600" />}
            {crumb.to ? (
              <Link
                to={crumb.to}
                className="text-ink-600 hover:text-parchment transition-colors"
              >
                {crumb.label}
              </Link>
            ) : (
              <span className="text-parchment font-semibold">{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>
    </header>
  )
}
