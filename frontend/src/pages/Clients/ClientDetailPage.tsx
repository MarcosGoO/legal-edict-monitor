import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import * as Tabs from '@radix-ui/react-tabs'
import { Pencil, Plus, ShieldAlert, Eye, List } from 'lucide-react'
import { Card, CardBody } from '../../components/ui/Card'
import StatusBadge from '../../components/ui/StatusBadge'
import MonoValue from '../../components/ui/MonoValue'
import EmptyState from '../../components/ui/EmptyState'
import { FullPageSpinner } from '../../components/ui/LoadingSpinner'
import WatchlistEntryCard from './components/WatchlistEntryCard'
import AddWatchlistDialog from './components/AddWatchlistDialog'
import { useClient } from '../../hooks/useClients'
import { useWatchlist, useCreateWatchlistEntry } from '../../hooks/useWatchlist'
import { formatDocumentType } from '../../utils/formatters'
export default function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: client, isLoading, isError } = useClient(id!)
  const { data: watchlist, isLoading: watchlistLoading } = useWatchlist(id!)
  const createWatchlist = useCreateWatchlistEntry(id!)

  const [dialogOpen, setDialogOpen] = useState(false)

  if (isLoading) return <FullPageSpinner />

  if (isError || !client) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="Cliente no encontrado"
        description="El cliente no existe o fue eliminado."
        action={
          <button
            onClick={() => navigate('/clients')}
            className="px-4 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg"
          >
            Volver a clientes
          </button>
        }
      />
    )
  }

  const infoRows: { label: string; value: React.ReactNode }[] = [
    { label: 'Nombre completo', value: <span className="font-medium text-slate-800">{client.full_name}</span> },
    { label: 'Tipo de documento', value: formatDocumentType(client.document_type) },
    { label: 'Número', value: <MonoValue value={client.document_number} copyable /> },
    { label: 'NIT', value: <MonoValue value={client.nit} copyable /> },
    {
      label: 'Aliases',
      value: client.aliases.length > 0
        ? <div className="flex flex-wrap gap-1">
            {client.aliases.map((a) => (
              <span key={a} className="px-2 py-0.5 bg-brand-100 text-brand-800 rounded text-xs font-medium">{a}</span>
            ))}
          </div>
        : <span className="text-slate-400 text-sm">Sin aliases</span>,
    },
  ]

  const tabTriggerCls =
    'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ' +
    'border-transparent text-slate-500 hover:text-slate-700 ' +
    'data-[state=active]:border-brand-500 data-[state=active]:text-brand-600'

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-xl font-bold text-slate-800">{client.full_name}</h2>
            <StatusBadge
              variant={client.is_active ? 'success' : 'neutral'}
              label={client.is_active ? 'Activo' : 'Inactivo'}
            />
          </div>
          {client.document_type && client.document_number && (
            <p className="text-sm text-slate-500">
              {formatDocumentType(client.document_type)}{' '}
              <MonoValue value={client.document_number} />
            </p>
          )}
        </div>
        <button
          onClick={() => navigate(`/clients/${id}/edit`)}
          className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex-shrink-0"
        >
          <Pencil className="w-3.5 h-3.5" />
          Editar
        </button>
      </div>

      {/* Tabs */}
      <Tabs.Root defaultValue="info">
        <Tabs.List className="flex border-b border-slate-200">
          <Tabs.Trigger value="info" className={`focus:outline-none ${tabTriggerCls}`}>
            Información
          </Tabs.Trigger>
          <Tabs.Trigger value="watchlist" className={`focus:outline-none ${tabTriggerCls}`}>
            Lista de vigilancia
            {(watchlist?.length ?? 0) > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 bg-brand-100 text-brand-700 text-xs rounded-full">
                {watchlist!.length}
              </span>
            )}
          </Tabs.Trigger>
          <Tabs.Trigger value="edicts" className={`focus:outline-none ${tabTriggerCls}`}>
            Edictos detectados
          </Tabs.Trigger>
        </Tabs.List>

        {/* Tab: Info */}
        <Tabs.Content value="info">
          <Card className="mt-4">
            <CardBody>
              <dl className="divide-y divide-slate-100">
                {infoRows.map(({ label, value }) => (
                  <div key={label} className="flex gap-4 py-3 text-sm">
                    <dt className="w-40 flex-shrink-0 text-slate-500">{label}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
              </dl>
            </CardBody>
          </Card>
        </Tabs.Content>

        {/* Tab: Watchlist */}
        <Tabs.Content value="watchlist">
          <div className="mt-4 space-y-3">
            <div className="flex justify-end">
              <button
                onClick={() => setDialogOpen(true)}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-brand-500 rounded-lg hover:bg-brand-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Agregar vigilancia
              </button>
            </div>

            {watchlistLoading ? (
              <FullPageSpinner />
            ) : (watchlist?.length ?? 0) === 0 ? (
              <Card>
                <CardBody>
                  <EmptyState
                    icon={List}
                    title="Sin configuración de vigilancia"
                    description="Agrega radicados o despachos para que el sistema alerte cuando aparezcan en edictos."
                    action={
                      <button
                        onClick={() => setDialogOpen(true)}
                        className="px-4 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg"
                      >
                        Agregar vigilancia
                      </button>
                    }
                  />
                </CardBody>
              </Card>
            ) : (
              <div className="space-y-3">
                {watchlist!.map((entry) => (
                  <WatchlistEntryCard key={entry.id} entry={entry} />
                ))}
              </div>
            )}
          </div>
        </Tabs.Content>

        {/* Tab: Edicts (future) */}
        <Tabs.Content value="edicts">
          <Card className="mt-4">
            <CardBody>
              <EmptyState
                icon={Eye}
                title="Módulo en desarrollo"
                description="Los edictos detectados para este cliente aparecerán aquí cuando el módulo de monitoreo esté activo."
              />
            </CardBody>
          </Card>
        </Tabs.Content>
      </Tabs.Root>

      <AddWatchlistDialog
        clientId={id!}
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={async (data) => { await createWatchlist.mutateAsync(data) }}
        isLoading={createWatchlist.isPending}
      />
    </div>
  )
}
