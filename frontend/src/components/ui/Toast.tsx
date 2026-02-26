import * as ToastPrimitive from '@radix-ui/react-toast'
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react'
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { clsx } from 'clsx'

// ── Types ────────────────────────────────────────────────────────────────────

type ToastVariant = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  variant: ToastVariant
  message: string
}

interface ToastContextValue {
  toast: (message: string, variant?: ToastVariant) => void
}

// ── Context ──────────────────────────────────────────────────────────────────

const ToastContext = createContext<ToastContextValue>({ toast: () => {} })

export const useToast = () => useContext(ToastContext)

// ── Provider ─────────────────────────────────────────────────────────────────

const ICONS: Record<ToastVariant, React.ElementType> = {
  success: CheckCircle,
  error:   XCircle,
  info:    AlertCircle,
}

const COLORS: Record<ToastVariant, string> = {
  success: 'text-emerald-500',
  error:   'text-red-500',
  info:    'text-blue-500',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  let counter = 0

  const toast = useCallback((message: string, variant: ToastVariant = 'info') => {
    const id = ++counter
    setToasts((prev) => [...prev, { id, variant, message }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000)
  }, [])

  return (
    <ToastContext.Provider value={{ toast }}>
      <ToastPrimitive.Provider swipeDirection="right">
        {children}

        {toasts.map((t) => {
          const Icon = ICONS[t.variant]
          return (
            <ToastPrimitive.Root
              key={t.id}
              open
              className={clsx(
                'flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-xl shadow-lg',
                'data-[state=open]:animate-in data-[state=open]:slide-in-from-right-4',
                'data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right-4',
                'max-w-sm w-full',
              )}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${COLORS[t.variant]}`} />
              <ToastPrimitive.Description className="flex-1 text-sm text-slate-700">
                {t.message}
              </ToastPrimitive.Description>
              <ToastPrimitive.Close className="text-slate-400 hover:text-slate-600 p-0.5 rounded">
                <X className="w-3.5 h-3.5" />
              </ToastPrimitive.Close>
            </ToastPrimitive.Root>
          )
        })}

        <ToastPrimitive.Viewport className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  )
}
