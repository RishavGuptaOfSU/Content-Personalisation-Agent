import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, CheckCircle2, Palette, Settings2, Users } from 'lucide-react'
import AgentProfileForm from '../components/AgentProfileForm'
import { Badge, ErrorState, LoadingScreen } from '../components/ui'
import { useToast } from '../context/ToastContext'
import { useAppShell } from '../layouts/AppLayout'
import { catalogApi, errorMessage, profileApi } from '../services/api'
import { accent, agentIcon } from '../utils/agents'
import { displayValue, pluralize } from '../utils/format'

/**
 * The brand profile — the domain-level profile, answered once and reused by all
 * five agents. In a single-domain product this is the most important screen:
 * tone, audience and brand colours set here shape every caption and every
 * rendered graphic.
 */
export default function BrandPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { agents, reloadCatalog } = useAppShell()

  const [brand, setBrand] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [card, saved] = await Promise.all([catalogApi.brand(), profileApi.getBrand()])
      setBrand(card)
      setProfile(saved)
      setEditing(!saved?.is_configured)
    } catch (requestError) {
      setError(errorMessage(requestError, 'Could not load the brand profile'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const save = async (values) => {
    setSaving(true)
    try {
      const updated = await profileApi.saveBrand(values)
      setProfile(updated)
      setEditing(false)
      await reloadCatalog()
      toast.success('Brand profile saved. All five agents use it from the next message.')
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Could not save the brand profile'))
    } finally {
      setSaving(false)
    }
  }

  const answers = useMemo(() => {
    const data = profile?.profile_data || {}
    return (brand?.profile_fields || [])
      .map((field) => ({ label: field.label, value: displayValue(data[field.key]) }))
      .filter((row) => row.value)
  }, [brand, profile])

  if (loading) return <LoadingScreen label="Loading brand profile…" />
  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-5 py-10">
        <ErrorState message={error} onRetry={load} />
      </div>
    )
  }
  if (!brand) return null

  const tone = accent(brand.accent)
  const configured = Boolean(profile?.is_configured)

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-3xl px-5 py-8 sm:px-8">
        <button type="button" className="btn-ghost -ml-2 mb-5 text-sm" onClick={() => navigate('/agents')}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          All agents
        </button>

        <header className="flex flex-wrap items-start gap-4">
          <span className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl ${tone.bg} ${tone.text}`}>
            <Palette className="h-6 w-6" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <h1 className="flex flex-wrap items-center gap-2 text-2xl font-semibold">
              Brand profile
              <Badge tone={configured ? 'green' : 'amber'}>
                {configured ? (
                  <>
                    <CheckCircle2 className="h-3 w-3" aria-hidden="true" /> Saved
                  </>
                ) : (
                  <>
                    <Settings2 className="h-3 w-3" aria-hidden="true" /> Not answered yet
                  </>
                )}
              </Badge>
            </h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Answered once and reused by all {pluralize(brand.agent_count, 'agent')}. Your brand
              colours are what the image agents render with, and the tone is what every caption
              inherits.
            </p>
          </div>
        </header>

        <section className="card mt-6 p-6">
          {editing ? (
            <AgentProfileForm
              fields={brand.profile_fields}
              initialData={profile?.profile_data || {}}
              onSubmit={save}
              onCancel={configured ? () => setEditing(false) : undefined}
              submitting={saving}
              submitLabel="Save brand profile"
              columns={2}
            />
          ) : (
            <>
              <div className="flex items-start justify-between gap-3">
                <h2 className="text-sm font-semibold">Your answers</h2>
                <button
                  type="button"
                  className="btn-secondary px-2.5 py-1.5 text-xs"
                  onClick={() => setEditing(true)}
                >
                  Edit
                </button>
              </div>
              <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
                {answers.map((row) => (
                  <div key={row.label}>
                    <dt className="text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
                      {row.label}
                    </dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">{row.value}</dd>
                  </div>
                ))}
              </dl>
            </>
          )}
        </section>

        <section className="mt-6" aria-label="Agents using this profile">
          <h2 className="flex items-center gap-2 text-sm font-semibold">
            <Users className="h-4 w-4 text-slate-400" aria-hidden="true" />
            Agents using these answers
          </h2>
          <ul className="mt-3 divide-y divider overflow-hidden rounded-xl border divider">
            {agents.map((agent) => {
              const Icon = agentIcon(agent.icon)
              return (
                <li key={agent.key}>
                  <Link
                    to={`/agent/${agent.key}`}
                    className="flex items-center gap-3 bg-white px-4 py-3 transition-colors hover:bg-slate-50 dark:bg-slate-900 dark:hover:bg-slate-800/60"
                  >
                    <Icon className={`h-4 w-4 shrink-0 ${tone.text}`} aria-hidden="true" />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{agent.name}</span>
                      <span className="block truncate text-xs text-slate-500 dark:text-slate-400">
                        {agent.tagline}
                      </span>
                    </span>
                    <Badge tone={agent.is_configured ? 'green' : 'amber'}>
                      {agent.is_configured ? 'Personalized' : 'Needs setup'}
                    </Badge>
                    <ArrowRight className="h-3.5 w-3.5 shrink-0 text-slate-300 dark:text-slate-600" aria-hidden="true" />
                  </Link>
                </li>
              )
            })}
          </ul>
        </section>
      </div>
    </div>
  )
}
