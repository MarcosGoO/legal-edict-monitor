import { useNavigate } from 'react-router-dom'
import { MapPin } from 'lucide-react'

export default function NotFoundPage() {
  const navigate = useNavigate()
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
        <MapPin className="w-8 h-8 text-slate-400" />
      </div>
      <h2 className="text-2xl font-bold text-slate-800 mb-1">404</h2>
      <p className="text-slate-500 text-sm mb-6">La página que buscas no existe.</p>
      <button
        onClick={() => navigate('/')}
        className="px-5 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
      >
        Volver al inicio
      </button>
    </div>
  )
}
