import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getWatchlist, createWatchlistEntry } from '../api/watchlist'
import type { WatchlistCreate } from '../types/api'

export function useWatchlist(clientId: string) {
  return useQuery({
    queryKey: ['watchlist', clientId],
    queryFn: () => getWatchlist(clientId),
    enabled: !!clientId,
  })
}

export function useCreateWatchlistEntry(clientId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: WatchlistCreate) => createWatchlistEntry(clientId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['watchlist', clientId] }),
  })
}
