/** Small formatting helpers shared across pages. */

export function relativeTime(value) {
  if (!value) return ''
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return ''

  const seconds = Math.round((Date.now() - date.getTime()) / 1000)
  if (seconds < 45) return 'just now'
  if (seconds < 90) return 'a minute ago'

  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min ago`

  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} hr${hours === 1 ? '' : 's'} ago`

  const days = Math.round(hours / 24)
  if (days < 7) return `${days} day${days === 1 ? '' : 's'} ago`
  if (days < 30) return `${Math.round(days / 7)} wk ago`

  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function groupByDay(items, getDate) {
  const groups = new Map()
  const today = new Date().toDateString()
  const yesterday = new Date(Date.now() - 86400000).toDateString()

  for (const item of items) {
    const date = new Date(getDate(item))
    let label
    if (Number.isNaN(date.getTime())) label = 'Earlier'
    else if (date.toDateString() === today) label = 'Today'
    else if (date.toDateString() === yesterday) label = 'Yesterday'
    else if (Date.now() - date.getTime() < 7 * 86400000) label = 'Previous 7 days'
    else if (Date.now() - date.getTime() < 30 * 86400000) label = 'Previous 30 days'
    else label = 'Older'

    if (!groups.has(label)) groups.set(label, [])
    groups.get(label).push(item)
  }
  return [...groups.entries()]
}

export function titleCase(value) {
  if (!value) return ''
  return String(value)
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

export function pluralize(count, singular, plural) {
  return `${count} ${count === 1 ? singular : plural ?? `${singular}s`}`
}

export function truncate(value, length = 120) {
  const text = String(value ?? '')
  return text.length <= length ? text : `${text.slice(0, length).trimEnd()}…`
}

/** Render a profile value (string or array) for display. */
export function displayValue(value) {
  if (value === null || value === undefined || value === '') return ''
  if (Array.isArray(value)) return value.join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
