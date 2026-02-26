import apiClient from './client'
import type {
  DocumentProcessResponse,
  EntityTypesResponse,
  TextParseResponse,
} from '../types/api'

export async function processDocument(file: File): Promise<DocumentProcessResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await apiClient.post<DocumentProcessResponse>(
    '/api/v1/documents/process',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function parseText(text: string): Promise<TextParseResponse> {
  const { data } = await apiClient.post<TextParseResponse>(
    '/api/v1/documents/parse-text',
    { text },
  )
  return data
}

export async function getEntityTypes(): Promise<EntityTypesResponse> {
  const { data } = await apiClient.get<EntityTypesResponse>(
    '/api/v1/documents/entity-types',
  )
  return data
}
