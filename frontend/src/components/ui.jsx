import { forwardRef } from 'react'
import { AlertCircle, Inbox, Loader2 } from 'lucide-react'

export function Spinner({ className = 'h-4 w-4' }) {
  return <Loader2 className={`animate-spin ${className}`} aria-hidden="true" />
}

export function LoadingScreen({ label = 'Loading…' }) {
  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-3 text-slate-500 dark:text-slate-400">
      <Spinner className="h-6 w-6" />
      <p className="text-sm">{label}</p>
    </div>
  )
}

export function Skeleton({ className = 'h-4 w-full' }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />
}

export function CardSkeleton() {
  return (
    <div className="card p-5">
      <div className="flex items-start gap-3">
        <Skeleton className="h-10 w-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-3/4" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-5/6" />
      </div>
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-6 w-20 rounded-full" />
        <Skeleton className="h-6 w-24 rounded-full" />
      </div>
    </div>
  )
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 px-6 py-12 text-center dark:border-slate-700">
      <span className="rounded-full bg-slate-100 p-3 text-slate-400 dark:bg-slate-800 dark:text-slate-500">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <div>
        <p className="font-medium text-slate-800 dark:text-slate-200">{title}</p>
        {description && (
          <p className="mx-auto mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        )}
      </div>
      {action}
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center justify-center gap-3 rounded-xl border border-rose-200 bg-rose-50 px-6 py-10 text-center dark:border-rose-500/30 dark:bg-rose-500/10"
    >
      <AlertCircle className="h-5 w-5 text-rose-600 dark:text-rose-400" aria-hidden="true" />
      <p className="text-sm text-rose-800 dark:text-rose-200">{message}</p>
      {onRetry && (
        <button type="button" className="btn-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

export function Badge({ children, tone = 'slate', className = '' }) {
  const tones = {
    slate:
      'border-slate-200 bg-slate-100 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
    green:
      'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
    amber:
      'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
    brand:
      'border-brand-200 bg-brand-50 text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-300',
    rose: 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300',
  }
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[0.7rem] font-medium ${tones[tone] ?? tones.slate} ${className}`}
    >
      {children}
    </span>
  )
}

export const TextInput = forwardRef(function TextInput(
  { label, hint, error, id, className = '', ...props },
  ref,
) {
  const inputId = id || props.name
  const describedBy = error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined
  return (
    <div className={className}>
      {label && (
        <label className="label" htmlFor={inputId}>
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={`input ${error ? 'border-rose-400 focus:border-rose-500 focus:ring-rose-500' : ''}`}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        {...props}
      />
      {hint && !error && (
        <p id={`${inputId}-hint`} className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-xs text-rose-600 dark:text-rose-400">
          {error}
        </p>
      )}
    </div>
  )
})

export function Select({ label, id, options = [], hint, className = '', ...props }) {
  const selectId = id || props.name
  return (
    <div className={className}>
      {label && (
        <label className="label" htmlFor={selectId}>
          {label}
        </label>
      )}
      <select id={selectId} className="input" {...props}>
        {options.map((option) => {
          const value = typeof option === 'string' ? option : option.value
          const text = typeof option === 'string' ? option : option.label
          return (
            <option key={value} value={value}>
              {text}
            </option>
          )
        })}
      </select>
      {hint && <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{hint}</p>}
    </div>
  )
}

export function Textarea({ label, id, hint, className = '', rows = 4, ...props }) {
  const areaId = id || props.name
  return (
    <div className={className}>
      {label && (
        <label className="label" htmlFor={areaId}>
          {label}
        </label>
      )}
      <textarea id={areaId} rows={rows} className="input resize-y" {...props} />
      {hint && <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{hint}</p>}
    </div>
  )
}

export function SectionHeading({ title, description, action }) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
        {description && (
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{description}</p>
        )}
      </div>
      {action}
    </div>
  )
}
