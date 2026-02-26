import apiClient from './client'
import type {
  ClientCreate,
  ClientListParams,
  ClientListResponse,
  ClientResponse,
} from '../types/api'

export async function listClients(params: ClientListParams = {}): Promise<ClientListResponse> {
  const { data } = await apiClient.get<ClientListResponse>('/api/v1/clients', { params })
  return data
}

export async function getClient(id: string): Promise<ClientResponse> {
  const { data } = await apiClient.get<ClientResponse>(`/api/v1/clients/${id}`)
  return data
}

export async function createClient(payload: ClientCreate): Promise<ClientResponse> {
  const { data } = await apiClient.post<ClientResponse>('/api/v1/clients', payload)
  return data
}

export async function updateClient(id: string, payload: ClientCreate): Promise<ClientResponse> {
  const { data } = await apiClient.put<ClientResponse>(`/api/v1/clients/${id}`, payload)
  return data
}

export async function deleteClient(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/clients/${id}`)
}
