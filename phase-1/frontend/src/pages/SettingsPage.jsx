import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Brain,
  Cpu,
  KeyRound,
  Monitor,
  Moon,
  Plus,
  Search,
  Sun,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  Workflow,
} from 'lucide-react'
import {
  Badge,
  EmptyState,
  ErrorState,
  Select,
  Spinner,
  TextInput,
  SectionHeading,
  Skeleton,
} from '../components/ui'
import { ConfirmDialog } from '../components/Modal'
import { useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'
import { useAppShell } from '../layouts/AppLayout'
import {
  authApi,
  chatApi,
  errorMessage,
  feedbackApi,
  memoryApi,
} from '../services/api'
import { relativeTime, titleCase } from '../utils/format'

const MEMORY_KINDS = [
  { value: '', label: 'All kinds' },
  { value: 'preference', label: 'Preference' },
  { value: 'requirement', label: 'Requirement' },
  { value: 'interest', label: 'Interest' },
  { value: 'skill', label: 'Skill' },
  { value: 'fact', label: 'Fact' },
  { value: 'feedback', label: 'Feedback' },
]

/**
 * A memory's scope is encoded in one select value so a single control can cover
 * all three levels: `global`, `domain:<key>` or `agent:<domain>.<slug>`.
 */
function parseScope(value) {
  if (!value || value === 'global') return {}
  if (value.startsWith('domain:')) return { domain: value.slice(7) }
  if (value.startsWith('agent:')) return { agent_key: value.slice(6) }
  return {}
}

function MemoryManager() {
  const toast = useToast()
  const { domains, agents, agentsByDomain } = useAppShell()
  const [memories, setMemories] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [scopeFilter, setScopeFilter] = useState('')
  const [kindFilter, setKindFilter] = useState('')
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [newMemory, setNewMemory] = useState('')
  const [newMemoryScope, setNewMemoryScope] = useState('global')
  const [adding, setAdding] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { limit: 200, ...parseScope(scopeFilter) }
      if (kindFilter) params.kind = kindFilter
      const [list, stats] = await Promise.all([memoryApi.list(params), memoryApi.summary()])
      setMemories(list)
      setSummary(stats)
    } catch (requestError) {
      setError(errorMessage(requestError, 'Could not load memories'))
    } finally {
      setLoading(false)
    }
  }, [scopeFilter, kindFilter])

  useEffect(() => {
    load()
  }, [load])

  const runSearch = async (event) => {
    event.preventDefault()
    if (!query.trim()) {
      load()
      return
    }
    setSearching(true)
    try {
      const params = { q: query.trim(), limit: 20, ...parseScope(scopeFilter) }
      setMemories(await memoryApi.search(params))
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Search failed'))
    } finally {
      setSearching(false)
    }
  }

  const addMemory = async (event) => {
    event.preventDefault()
    const content = newMemory.trim()
    if (content.length < 3) return
    setAdding(true)
    try {
      await memoryApi.create({
        content,
        ...parseScope(newMemoryScope),
        kind: 'preference',
        importance: 0.7,
      })
      setNewMemory('')
      toast.success('Memory saved. Agents will use it from the next message.')
      load()
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Could not save the memory'))
    } finally {
      setAdding(false)
    }
  }

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await memoryApi.remove(pendingDelete.id)
      setMemories((current) => current.filter((item) => item.id !== pendingDelete.id))
      setPendingDelete(null)
      toast.success('Memory deleted')
      load()
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Could not delete the memory'))
    } finally {
      setDeleting(false)
    }
  }

  /** Global, then each domain, then each agent nested under its domain. */
  const scopeOptions = useMemo(() => {
    const options = [
      { value: '', label: 'All scopes' },
      { value: 'global', label: 'Global — every agent' },
    ]
    for (const domain of domains) {
      options.push({ value: `domain:${domain.key}`, label: `${domain.name} — whole domain` })
      for (const agent of agentsByDomain[domain.key] ?? []) {
        options.push({ value: `agent:${agent.key}`, label: `   ${domain.name} › ${agent.name}` })
      }
    }
    return options
  }, [domains, agentsByDomain])

  /** agent key -> display name, for the scope badge on each memory row. */
  const agentNames = useMemo(
    () => Object.fromEntries(agents.map((agent) => [agent.key, agent.name])),
    [agents],
  )
  const domainNames = useMemo(
    () => Object.fromEntries(domains.map((domain) => [domain.key, domain.name])),
    [domains],
  )

  const scopeLabel = (memory) => {
    if (memory.agent_key) return agentNames[memory.agent_key] ?? memory.agent_key
    if (memory.domain) return `${domainNames[memory.domain] ?? memory.domain} (domain)`
    return 'Global'
  }

  return (
    <section className="card p-6" aria-labelledby="memory-heading">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
          <Brain className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <h2 id="memory-heading" className="font-semibold">
            Long-term memory
          </h2>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            What the system has learned about you. Stored as embeddings and retrieved semantically
            for every request.
          </p>
        </div>
      </div>

      {summary && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          <Badge tone="brand">{summary.total} total</Badge>
          {Object.entries(summary.by_domain ?? {}).map(([key, count]) => (
            <Badge key={key}>
              {key === 'global' ? 'Global' : (domainNames[key] ?? titleCase(key))}: {count}
            </Badge>
          ))}
        </div>
      )}

      {/* Add */}
      <form onSubmit={addMemory} className="mt-5 flex flex-wrap items-end gap-2">
        <TextInput
          className="min-w-[14rem] flex-1"
          label="Teach the agents something"
          name="new_memory"
          placeholder="e.g. Always include a runnable example"
          value={newMemory}
          onChange={(event) => setNewMemory(event.target.value)}
        />
        <Select
          className="w-56"
          label="Applies to"
          name="new_memory_scope"
          value={newMemoryScope}
          onChange={(event) => setNewMemoryScope(event.target.value)}
          options={scopeOptions.filter((option) => option.value !== '')}
          hint="Global, a whole domain, or one agent."
        />
        <button type="submit" className="btn-primary" disabled={adding || newMemory.trim().length < 3}>
          {adding ? <Spinner /> : <Plus className="h-4 w-4" aria-hidden="true" />}
          Add
        </button>
      </form>

      {/* Filters */}
      <div className="mt-6 flex flex-wrap items-end gap-2 border-t divider pt-4">
        <form onSubmit={runSearch} className="flex min-w-[16rem] flex-1 items-end gap-2">
          <TextInput
            className="flex-1"
            label="Semantic search"
            name="memory_search"
            placeholder="What would the agent recall for…?"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button type="submit" className="btn-secondary" disabled={searching}>
            {searching ? <Spinner /> : <Search className="h-4 w-4" aria-hidden="true" />}
            Search
          </button>
        </form>
        <Select
          className="w-56"
          label="Scope"
          name="scope_filter"
          value={scopeFilter}
          onChange={(event) => {
            setQuery('')
            setScopeFilter(event.target.value)
          }}
          options={scopeOptions}
        />
        <Select
          className="w-40"
          label="Kind"
          name="kind_filter"
          value={kindFilter}
          onChange={(event) => {
            setQuery('')
            setKindFilter(event.target.value)
          }}
          options={MEMORY_KINDS}
        />
      </div>

      <div className="mt-4">
        {error ? (
          <ErrorState message={error} onRetry={load} />
        ) : loading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-14 w-full rounded-lg" />
            ))}
          </div>
        ) : memories.length === 0 ? (
          <EmptyState
            icon={Brain}
            title="No memories yet"
            description="Chat with an agent and give feedback like “keep posts concise”. Durable preferences are stored here automatically."
          />
        ) : (
          <ul className="divide-y divider">
            {memories.map((memory) => (
              <li key={memory.id} className="group flex items-start gap-3 py-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-slate-800 dark:text-slate-200">{memory.content}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[0.7rem] text-slate-500 dark:text-slate-400">
                    <Badge>{scopeLabel(memory)}</Badge>
                    <Badge>{memory.kind}</Badge>
                    <span>importance {(memory.importance * 100).toFixed(0)}%</span>
                    {memory.occurrences > 1 && <span>· reinforced {memory.occurrences}×</span>}
                    {memory.use_count > 0 && <span>· used {memory.use_count}×</span>}
                    <span>· {relativeTime(memory.created_at)}</span>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-ghost shrink-0 p-1.5 text-slate-400 opacity-0 transition-opacity hover:text-rose-600 focus-visible:opacity-100 group-hover:opacity-100"
                  onClick={() => setPendingDelete(memory)}
                  aria-label={`Delete memory: ${memory.content}`}
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        onClose={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
        title="Delete this memory?"
        description={`"${pendingDelete?.content ?? ''}" will no longer be used to personalize responses.`}
        confirmLabel="Delete"
        busy={deleting}
      />
    </section>
  )
}

function FeedbackHistory() {
  const { agentsByKey } = useAppShell()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    feedbackApi
      .list({ limit: 25 })
      .then((data) => {
        if (!cancelled) setEntries(data)
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="card p-6">
      <SectionHeading
        title="Feedback history"
        description="Each rating you give. Repeated signals are what update your profile."
      />
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full rounded-lg" />
          ))}
        </div>
      ) : entries.length === 0 ? (
        <EmptyState
          icon={ThumbsUp}
          title="No feedback yet"
          description="Rate a response to start teaching the agents."
        />
      ) : (
        <ul className="divide-y divider">
          {entries.map((entry) => (
            <li key={entry.id} className="flex items-start gap-3 py-2.5">
              <span
                className={`mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full ${
                  entry.rating > 0
                    ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/15 dark:text-emerald-400'
                    : 'bg-rose-50 text-rose-600 dark:bg-rose-500/15 dark:text-rose-400'
                }`}
              >
                {entry.rating > 0 ? (
                  <ThumbsUp className="h-3 w-3" aria-hidden="true" />
                ) : (
                  <ThumbsDown className="h-3 w-3" aria-hidden="true" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm text-slate-800 dark:text-slate-200">
                  {entry.feedback_text || (entry.rating > 0 ? 'Marked helpful' : 'Marked not helpful')}
                </p>
                <p className="mt-0.5 text-[0.7rem] text-slate-500 dark:text-slate-400">
                  {agentsByKey[entry.agent_key]?.name ?? entry.agent_key} ·{' '}
                  {relativeTime(entry.created_at)}
                  {Object.keys(entry.outcome?.profile_changes || {}).length > 0 && (
                    <span className="ml-1 text-emerald-600 dark:text-emerald-400">
                      · profile updated
                    </span>
                  )}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function AppearanceCard() {
  const { theme, setTheme } = useTheme()
  const options = [
    { value: 'light', label: 'Light', Icon: Sun },
    { value: 'dark', label: 'Dark', Icon: Moon },
  ]
  return (
    <section className="card p-6">
      <SectionHeading title="Appearance" description="Applies to this browser." />
      <div className="flex gap-2">
        {options.map(({ value, label, Icon }) => (
          <button
            key={value}
            type="button"
            onClick={() => setTheme(value)}
            aria-pressed={theme === value}
            className={theme === value ? 'chip-active px-3 py-1.5' : 'chip-idle px-3 py-1.5'}
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            {label}
          </button>
        ))}
        <button
          type="button"
          onClick={() =>
            setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
          }
          className="chip-idle px-3 py-1.5"
        >
          <Monitor className="h-3.5 w-3.5" aria-hidden="true" />
          Match system
        </button>
      </div>
    </section>
  )
}

function PasswordCard() {
  const toast = useToast()
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm: '' })
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  const submit = async (event) => {
    event.preventDefault()
    const next = {}
    if (!form.current_password) next.current_password = 'Required'
    if (form.new_password.length < 8) next.new_password = 'At least 8 characters'
    else if (!/[A-Za-z]/.test(form.new_password) || !/\d/.test(form.new_password))
      next.new_password = 'Include at least one letter and one number'
    if (form.new_password !== form.confirm) next.confirm = 'Passwords do not match'
    setErrors(next)
    if (Object.keys(next).length) return

    setSaving(true)
    try {
      await authApi.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      })
      setForm({ current_password: '', new_password: '', confirm: '' })
      toast.success('Password changed.')
    } catch (error) {
      toast.error(errorMessage(error, 'Could not change the password'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="card p-6">
      <SectionHeading title="Password" description="Change the password for this account." />
      <form onSubmit={submit} className="grid gap-4 sm:grid-cols-3">
        <TextInput
          label="Current password"
          name="current_password"
          type="password"
          autoComplete="current-password"
          value={form.current_password}
          error={errors.current_password}
          onChange={(event) => setForm({ ...form, current_password: event.target.value })}
        />
        <TextInput
          label="New password"
          name="new_password"
          type="password"
          autoComplete="new-password"
          value={form.new_password}
          error={errors.new_password}
          onChange={(event) => setForm({ ...form, new_password: event.target.value })}
        />
        <TextInput
          label="Confirm new password"
          name="confirm"
          type="password"
          autoComplete="new-password"
          value={form.confirm}
          error={errors.confirm}
          onChange={(event) => setForm({ ...form, confirm: event.target.value })}
        />
        <div className="sm:col-span-3">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving && <Spinner />}
            <KeyRound className="h-4 w-4" aria-hidden="true" />
            Update password
          </button>
        </div>
      </form>
    </section>
  )
}

function SystemCard() {
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    chatApi
      .pipeline()
      .then((data) => {
        if (!cancelled) setInfo(data)
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="card p-6">
      <SectionHeading
        title="System"
        description="Which provider and pipeline are serving your requests."
      />
      {loading ? (
        <Skeleton className="h-20 w-full rounded-lg" />
      ) : !info ? (
        <p className="text-sm text-slate-500">Unavailable.</p>
      ) : (
        <div className="space-y-4 text-sm">
          <div>
            <p className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
              <Cpu className="h-3.5 w-3.5" aria-hidden="true" /> LLM provider
            </p>
            <p className="mt-1 text-slate-800 dark:text-slate-200">
              {info.providers.llm.provider} · {info.providers.llm.model}
            </p>
            {info.providers.llm.note && (
              <p className="mt-1 rounded-lg bg-amber-50 p-2.5 text-xs text-amber-900 dark:bg-amber-500/10 dark:text-amber-200">
                {info.providers.llm.note}
              </p>
            )}
            <div className="mt-2 flex flex-wrap gap-1.5">
              {info.providers.llm.supports_streaming && <Badge tone="green">streaming</Badge>}
              {info.providers.router_uses_llm ? (
                <Badge tone="brand">LLM routing</Badge>
              ) : (
                <Badge>heuristic routing</Badge>
              )}
              {info.providers.llm_memory_extraction && <Badge tone="brand">LLM memory extraction</Badge>}
              {info.providers.llm.model_pulled === false && (
                <Badge tone="rose">model not pulled</Badge>
              )}
            </div>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
              Embeddings: {info.providers.embeddings.provider} (
              {info.providers.embeddings.dimension}d) · router model:{' '}
              {info.providers.router_model}
            </p>
            {info.providers.embeddings.warning && (
              <p className="mt-1.5 rounded-lg bg-rose-50 p-2.5 text-xs text-rose-800 dark:bg-rose-500/10 dark:text-rose-200">
                {info.providers.embeddings.warning}
              </p>
            )}
          </div>
          <div>
            <p className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
              <Workflow className="h-3.5 w-3.5" aria-hidden="true" /> LangGraph nodes
            </p>
            <ol className="mt-1.5 flex flex-wrap items-center gap-1 text-xs">
              {info.graph_nodes.map((node, index) => (
                <li key={node} className="flex items-center gap-1">
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    {node}
                  </span>
                  {index < info.graph_nodes.length - 1 && (
                    <span className="text-slate-300 dark:text-slate-600">→</span>
                  )}
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </section>
  )
}

export default function SettingsPage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-4xl space-y-6 px-5 py-8 sm:px-8">
        <header>
          <h1 className="text-2xl font-semibold">Settings</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Memory, appearance, security and system information.
          </p>
        </header>

        <MemoryManager />
        <FeedbackHistory />
        <AppearanceCard />
        <PasswordCard />
        <SystemCard />
      </div>
    </div>
  )
}
