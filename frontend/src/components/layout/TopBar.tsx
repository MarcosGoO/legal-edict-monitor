import { useLocation } from 'react-router-dom'

const routeLabels: Record<string, string> = {
  '/': 'Inicio',
  '/clients': 'Clientes',
  '/clients/new': 'Nuevo Cliente',
  '/documents': 'Documentos',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const label = routeLabels[pathname] ?? 'Edict Guardian'

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center px-6 flex-shrink-0">
      <h1 className="text-sm font-semibold text-slate-700">{label}</h1>
    </header>
  )
}
