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
            className="px-4 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
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
          <tr className="border-b border-slate-200">
            {['Nombre', 'Tipo doc.', 'Número', 'NIT', 'Aliases', 'Estado', ''].map((h) => (
              <th
                key={h}
                className="px-3 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap"
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
                'border-b border-slate-100 cursor-pointer transition-colors',
                'hover:bg-slate-50 group',
              )}
            >
              <td className="px-3 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-semibold text-brand-700">
                      {client.full_name.charAt(0)}
                    </span>
                  </div>
                  <span className="font-medium text-slate-800 line-clamp-1">
                    {client.full_name}
                  </span>
                </div>
              </td>

              <td className="px-3 py-3 text-slate-500">
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
                    className="p-1.5 rounded-md text-slate-400 hover:text-brand-500 hover:bg-brand-100 transition-colors"
                    aria-label="Editar"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDelete(client) }}
                    className="p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                    aria-label="Eliminar"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
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
  if (aliases.length === 0) return <span className="text-slate-400 text-xs">—</span>
  const visible = aliases.slice(0, 2)
  const rest = aliases.length - 2
  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((a) => (
        <span key={a} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-xs">
          {a}
        </span>
      ))}
      {rest > 0 && (
        <span className="px-1.5 py-0.5 bg-slate-100 text-slate-400 rounded text-xs">+{rest}</span>
      )}
    </div>
  )
}
