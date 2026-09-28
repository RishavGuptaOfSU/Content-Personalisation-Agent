import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const TOKEN_KEY = 'cpa.token'

export const tokenStore = {
  get: () => {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch {
      return null
    }
  },
  set: (token) => {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token)
      else localStorage.removeItem(TOKEN_KEY)
    } catch {
      /* storage unavailable (private mode) — the in-memory header still works */
    }
  },
  clear: () => tokenStore.set(null),
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = tokenStore.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Turn any axios failure into a readable message for a toast. */
export function errorMessage(error, fallback = 'Something went wrong') {
  if (!error) return fallback
  if (error.code === 'ECONNABORTED') return 'The request timed out. Please try again.'
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
  }
  if (error.response?.status === 401) return 'Your session expired. Please sign in again.'
  if (!error.response) return 'Cannot reach the API. Is the backend running?'
  return error.message || fallback
}

let onUnauthorized = null
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    // Don't bounce the user out for a failed login attempt.
    const isAuthAttempt = url.includes('/auth/login') || url.includes('/auth/register')
    if (status === 401 && !isAuthAttempt && onUnauthorized) onUnauthorized()
    return Promise.reject(error)
  },
)

// --------------------------------------------------------------------- auth
export const authApi = {
  register: (payload) => api.post('/auth/register', payload).then((r) => r.data),
  login: (payload) => api.post('/auth/login', payload).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
  changePassword: (payload) => api.post('/auth/change-password', payload).then((r) => r.data),
}

// ------------------------------------------------------- catalog (2 levels)
/**
 * The catalog is two levels deep: a **domain** (`marketing`) holds many narrow
 * **agents** (`marketing.post-image`). Agents are always addressed by their
 * fully qualified key.
 */
export const catalogApi = {
  overview: () => api.get('/catalog').then((r) => r.data),
  domains: () => api.get('/domains').then((r) => r.data),
  domain: (domain) => api.get(`/domains/${domain}`).then((r) => r.data),
  domainAgents: (domain) => api.get(`/domains/${domain}/agents`).then((r) => r.data),
  agents: () => api.get('/agents').then((r) => r.data),
  agent: (agentKey) => api.get(`/agents/${agentKey}`).then((r) => r.data),
}

// ----------------------------------------------------------------- profiles
export const profileApi = {
  getGlobal: () => api.get('/profile/global').then((r) => r.data),
  updateGlobal: (payload) => api.put('/profile/global', payload).then((r) => r.data),
  overview: () => api.get('/profile/overview').then((r) => r.data),

  // Domain level: the answers every agent in the domain reuses.
  getDomain: (domain) => api.get(`/profile/domain/${domain}`).then((r) => r.data),
  saveDomain: (domain, profileData) =>
    api.put(`/profile/domain/${domain}`, { profile_data: profileData }).then((r) => r.data),

  // Agent level: the narrow specifics of one job.
  getAgent: (agentKey) => api.get(`/profile/agent/${agentKey}`).then((r) => r.data),
  saveAgent: (agentKey, profileData) =>
    api.put(`/profile/agent/${agentKey}`, { profile_data: profileData }).then((r) => r.data),
  patchAgent: (agentKey, profileData) =>
    api.patch(`/profile/agent/${agentKey}`, { profile_data: profileData }).then((r) => r.data),
}

/**
 * Absolute URL for a generated image or chart.
 *
 * The backend returns a root-relative path (`/api/media/<file>.png`). When the
 * UI talks to the API on another origin, that path has to be re-based or the
 * browser would request it from the dev server instead.
 */
export function mediaUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  if (API_BASE_URL === '/api' || url.startsWith(API_BASE_URL)) return url
  return `${API_BASE_URL.replace(/\/$/, '')}${url.replace(/^\/api/, '')}`
}

/**
 * Stream a chat turn over Server-Sent Events.
 *
 * `EventSource` cannot send an Authorization header, so this uses `fetch` with a
 * manual SSE parser. Local models generate at a few tokens per second, so the
 * backend emits the routing decision and personalization trace (`meta`) before
 * the first token, then `delta` chunks, then the persisted turn (`done`).
 *
 * Returns a promise that resolves when the stream completes.
 */
export async function streamChat(
  payload,
  { onMeta, onDelta, onStatus, onDone, signal } = {},
) {
  const token = tokenStore.get()
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
    signal,
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) detail = body.detail
    } catch {
      /* non-JSON error body */
    }
    if (response.status === 401) {
      tokenStore.clear()
      if (onUnauthorized) onUnauthorized()
    }
    throw new Error(detail)
  }
  if (!response.body) throw new Error('Streaming is not supported by this browser')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let streamError = null

  const dispatch = (rawEvent) => {
    let event = 'message'
    const dataLines = []
    for (const line of rawEvent.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim()
      else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
    }
    if (dataLines.length === 0) return
    let data
    try {
      data = JSON.parse(dataLines.join('\n'))
    } catch {
      return
    }
    if (event === 'meta') onMeta?.(data)
    else if (event === 'delta') onDelta?.(data.text ?? '')
    // Visual agents cannot stream tokens — they report progress instead.
    else if (event === 'status') onStatus?.(data.message ?? '')
    else if (event === 'done') onDone?.(data)
    else if (event === 'error') streamError = new Error(data.detail || 'Generation failed')
  }

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let boundary = buffer.indexOf('\n\n')
    while (boundary !== -1) {
      dispatch(buffer.slice(0, boundary))
      buffer = buffer.slice(boundary + 2)
      boundary = buffer.indexOf('\n\n')
    }
    if (streamError) break
  }
  if (buffer.trim()) dispatch(buffer)
  if (streamError) throw streamError
}

// --------------------------------------------------------------------- chat
export const chatApi = {
  // Non-streaming fallback. Generous timeout: a local CPU model can take minutes.
  send: (payload) => api.post('/chat', payload, { timeout: 600000 }).then((r) => r.data),
  stream: streamChat,
  pipeline: () => api.get('/chat/pipeline').then((r) => r.data),
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api
      .post('/chat/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then((r) => r.data)
  },
}

// ------------------------------------------------------------ conversations
export const conversationsApi = {
  list: (params = {}) => api.get('/conversations', { params }).then((r) => r.data),
  create: (payload) => api.post('/conversations', payload).then((r) => r.data),
  get: (id) => api.get(`/conversations/${id}`).then((r) => r.data),
  update: (id, payload) => api.patch(`/conversations/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/conversations/${id}`).then((r) => r.data),
}

// ----------------------------------------------------------------- feedback
export const feedbackApi = {
  submit: (payload) => api.post('/feedback', payload).then((r) => r.data),
  list: (params = {}) => api.get('/feedback', { params }).then((r) => r.data),
}

// ------------------------------------------------------------------- memory
export const memoryApi = {
  list: (params = {}) => api.get('/memory', { params }).then((r) => r.data),
  summary: (params = {}) => api.get('/memory/summary', { params }).then((r) => r.data),
  search: (params) => api.get('/memory/search', { params }).then((r) => r.data),
  create: (payload) => api.post('/memory', payload).then((r) => r.data),
  remove: (id) => api.delete(`/memory/${id}`).then((r) => r.data),
}

// ---------------------------------------------------------------- dashboard
export const dashboardApi = {
  stats: () => api.get('/dashboard/stats').then((r) => r.data),
}
