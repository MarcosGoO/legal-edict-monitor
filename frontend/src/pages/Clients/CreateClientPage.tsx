import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardBody } from '../../components/ui/Card'
import ClientForm from './components/ClientForm'
import { useCreateClient } from '../../hooks/useClients'
import { useToast } from '../../components/ui/Toast'
import type { ClientCreate } from '../../types/api'

export default function CreateClientPage() {
  const navigate = useNavigate()
  const mutation = useCreateClient()
  const { toast } = useToast()

  const handleSubmit = async (data: ClientCreate) => {
    try {
      const created = await mutation.mutateAsync(data)
      toast('Cliente creado correctamente', 'success')
      navigate(`/clients/${created.id}`)
    } catch (err) {
      toast((err as Error)?.message ?? 'Error al crear el cliente', 'error')
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Nuevo Cliente</h2>
        <p className="text-sm text-slate-500 mt-0.5">
          Registra una persona o empresa para monitorear en edictos.
        </p>
      </div>
      <Card>
        <CardHeader title="Datos del cliente" />
        <CardBody>
          <ClientForm onSubmit={handleSubmit} isLoading={mutation.isPending} />
        </CardBody>
      </Card>
    </div>
  )
}
