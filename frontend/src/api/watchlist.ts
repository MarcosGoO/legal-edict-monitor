import apiClient from './client'
import type { WatchlistCreate, WatchlistResponse } from '../types/api'

export async function getWatchlist(clientId: string): Promise<WatchlistResponse[]> {
  const { data } = await apiClient.get<WatchlistResponse[]>(
    `/api/v1/clients/${clientId}/watchlist`,
  )
  return data
}

export async function createWatchlistEntry(
  clientId: string,
  payload: WatchlistCreate,
): Promise<WatchlistResponse> {
  const { data } = await apiClient.post<WatchlistResponse>(
    `/api/v1/clients/${clientId}/watchlist`,
    payload,
  )
  return data
}
