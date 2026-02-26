import { useQuery } from '@tanstack/react-query'
import { getHealth, getReady } from '../api/health'

export function useSystemHealth() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    refetchInterval: 30_000,
    retry: 1,
  })

  const ready = useQuery({
    queryKey: ['ready'],
    queryFn: getReady,
    refetchInterval: 30_000,
    retry: 1,
  })

  const apiOk = health.isSuccess
  const dbOk = ready.isSuccess && ready.data.checks.database === 'ok'
  const redisOk = ready.isSuccess && ready.data.checks.redis === 'ok'

  return {
    apiOk,
    dbOk,
    redisOk,
    isLoading: health.isLoading || ready.isLoading,
    refetch: () => {
      health.refetch()
      ready.refetch()
    },
  }
}
