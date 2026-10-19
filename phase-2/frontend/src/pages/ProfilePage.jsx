import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CheckCircle2,
  ChevronDown,
  Globe,
  Layers,
  Pencil,
  Plus,
  Settings2,
  Sparkles,
  X,
} from 'lucide-react'
import AgentProfileForm from '../components/AgentProfileForm'
import {
  Badge,
  ErrorState,
  LoadingScreen,
  Select,
  Spinner,
  TextInput,
  Textarea,
} from '../components/ui'
import { useToast } from '../context/ToastContext'
import { useAppShell } from '../layouts/AppLayout'
import { DOMAIN, catalogApi, errorMessage, profileApi } from '../services/api'
import { accent, agentIcon, OUTPUT_KIND_LABELS } from '../utils/agents'
import { displayValue } from '../utils/format'

const RESPONSE_LENGTHS = [
  { value: 'concise', label: 'Concise — short and to the point' },
  { value: 'balanced', label: 'Balanced — the default' },
  { value: 'detailed', label: 'Detailed — go deep' },
]
const STYLES = [
  { value: 'friendly', label: 'Friendly' },
  { value: 'professional', label: 'Professional' },
  { value: 'direct', label: 'Direct — no hedging' },
  { value: 'casual', label: 'Casual' },
  { value: 'academic', label: 'Academic' },
]
const SKILL_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'expert', label: 'Expert' },
]

function ListEditor({ label, values = [], onChange, placeholder }) {
  const [draft, setDraft] = useState('')
  const add = () => {
    const next = draft.trim()
    if (!next || values.includes(next)) {
      setDraft('')
      return
    }
    onChange([...values, next])
    setDraft('')
  }
  return (
    <div>
      <label className="label" htmlFor={`${label}-input`}>
        {label}
      </label>
      <div className="flex gap-2">
        <input
          id={`${label}-input`}
          className="input"
          value={draft}
          placeholder={placeholder}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault()
              add()
            }
          }}
        />
        <button
          type="button"
          className="btn-secondary shrink-0"
          onClick={add}
          aria-label={`Add ${label}`}
        >
          <Plus className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
      {values.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {values.map((value) => (
            <li key={value}>
              <span className="chip border-slate-200 bg-slate-100 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {value}
                <button
                  type="button"
                  className="ml-0.5 rounded-full p-0.5 opacity-60 hover:opacity-100"
                  onClick={() => onChange(values.filter((item) => item !== value))}
                  aria-label={`Remove ${value}`}
                >
                  <X className="h-3 w-3" aria-hidden="true" />
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function GlobalProfileCard({ profile, onSaved }) {
  const toast = useToast()
  const [form, setForm] = useState(() => ({ ...profile }))
  const [saving, setSaving] = useState(false)

  useEffect(() => setForm({ ...profile }), [profile])

  const update = (key) => (event) =>
    setForm((current) => ({ ...current, [key]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    setSaving(true)
    try {
      const payload = {
        display_name: form.display_name || null,
        occupation: form.occupation || null,
        location: form.location || null,
        language: form.language || 'English',
        preferred_response_length: form.preferred_response_length,
        communication_style: form.communication_style,
        general_skill_level: form.general_skill_level,
        interests: form.interests || [],
        goals: form.goals || [],
        preferences: form.preferences || {},
        bio: form.bio || null,
      }
      const updated = await profileApi.updateGlobal(payload)
      onSaved(updated)
      toast.success('Global profile saved. Every agent uses it.')
    } catch (error) {
      toast.error(errorMessage(error, 'Could not save the global profile'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="card p-6" aria-labelledby="global-profile-heading">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
          <Globe className="h-5 w-5" aria-hidden="true" />
        </span>
        <div>
          <h2 id="global-profile-heading" className="font-semibold">
            Global profile
          </h2>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Level 1 of 3. Shared by <strong>every</strong> domain and agent. Controls tone, length
            and assumed skill level.
          </p>
        </div>
      </div>

      <form onSubmit={submit} className="mt-6 space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput
            label="Display name"
            name="display_name"
            value={form.display_name ?? ''}
            onChange={update('display_name')}
          />
          <TextInput
            label="Occupation"
            name="occupation"
            placeholder="e.g. Backend engineer"
            value={form.occupation ?? ''}
            onChange={update('occupation')}
          />
          <TextInput
            label="Location"
            name="location"
            placeholder="e.g. Bengaluru, India"
            value={form.location ?? ''}
            onChange={update('location')}
          />
          <TextInput
            label="Preferred language"
            name="language"
            value={form.language ?? 'English'}
            onChange={update('language')}
            hint="Replies are written in this language."
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <Select
            label="Response length"
            name="preferred_response_length"
            value={form.preferred_response_length}
            onChange={update('preferred_response_length')}
            options={RESPONSE_LENGTHS}
          />
          <Select
            label="Communication style"
            name="communication_style"
            value={form.communication_style}
            onChange={update('communication_style')}
            options={STYLES}
          />
          <Select
            label="General skill level"
            name="general_skill_level"
            value={form.general_skill_level}
            onChange={update('general_skill_level')}
            options={SKILL_LEVELS}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <ListEditor
            label="General interests"
            values={form.interests ?? []}
            placeholder="AI agents, cloud…"
            onChange={(values) => setForm((current) => ({ ...current, interests: values }))}
          />
          <ListEditor
            label="Goals"
            values={form.goals ?? []}
            placeholder="Ship a side project…"
            onChange={(values) => setForm((current) => ({ ...current, goals: values }))}
          />
        </div>

        <Textarea
          label="About you"
          name="bio"
          rows={3}
          placeholder="One or two lines the agents should always know."
          value={form.bio ?? ''}
          onChange={update('bio')}
        />

        <div className="flex items-center justify-between gap-3 border-t divider pt-4">
          <p className="text-xs text-slate-400 dark:text-slate-500">
            Revision {profile.personalization_version} — updated automatically when the system
            learns a repeated preference.
          </p>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving && <Spinner />}
            Save global profile
          </button>
        </div>
      </form>
    </section>
  )
}

/** Inline editor for one agent's own profile inside a domain group. */
function AgentProfileRow({ agent, profile, onSaved }) {
  const toast = useToast()
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [detail, setDetail] = useState(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [saving, setSaving] = useState(false)

  const Icon = agentIcon(agent.icon)
  const configured = Boolean(profile?.is_configured)

  const openEditor = async () => {
    setExpanded(true)
    setEditing(true)
    if (!detail) {
      setLoadingDetail(true)
      try {
        setDetail(await catalogApi.agent(agent.key))
      } catch (error) {
        toast.error(errorMessage(error, 'Could not load the form'))
        setEditing(false)
      } finally {
        setLoadingDetail(false)
      }
    }
  }

  const save = async (values) => {
    setSaving(true)
    try {
      const updated = await profileApi.saveAgent(agent.key, values)
      onSaved(agent.key, updated)
      setEditing(false)
      toast.success(`${agent.name} profile saved.`)
    } catch (error) {
      toast.error(errorMessage(error, 'Could not save the profile'))
    } finally {
      setSaving(false)
    }
  }

  const summaryRows = useMemo(() => {
    const data = profile?.profile_data || {}
    return Object.entries(data)
      .filter(([key, value]) => key !== 'history' && displayValue(value))
      .slice(0, 6)
  }, [profile])

  return (
    <li className="border-t divider first:border-t-0">
      <div className="flex items-center gap-3 px-4 py-3">
        <Icon className="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
        <button
          type="button"
          className="min-w-0 flex-1 text-left"
          onClick={() => setExpanded((open) => !open)}
          aria-expanded={expanded}
        >
          <span className="flex flex-wrap items-center gap-2">
            <span className="truncate text-sm font-medium">{agent.name}</span>
            <Badge tone={configured ? 'green' : 'amber'}>
              {configured ? (
                <>
                  <CheckCircle2 className="h-3 w-3" aria-hidden="true" /> Personalized
                </>
              ) : (
                <>
                  <Settings2 className="h-3 w-3" aria-hidden="true" /> Not configured
                </>
              )}
            </Badge>
            {agent.output_kind !== 'text' && (
              <Badge tone="brand">{OUTPUT_KIND_LABELS[agent.output_kind]}</Badge>
            )}
          </span>
          <span className="mt-0.5 block truncate text-xs text-slate-500 dark:text-slate-400">
            {agent.scope}
          </span>
        </button>

        <button
          type="button"
          className="btn-secondary px-2.5 py-1.5 text-xs"
          onClick={editing ? () => setEditing(false) : openEditor}
        >
          <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
          {editing ? 'Close' : configured ? 'Edit' : 'Set up'}
        </button>
        <button
          type="button"
          className="btn-ghost p-1.5"
          onClick={() => setExpanded((open) => !open)}
          aria-label={expanded ? 'Collapse' : 'Expand'}
        >
          <ChevronDown
            className={`h-4 w-4 transition-transform ${expanded ? '' : '-rotate-90'}`}
            aria-hidden="true"
          />
        </button>
      </div>

      {expanded && (
        <div className="border-t divider bg-slate-50/60 px-4 py-4 dark:bg-slate-800/30">
          {editing ? (
            loadingDetail ? (
              <div className="py-6">
                <Spinner className="mx-auto h-5 w-5" />
              </div>
            ) : detail ? (
              <AgentProfileForm
                fields={detail.profile_fields}
                initialData={profile?.profile_data || {}}
                onSubmit={save}
                onCancel={() => setEditing(false)}
                submitting={saving}
                submitLabel="Save profile"
                columns={2}
              />
            ) : null
          ) : summaryRows.length > 0 ? (
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              {summaryRows.map(([key, value]) => (
                <div key={key}>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
                    {key.replace(/_/g, ' ')}
                  </dt>
                  <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                    {displayValue(value)}
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                No {agent.name} profile yet. It falls back to the domain and global profiles.
              </p>
              <Link to={`/agent/${agent.key}/setup`} className="btn-primary text-xs">
                <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
                Personalize now
              </Link>
            </div>
          )}
        </div>
      )}
    </li>
  )
}

/** The brand profile — the middle level, shared by all five agents. */
function BrandProfileCard({ brand, profile, onSaved }) {
  const toast = useToast()
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  const tone = accent(brand?.accent)

  const answers = useMemo(() => {
    const data = profile?.profile_data || {}
    return (brand?.profile_fields || [])
      .map((field) => ({ label: field.label, value: displayValue(data[field.key]) }))
      .filter((row) => row.value)
  }, [brand, profile])

  const save = async (values) => {
    setSaving(true)
    try {
      const updated = await profileApi.saveBrand(values)
      onSaved(updated)
      setEditing(false)
      toast.success('Brand profile saved. All five agents use it.')
    } catch (error) {
      toast.error(errorMessage(error, 'Could not save the brand profile'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="card p-6" aria-labelledby="brand-profile-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span
            className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${tone.bg} ${tone.text}`}
          >
            <Layers className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 id="brand-profile-heading" className="flex flex-wrap items-center gap-2 font-semibold">
              Brand profile
              <Badge tone={profile?.is_configured ? 'green' : 'amber'}>
                {profile?.is_configured ? 'Saved' : 'Not answered yet'}
              </Badge>
            </h2>
            <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
              Level 2 of 3. Answered once and reused by all five agents — tone, audience and the
              colours the image agents render with.
            </p>
          </div>
        </div>
        <button
          type="button"
          className="btn-secondary px-2.5 py-1.5 text-xs"
          onClick={() => setEditing((value) => !value)}
        >
          <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
          {editing ? 'Close' : profile?.is_configured ? 'Edit' : 'Answer'}
        </button>
      </div>

      {editing ? (
        <div className="mt-5">
          <AgentProfileForm
            fields={brand?.profile_fields || []}
            initialData={profile?.profile_data || {}}
            onSubmit={save}
            onCancel={() => setEditing(false)}
            submitting={saving}
            submitLabel="Save brand profile"
            columns={2}
          />
        </div>
      ) : answers.length > 0 ? (
        <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-3">
          {answers.map((row) => (
            <div key={row.label}>
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
                {row.label}
              </dt>
              <dd className="mt-0.5 text-slate-800 dark:text-slate-200">{row.value}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="mt-5 text-sm text-slate-500 dark:text-slate-400">
          Not answered yet. Every agent would have to guess your brand, audience and tone.
        </p>
      )}
    </section>
  )
}

export default function ProfilePage() {
  const { agents, brand, reloadCatalog } = useAppShell()
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setOverview(await profileApi.overview())
    } catch (requestError) {
      setError(errorMessage(requestError, 'Could not load your profiles'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleAgentSaved = (agentKey, updated) => {
    setOverview((current) => ({
      ...current,
      agent_profiles: { ...current.agent_profiles, [agentKey]: updated },
    }))
    reloadCatalog()
  }

  if (loading) return <LoadingScreen label="Loading your profiles…" />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!overview) return null

  const agentProfiles = overview.agent_profiles ?? {}
  const brandProfile = overview.domain_profiles?.[DOMAIN] ?? null
  const configuredAgents = Object.values(agentProfiles).filter((item) => item?.is_configured).length

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-4xl px-5 py-8 sm:px-8">
        <header>
          <h1 className="text-2xl font-semibold">Profiles</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Three levels, most general first: you, your brand, then each agent. An agent reads all
            three — never another agent&apos;s.
          </p>
        </header>

        <div className="mt-6 space-y-6">
          <GlobalProfileCard
            profile={overview.global_profile}
            onSaved={(updated) =>
              setOverview((current) => ({ ...current, global_profile: updated }))
            }
          />

          <BrandProfileCard
            brand={brand}
            profile={brandProfile}
            onSaved={(updated) => {
              setOverview((current) => ({
                ...current,
                domain_profiles: { ...current.domain_profiles, [DOMAIN]: updated },
              }))
              reloadCatalog()
            }}
          />
        </div>

        <div className="mt-10">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold">Agent profiles</h2>
              <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                Level 3 of 3. The narrow specifics of one job — expand an agent to edit them.
              </p>
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {configuredAgents}/{agents.length || 5} personalized
            </span>
          </div>

          <section className="card overflow-hidden">
            <ul>
              {agents.map((agent) => (
                <AgentProfileRow
                  key={agent.key}
                  agent={agent}
                  profile={agentProfiles[agent.key]}
                  onSaved={handleAgentSaved}
                />
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
