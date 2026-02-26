import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listClients, getClient, createClient, updateClient, deleteClient } from '../api/clients'
import type { ClientCreate, ClientListParams } from '../types/api'

export function useClientList(params: ClientListParams = {}) {
  return useQuery({
    queryKey: ['clients', params],
    queryFn: () => listClients(params),
  })
}

export function useClient(id: string) {
  return useQuery({
    queryKey: ['clients', id],
    queryFn: () => getClient(id),
    enabled: !!id,
  })
}

export function useCreateClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ClientCreate) => createClient(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })
}

export function useUpdateClient(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ClientCreate) => updateClient(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })
}

export function useDeleteClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteClient(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })
}
