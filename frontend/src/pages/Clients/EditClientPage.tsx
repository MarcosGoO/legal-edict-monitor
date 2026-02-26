import { useNavigate, useParams } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardBody } from '../../components/ui/Card'
import ClientForm from './components/ClientForm'
import { FullPageSpinner } from '../../components/ui/LoadingSpinner'
import EmptyState from '../../components/ui/EmptyState'
import { useClient, useUpdateClient } from '../../hooks/useClients'
import { useToast } from '../../components/ui/Toast'
import type { ClientCreate } from '../../types/api'

export default function EditClientPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: client, isLoading, isError } = useClient(id!)
  const mutation = useUpdateClient(id!)

  const handleSubmit = async (data: ClientCreate) => {
    try {
      await mutation.mutateAsync(data)
      toast('Cambios guardados correctamente', 'success')
      navigate(`/clients/${id}`)
    } catch (err) {
      toast((err as Error)?.message ?? 'Error al guardar los cambios', 'error')
    }
  }

  if (isLoading) return <FullPageSpinner />

  if (isError || !client) {
    return (
      <EmptyState
        icon={AlertCircle}
        title="Cliente no encontrado"
        description="El cliente solicitado no existe o no está disponible."
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

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Editar Cliente</h2>
        <p className="text-sm text-slate-500 mt-0.5">{client.full_name}</p>
      </div>
      <Card>
        <CardHeader title="Datos del cliente" />
        <CardBody>
          <ClientForm defaultValues={client} onSubmit={handleSubmit} isLoading={mutation.isPending} />
        </CardBody>
      </Card>
    </div>
  )
}
