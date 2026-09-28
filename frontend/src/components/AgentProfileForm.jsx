import { useCallback, useEffect, useMemo, useState } from 'react'
import { Plus, X } from 'lucide-react'
import { Select, Spinner, TextInput, Textarea } from './ui'

/** Free-text tag editor used for `kind: "tags"` fields. */
function TagsInput({ field, value, onChange }) {
  const [draft, setDraft] = useState('')
  const tags = Array.isArray(value) ? value : []

  const add = useCallback(
    (raw) => {
      const next = String(raw || '').trim()
      if (!next) return
      if (tags.some((tag) => tag.toLowerCase() === next.toLowerCase())) {
        setDraft('')
        return
      }
      onChange([...tags, next.slice(0, 120)])
      setDraft('')
    },
    [tags, onChange],
  )

  return (
    <div>
      <label className="label" htmlFor={`${field.key}-input`}>
        {field.label}
        {field.required && <span className="ml-1 text-rose-500">*</span>}
      </label>
      <div className="flex gap-2">
        <input
          id={`${field.key}-input`}
          className="input"
          value={draft}
          placeholder={field.placeholder || 'Type and press Enter'}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ',') {
              event.preventDefault()
              add(draft)
            } else if (event.key === 'Backspace' && !draft && tags.length) {
              onChange(tags.slice(0, -1))
            }
          }}
        />
        <button
          type="button"
          className="btn-secondary shrink-0"
          onClick={() => add(draft)}
          aria-label={`Add ${field.label}`}
        >
          <Plus className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
      {tags.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <li key={tag}>
              <span className="chip border-slate-200 bg-slate-100 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {tag}
                <button
                  type="button"
                  onClick={() => onChange(tags.filter((item) => item !== tag))}
                  className="ml-0.5 rounded-full p-0.5 opacity-60 hover:opacity-100"
                  aria-label={`Remove ${tag}`}
                >
                  <X className="h-3 w-3" aria-hidden="true" />
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
      {field.help_text && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{field.help_text}</p>
      )}
    </div>
  )
}

function MultiSelect({ field, value, onChange }) {
  const selected = Array.isArray(value) ? value : []
  const toggle = (option) => {
    onChange(
      selected.includes(option)
        ? selected.filter((item) => item !== option)
        : [...selected, option],
    )
  }
  return (
    <fieldset>
      <legend className="label">
        {field.label}
        {field.required && <span className="ml-1 text-rose-500">*</span>}
      </legend>
      <div className="flex flex-wrap gap-1.5">
        {field.options.map((option) => {
          const active = selected.includes(option)
          return (
            <button
              key={option}
              type="button"
              aria-pressed={active}
              onClick={() => toggle(option)}
              className={active ? 'chip-active' : 'chip-idle'}
            >
              {option}
            </button>
          )
        })}
      </div>
      {field.help_text && (
        <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">{field.help_text}</p>
      )}
    </fieldset>
  )
}

export function buildInitialValues(fields, existing = {}) {
  const values = {}
  for (const field of fields) {
    const current = existing?.[field.key]
    if (current !== undefined && current !== null && current !== '') {
      values[field.key] = current
    } else if (field.kind === 'multiselect' || field.kind === 'tags') {
      values[field.key] = []
    } else if (field.kind === 'select') {
      values[field.key] = field.default ?? ''
    } else {
      values[field.key] = field.default ?? ''
    }
  }
  return values
}

function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (Array.isArray(value)) return value.length === 0
  return String(value).trim() === ''
}

/**
 * Renders an agent's profile form from the field definitions served by
 * `GET /api/agents/{agent}`. Used for both first-time setup and later edits,
 * so the two can never drift apart.
 */
export default function AgentProfileForm({
  fields = [],
  initialData = {},
  onSubmit,
  onCancel,
  submitLabel = 'Save profile',
  submitting = false,
  columns = 1,
}) {
  const [values, setValues] = useState(() => buildInitialValues(fields, initialData))
  const [errors, setErrors] = useState({})

  useEffect(() => {
    setValues(buildInitialValues(fields, initialData))
    setErrors({})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fields, JSON.stringify(initialData)])

  const setValue = useCallback((key, next) => {
    setValues((current) => ({ ...current, [key]: next }))
    setErrors((current) => {
      if (!current[key]) return current
      const { [key]: _removed, ...rest } = current
      return rest
    })
  }, [])

  const requiredKeys = useMemo(
    () => fields.filter((field) => field.required).map((field) => field.key),
    [fields],
  )

  const handleSubmit = (event) => {
    event.preventDefault()
    const nextErrors = {}
    for (const key of requiredKeys) {
      if (isEmpty(values[key])) nextErrors[key] = 'This field is required'
    }
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      const firstField = document.getElementById(`${Object.keys(nextErrors)[0]}-input`)
      firstField?.focus()
      return
    }
    onSubmit(values)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div className={columns === 2 ? 'grid gap-5 sm:grid-cols-2' : 'space-y-5'}>
        {fields.map((field) => {
          const error = errors[field.key]
          const span = field.kind === 'textarea' || field.kind === 'multiselect' ? 'sm:col-span-2' : ''
          return (
            <div key={field.key} className={span}>
              {field.kind === 'multiselect' && (
                <MultiSelect
                  field={field}
                  value={values[field.key]}
                  onChange={(next) => setValue(field.key, next)}
                />
              )}
              {field.kind === 'tags' && (
                <TagsInput
                  field={field}
                  value={values[field.key]}
                  onChange={(next) => setValue(field.key, next)}
                />
              )}
              {field.kind === 'select' && (
                <Select
                  id={`${field.key}-input`}
                  label={`${field.label}${field.required ? ' *' : ''}`}
                  name={field.key}
                  value={values[field.key] ?? ''}
                  hint={field.help_text}
                  onChange={(event) => setValue(field.key, event.target.value)}
                  options={[{ value: '', label: 'Select…' }, ...field.options]}
                />
              )}
              {field.kind === 'textarea' && (
                <Textarea
                  id={`${field.key}-input`}
                  label={`${field.label}${field.required ? ' *' : ''}`}
                  name={field.key}
                  value={values[field.key] ?? ''}
                  placeholder={field.placeholder}
                  hint={field.help_text}
                  rows={5}
                  onChange={(event) => setValue(field.key, event.target.value)}
                />
              )}
              {(field.kind === 'text' || field.kind === 'number') && (
                <TextInput
                  id={`${field.key}-input`}
                  label={`${field.label}${field.required ? ' *' : ''}`}
                  name={field.key}
                  type={field.kind === 'number' ? 'number' : 'text'}
                  value={values[field.key] ?? ''}
                  placeholder={field.placeholder}
                  hint={field.help_text}
                  onChange={(event) => setValue(field.key, event.target.value)}
                />
              )}
              {error && field.kind !== 'text' && (
                <p className="mt-1 text-xs text-rose-600 dark:text-rose-400">{error}</p>
              )}
              {error && field.kind === 'text' && (
                <p className="mt-1 text-xs text-rose-600 dark:text-rose-400">{error}</p>
              )}
            </div>
          )
        })}
      </div>

      <div className="flex flex-wrap items-center justify-end gap-2 border-t divider pt-4">
        {onCancel && (
          <button type="button" className="btn-ghost" onClick={onCancel} disabled={submitting}>
            Cancel
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting && <Spinner />}
          {submitLabel}
        </button>
      </div>
    </form>
  )
}
