import { useNavigate } from 'react-router-dom'
import { Pencil, Trash2, ChevronRight, Users } from 'lucide-react'
import { clsx } from 'clsx'
import type { ClientResponse } from '../../../types/api'
import MonoValue from '../../../components/ui/MonoValue'
import StatusBadge from '../../../components/ui/StatusBadge'
import EmptyState from '../../../components/ui/EmptyState'
import { formatDocumentType } from '../../../utils/formatters'

interface ClientTableProps {
  clients: ClientResponse[]
  onDelete: (client: ClientResponse) => void
}

export default function ClientTable({ clients, onDelete }: ClientTableProps) {
  const navigate = useNavigate()

  if (clients.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="No hay clientes registrados"
        description="Registra el primer cliente para empezar a monitorear edictos."
        action={
          <button
            onClick={() => navigate('/clients/new')}
            className="px-4 py-2 bg-gold-500 text-ink-950 text-sm font-medium rounded-lg hover:bg-gold-400 transition-colors"
          >
            Agregar primer cliente
          </button>
        }
      />
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-ink-700/40">
            {['Nombre', 'Tipo doc.', 'Número', 'NIT', 'Aliases', 'Estado', ''].map((h) => (
              <th
                key={h}
                className="px-3 py-3 text-left text-xs font-semibold text-ink-600 uppercase tracking-wider whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr
              key={client.id}
              onClick={() => navigate(`/clients/${client.id}`)}
              className={clsx(
                'border-b border-ink-700/30 cursor-pointer transition-colors',
                'hover:bg-ink-800/60 group',
              )}
            >
              <td className="px-3 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-gold-900 border border-gold-500/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-semibold text-gold-400">
                      {client.full_name.charAt(0)}
                    </span>
                  </div>
                  <span className="font-medium text-parchment/90 line-clamp-1">
                    {client.full_name}
                  </span>
                </div>
              </td>

              <td className="px-3 py-3 text-ink-600">
                {formatDocumentType(client.document_type)}
              </td>

              <td className="px-3 py-3">
                <MonoValue value={client.document_number} />
              </td>

              <td className="px-3 py-3">
                <MonoValue value={client.nit} />
              </td>

              <td className="px-3 py-3">
                <AliasCells aliases={client.aliases} />
              </td>

              <td className="px-3 py-3">
                <StatusBadge
                  variant={client.is_active ? 'success' : 'neutral'}
                  label={client.is_active ? 'Activo' : 'Inactivo'}
                />
              </td>

              {/* Actions */}
              <td className="px-3 py-3">
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); navigate(`/clients/${client.id}/edit`) }}
                    className="p-1.5 rounded-md text-ink-600 hover:text-gold-400 hover:bg-gold-900/60 transition-colors"
                    aria-label="Editar"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDelete(client) }}
                    className="p-1.5 rounded-md text-ink-600 hover:text-red-500 hover:bg-red-950/40 transition-colors"
                    aria-label="Eliminar"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <ChevronRight className="w-3.5 h-3.5 text-ink-700" />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AliasCells({ aliases }: { aliases: string[] }) {
  if (aliases.length === 0) return <span className="text-ink-600 text-xs">—</span>
  const visible = aliases.slice(0, 2)
  const rest = aliases.length - 2
  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((a) => (
        <span key={a} className="px-1.5 py-0.5 bg-ink-800 text-ink-600 border border-ink-700/40 rounded text-xs">
          {a}
        </span>
      ))}
      {rest > 0 && (
        <span className="px-1.5 py-0.5 bg-ink-800 text-ink-600 border border-ink-700/40 rounded text-xs">+{rest}</span>
      )}
    </div>
  )
}
