import { Users, UserCheck } from 'lucide-react'
import { Card, CardBody } from '../../../components/ui/Card'
import LoadingSpinner from '../../../components/ui/LoadingSpinner'
import { useClientList } from '../../../hooks/useClients'

interface StatItemProps {
  icon: React.ElementType
  label: string
  value: string | number
  loading: boolean
}

function StatItem({ icon: Icon, label, value, loading }: StatItemProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg bg-gold-500 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-ink-950" />
      </div>
      <div>
        <p className="text-xs text-ink-600 uppercase tracking-[0.12em]">{label}</p>
        {loading ? (
          <LoadingSpinner size="sm" className="mt-1" />
        ) : (
          <p className="font-display text-4xl font-bold text-parchment leading-none mt-0.5">{value}</p>
        )}
      </div>
    </div>
  )
}

export default function QuickStats() {
  const all = useClientList({ page_size: 1 })
  const active = useClientList({ page_size: 1, is_active: true })

  return (
    <Card>
      <CardBody className="flex gap-6 flex-wrap">
        <StatItem
          icon={Users}
          label="Clientes totales"
          value={all.data?.total ?? 0}
          loading={all.isLoading}
        />
        <div className="w-px bg-ink-700 self-stretch hidden sm:block" />
        <StatItem
          icon={UserCheck}
          label="Clientes activos"
          value={active.data?.total ?? 0}
          loading={active.isLoading}
        />
      </CardBody>
    </Card>
  )
}
