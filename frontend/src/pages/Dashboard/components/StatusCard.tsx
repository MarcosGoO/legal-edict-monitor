import { RefreshCw, Wifi, Database, Zap } from 'lucide-react'
import { Card, CardHeader, CardBody } from '../../../components/ui/Card'
import StatusBadge from '../../../components/ui/StatusBadge'
import LoadingSpinner from '../../../components/ui/LoadingSpinner'
import { useSystemHealth } from '../../../hooks/useSystemHealth'

interface ServiceRowProps {
  icon: React.ElementType
  name: string
  ok: boolean
  loading: boolean
}

function ServiceRow({ icon: Icon, name, ok, loading }: ServiceRowProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center">
          <Icon className="w-3.5 h-3.5 text-slate-500" />
        </div>
        <span className="text-sm text-slate-700">{name}</span>
      </div>
      {loading ? (
        <LoadingSpinner size="sm" />
      ) : (
        <StatusBadge
          variant={ok ? 'success' : 'error'}
          label={ok ? 'Operativo' : 'Sin conexión'}
        />
      )}
    </div>
  )
}

export default function StatusCard() {
  const { apiOk, dbOk, redisOk, isLoading, refetch } = useSystemHealth()

  return (
    <Card>
      <CardHeader
        title="Estado del Sistema"
        description="Actualización automática cada 30s"
        action={
          <button
            onClick={refetch}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            aria-label="Actualizar"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        }
      />
      <CardBody className="py-1">
        <ServiceRow icon={Wifi} name="API" ok={apiOk} loading={isLoading} />
        <ServiceRow icon={Database} name="Base de Datos" ok={dbOk} loading={isLoading} />
        <ServiceRow icon={Zap} name="Caché (Redis)" ok={redisOk} loading={isLoading} />
      </CardBody>
    </Card>
  )
}
