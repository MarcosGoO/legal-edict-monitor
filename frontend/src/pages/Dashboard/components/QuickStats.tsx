import { Users, UserCheck } from 'lucide-react'
import { Card, CardBody } from '../../../components/ui/Card'
import LoadingSpinner from '../../../components/ui/LoadingSpinner'
import { useClientList } from '../../../hooks/useClients'

interface StatItemProps {
  icon: React.ElementType
  label: string
  value: string | number
  loading: boolean
  color: string
}

function StatItem({ icon: Icon, label, value, loading, color }: StatItemProps) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        {loading ? (
          <LoadingSpinner size="sm" className="mt-1" />
        ) : (
          <p className="text-xl font-bold text-slate-800">{value}</p>
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
          color="bg-brand-500"
        />
        <div className="w-px bg-slate-200 self-stretch hidden sm:block" />
        <StatItem
          icon={UserCheck}
          label="Clientes activos"
          value={active.data?.total ?? 0}
          loading={active.isLoading}
          color="bg-emerald-500"
        />
      </CardBody>
    </Card>
  )
}
