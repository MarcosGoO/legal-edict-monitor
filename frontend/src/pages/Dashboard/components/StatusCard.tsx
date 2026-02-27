import { RefreshCw, Wifi, Database, Zap } from 'lucide-react'
import { Card, CardHeader, CardBody } from '../../../components/ui/Card'
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
    <div className="flex items-center justify-between py-3 border-b border-ink-700/40 last:border-0">
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-md bg-ink-800 flex items-center justify-center">
          <Icon className="w-3.5 h-3.5 text-ink-600" />
        </div>
        <span className="text-sm text-parchment/80">{name}</span>
      </div>
      {loading ? (
        <LoadingSpinner size="sm" />
      ) : (
        <div className="flex items-center gap-2">
          <span
            className={[
              'w-2 h-2 rounded-full flex-shrink-0 animate-dot-pulse',
              ok ? 'dot-glow-green' : 'dot-glow-red',
            ].join(' ')}
          />
          <span className={`text-xs font-medium ${ok ? 'text-emerald-400' : 'text-red-400'}`}>
            {ok ? 'Operativo' : 'Sin conexión'}
          </span>
        </div>
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
            className="p-1.5 rounded-md text-ink-600 hover:text-gold-500 hover:bg-ink-800 transition-colors"
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
