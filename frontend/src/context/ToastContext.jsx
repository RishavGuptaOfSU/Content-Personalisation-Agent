import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react'

const ToastContext = createContext(null)

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
}

const STYLES = {
  success:
    'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200',
  error:
    'border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200',
  warning:
    'border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200',
  info: 'border-slate-200 bg-white text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200',
}

let nextId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef(new Map())

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
    const timer = timers.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.current.delete(id)
    }
  }, [])

  const push = useCallback(
    (message, { type = 'info', duration = 4500, title } = {}) => {
      if (!message) return null
      const id = ++nextId
      setToasts((current) => [...current.slice(-3), { id, message, type, title }])
      if (duration > 0) {
        timers.current.set(
          id,
          setTimeout(() => dismiss(id), duration),
        )
      }
      return id
    },
    [dismiss],
  )

  useEffect(
    () => () => {
      timers.current.forEach((timer) => clearTimeout(timer))
      timers.current.clear()
    },
    [],
  )

  const value = useMemo(
    () => ({
      push,
      dismiss,
      success: (message, options) => push(message, { ...options, type: 'success' }),
      error: (message, options) => push(message, { ...options, type: 'error', duration: 6500 }),
      warning: (message, options) => push(message, { ...options, type: 'warning' }),
      info: (message, options) => push(message, { ...options, type: 'info' }),
    }),
    [push, dismiss],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-2"
        role="region"
        aria-label="Notifications"
      >
        {toasts.map((toast) => {
          const Icon = ICONS[toast.type] ?? Info
          return (
            <div
              key={toast.id}
              role="status"
              aria-live="polite"
              className={`pointer-events-auto flex animate-slide-in-right items-start gap-2.5 rounded-lg border p-3 shadow-lg ${STYLES[toast.type]}`}
            >
              <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <div className="min-w-0 flex-1 text-sm">
                {toast.title && <p className="font-semibold">{toast.title}</p>}
                <p className="break-words">{toast.message}</p>
              </div>
              <button
                type="button"
                onClick={() => dismiss(toast.id)}
                className="rounded p-0.5 opacity-60 transition-opacity hover:opacity-100"
                aria-label="Dismiss notification"
              >
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used inside a ToastProvider')
  return context
}
