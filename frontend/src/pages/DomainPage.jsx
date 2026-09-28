import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Brain,
  CheckCircle2,
  MessageSquare,
  Pencil,
  Settings2,
} from 'lucide-react'
import { Badge, CardSkeleton, ErrorState, LoadingScreen } from '../components/ui'
import { useAppShell } from '../layouts/AppLayout'
import { catalogApi, errorMessage, profileApi } from '../services/api'
import { accent, agentIcon, OUTPUT_KIND_ICONS, OUTPUT_KIND_LABELS } from '../utils/agents'
import { displayValue, pluralize, relativeTime } from '../utils/format'

/** One agent card inside a domain. */
function AgentCard({ agent, tone }) {
  const Icon = agentIcon(agent.icon)
  const KindIcon = OUTPUT_KIND_ICONS[agent.output_kind]
  const visual = agent.output_kind !== 'text'

  return (
    <Link
      to={`/agent/${agent.key}`}
      className={`card group flex flex-col p-5 transition-all hover:-translate-y-0.5 hover:shadow-md ${tone.hoverBorder}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className={`grid h-10 w-10 place-items-center rounded-lg ${tone.bg} ${tone.text}`}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        <span className="flex flex-col items-end gap-1.5">
          <Badge tone={agent.is_configured ? 'green' : 'amber'}>
            {agent.is_configured ? (
              <>
                <CheckCircle2 className="h-3 w-3" aria-hidden="true" /> Personalized
              </>
            ) : (
              <>
                <Settings2 className="h-3 w-3" aria-hidden="true" /> Not configured
              </>
            )}
          </Badge>
          {visual && (
            <Badge tone="brand">
              {KindIcon && <KindIcon className="h-3 w-3" aria-hidden="true" />}
              {OUTPUT_KIND_LABELS[agent.output_kind]}
            </Badge>
          )}
        </span>
      </div>

      <h3 className="mt-3.5 font-semibold text-slate-900 dark:text-slate-100">{agent.name}</h3>
      <p className={`mt-0.5 text-xs font-medium ${tone.text}`}>{agent.tagline}</p>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{agent.description}</p>

      <div className="mt-3 rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800/60">
        <p className="text-[0.7rem] font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
          Does only this
        </p>
        <p className="mt-0.5 text-xs text-slate-600 dark:text-slate-300">{agent.scope}</p>
      </div>

      {agent.examples?.length > 0 && (
        <ul className="mt-3 flex-1 space-y-1">
          {agent.examples.slice(0, 2).map((example) => (
            <li
              key={example}
              className="truncate text-xs text-slate-500 dark:text-slate-400"
              title={example}
            >
              “{example}”
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex items-center justify-between border-t divider pt-3 text-xs text-slate-500 dark:text-slate-400">
        <span className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <MessageSquare className="h-3.5 w-3.5" aria-hidden="true" />
            {agent.conversation_count}
          </span>
          {agent.memory_count > 0 && (
            <span className="flex items-center gap-1">
              <Brain className="h-3.5 w-3.5" aria-hidden="true" />
              {agent.memory_count}
            </span>
          )}
          {agent.last_used_at && <span>{relativeTime(agent.last_used_at)}</span>}
        </span>
        <span className="flex items-center gap-1 font-medium text-brand-600 opacity-0 transition-opacity group-hover:opacity-100 dark:text-brand-400">
          {agent.is_configured ? 'Open' : 'Set up'}
          <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
        </span>
      </div>
    </Link>
  )
}

export default function DomainPage() {
  const { domain: domainKey } = useParams()
  const navigate = useNavigate()
  const { domainsByKey, loadingCatalog, catalogError, reloadCatalog } = useAppShell()

  const [agents, setAgents] = useState([])
  const [domain, setDomain] = useState(null)
  const [domainProfile, setDomainProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [domainDetail, agentList, profile] = await Promise.all([
        catalogApi.domain(domainKey),
        catalogApi.domainAgents(domainKey),
        profileApi.getDomain(domainKey),
      ])
      setDomain(domainDetail)
      setAgents(agentList)
      setDomainProfile(profile)
    } catch (requestError) {
      if (requestError.response?.status === 404) {
        setError(`There is no “${domainKey}” domain.`)
      } else {
        setError(errorMessage(requestError, 'Could not load this domain'))
      }
    } finally {
      setLoading(false)
    }
  }, [domainKey])

  useEffect(() => {
    load()
  }, [load])

  const card = domain ?? domainsByKey[domainKey]
  const tone = accent(card?.accent)
  const Icon = agentIcon(card?.icon)

  const domainAnswers = useMemo(() => {
    const data = domainProfile?.profile_data || {}
    return (card?.profile_fields || [])
      .map((field) => ({ label: field.label, value: displayValue(data[field.key]) }))
      .filter((row) => row.value)
  }, [card, domainProfile])

  if (loading && !card) return <LoadingScreen label="Loading domain…" />
  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-5 py-10">
        <ErrorState message={error} onRetry={load} />
        <button type="button" className="btn-secondary mt-4" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to domains
        </button>
      </div>
    )
  }
  if (!card) return null

  const configuredCount = agents.filter((agent) => agent.is_configured).length

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">
        <Link to="/dashboard" className="btn-ghost -ml-2 mb-5 text-sm">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          All domains
        </Link>

        <header className="flex flex-wrap items-start gap-4">
          <span
            className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl ${tone.bg} ${tone.text}`}
          >
            <Icon className="h-6 w-6" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-semibold">{card.name}</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{card.description}</p>
          </div>
        </header>

        {/* The domain profile: answered once, reused by every agent below. */}
        <section
          className="card mt-6 p-5"
          aria-label={`${card.name} domain profile`}
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="flex items-center gap-2 text-sm font-semibold">
                Shared {card.name.toLowerCase()} profile
                <Badge tone={domainProfile?.is_configured ? 'green' : 'amber'}>
                  {domainProfile?.is_configured ? 'Saved' : 'Not answered yet'}
                </Badge>
              </h2>
              <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                Answered once and reused by all {pluralize(card.agent_count, 'agent')} in this
                domain — you will not be asked again per agent.
              </p>
            </div>
            {agents[0] && (
              <Link
                to={`/agent/${agents[0].key}/setup?step=domain`}
                className="btn-secondary px-2.5 py-1.5 text-xs"
              >
                <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
                {domainProfile?.is_configured ? 'Edit' : 'Answer now'}
              </Link>
            )}
          </div>

          {domainAnswers.length > 0 ? (
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
              {domainAnswers.map((row) => (
                <div key={row.label}>
                  <dt className="text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
                    {row.label}
                  </dt>
                  <dd className="mt-0.5 text-slate-800 dark:text-slate-200">{row.value}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <ul className="mt-4 flex flex-wrap gap-1.5">
              {(card.profile_fields || []).map((field) => (
                <li
                  key={field.key}
                  className="rounded-md bg-slate-100 px-2 py-0.5 text-[0.7rem] text-slate-500 dark:bg-slate-800 dark:text-slate-400"
                >
                  {field.label}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="mt-8" aria-label={`Agents in ${card.name}`}>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Pick the agent for your job</h2>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {configuredCount}/{agents.length || card.agent_count} personalized
            </span>
          </div>

          {catalogError ? (
            <ErrorState message={catalogError} onRetry={reloadCatalog} />
          ) : loading || loadingCatalog ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: card.agent_count || 4 }).map((_, index) => (
                <CardSkeleton key={index} />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <AgentCard key={agent.key} agent={agent} tone={tone} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
