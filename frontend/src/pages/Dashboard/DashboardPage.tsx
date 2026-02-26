import { Bell } from 'lucide-react'
import StatusCard from './components/StatusCard'
import QuickStats from './components/QuickStats'
import QuickActions from './components/QuickActions'
import { Card, CardBody } from '../../components/ui/Card'
import EmptyState from '../../components/ui/EmptyState'

export default function DashboardPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Panel de Control</h2>
        <p className="text-sm text-slate-500 mt-0.5">
          Monitoreo de edictos legales colombianos
        </p>
      </div>

      {/* Stats row */}
      <QuickStats />

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Quick actions — 2 cols */}
        <div className="lg:col-span-2 space-y-2">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
            Acciones rápidas
          </p>
          <QuickActions />
        </div>

        {/* System status — 1 col */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
            Servicios
          </p>
          <StatusCard />
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div className="space-y-2">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
          Actividad reciente
        </p>
        <Card>
          <CardBody>
            <EmptyState
              icon={Bell}
              title="Sin actividad reciente"
              description="Los edictos detectados y alertas aparecerán aquí cuando el módulo de monitoreo esté activo."
            />
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
