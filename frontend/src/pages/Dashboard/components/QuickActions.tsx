import { useNavigate } from 'react-router-dom'
import { FileText, UserPlus, ArrowRight } from 'lucide-react'

interface ActionCardProps {
  icon: React.ElementType
  title: string
  description: string
  onClick: () => void
}

function ActionCard({ icon: Icon, title, description, onClick }: ActionCardProps) {
  return (
    <button
      onClick={onClick}
      className="group flex-1 min-w-[200px] bg-ink-900 border border-ink-700/60 rounded-xl p-5 text-left card-gold-hover"
    >
      <div className="w-10 h-10 rounded-lg bg-gold-500 flex items-center justify-center mb-3">
        <Icon className="w-5 h-5 text-ink-950" />
      </div>
      <p className="text-sm font-semibold text-parchment mb-1">{title}</p>
      <p className="text-xs text-ink-600 leading-relaxed">{description}</p>
      <div className="flex items-center gap-1 mt-3 text-gold-500 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
        Ir ahora <ArrowRight className="w-3 h-3" />
      </div>
    </button>
  )
}

export default function QuickActions() {
  const navigate = useNavigate()

  return (
    <div className="flex gap-4 flex-wrap">
      <ActionCard
        icon={FileText}
        title="Procesar Documento"
        description="Sube un PDF o pega texto para extraer entidades legales colombianas."
        onClick={() => navigate('/documents')}
      />
      <ActionCard
        icon={UserPlus}
        title="Agregar Cliente"
        description="Registra un nuevo cliente para monitorear en edictos y gacetas."
        onClick={() => navigate('/clients/new')}
      />
    </div>
  )
}
