import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus } from 'lucide-react'
import { Card, CardBody } from '../../components/ui/Card'
import Pagination from '../../components/ui/Pagination'
import ConfirmDialog from '../../components/ui/ConfirmDialog'
import { FullPageSpinner } from '../../components/ui/LoadingSpinner'
import ClientFilters from './components/ClientFilters'
import ClientTable from './components/ClientTable'
import { useClientList, useDeleteClient } from '../../hooks/useClients'
import type { ClientResponse } from '../../types/api'

type ActiveFilter = 'all' | 'active' | 'inactive'

export default function ClientListPage() {
  const navigate = useNavigate()

  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [activeFilter, setActiveFilter] = useState<ActiveFilter>('all')
  const [toDelete, setToDelete] = useState<ClientResponse | null>(null)

  const isActiveParam =
    activeFilter === 'active' ? true : activeFilter === 'inactive' ? false : undefined

  const { data, isLoading } = useClientList({
    page,
    page_size: pageSize,
    search: search || undefined,
    is_active: isActiveParam,
  })

  const deleteMutation = useDeleteClient()

  const handleSearchChange = (v: string) => {
    setSearch(v)
    setPage(1)
  }

  const handleFilterChange = (v: ActiveFilter) => {
    setActiveFilter(v)
    setPage(1)
  }

  const handleDeleteConfirm = async () => {
    if (!toDelete) return
    await deleteMutation.mutateAsync(toDelete.id)
    setToDelete(null)
  }

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Clientes</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {data ? `${data.total} cliente${data.total !== 1 ? 's' : ''} registrados` : 'Cargando…'}
          </p>
        </div>
        <button
          onClick={() => navigate('/clients/new')}
          className="flex items-center gap-2 px-4 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
        >
          <UserPlus className="w-4 h-4" />
          Nuevo cliente
        </button>
      </div>

      {/* Filters */}
      <ClientFilters
        search={search}
        activeFilter={activeFilter}
        onSearchChange={handleSearchChange}
        onActiveFilterChange={handleFilterChange}
      />

      {/* Table */}
      <Card>
        <CardBody className="p-0">
          {isLoading ? (
            <FullPageSpinner />
          ) : (
            <div className="px-2">
              <ClientTable
                clients={data?.clients ?? []}
                onDelete={setToDelete}
              />
              {(data?.total ?? 0) > 0 && (
                <div className="px-3">
                  <Pagination
                    page={page}
                    pageSize={pageSize}
                    total={data?.total ?? 0}
                    onPageChange={setPage}
                    onPageSizeChange={(s) => { setPageSize(s); setPage(1) }}
                  />
                </div>
              )}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Delete confirmation */}
      <ConfirmDialog
        open={!!toDelete}
        title="¿Eliminar cliente?"
        description={`Se eliminará "${toDelete?.full_name}" y toda su configuración de vigilancia. Esta acción no se puede deshacer.`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setToDelete(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
