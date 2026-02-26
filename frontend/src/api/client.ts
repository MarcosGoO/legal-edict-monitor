import axios from 'axios'
import type { APIError } from '../types/api'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60_000,
})

// Response interceptor: normalize FastAPI error shapes
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response) {
      const data = error.response.data as APIError
      const detail = data?.detail
      if (typeof detail === 'string') {
        error.message = detail
      } else if (Array.isArray(detail) && detail.length > 0) {
        error.message = detail.map((d) => d.msg).join('; ')
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
