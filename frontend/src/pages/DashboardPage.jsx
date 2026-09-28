import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  Brain,
  CheckCircle2,
  Image as ImageIcon,
  MessageSquare,
  Moon,
  Settings2,
  Sun,
  Users,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { useAppShell } from '../layouts/AppLayout'
import { dashboardApi, errorMessage } from '../services/api'
import { accent, agentIcon } from '../utils/agents'
import { Badge, CardSkeleton, ErrorState, Skeleton } from '../components/ui'
import { pluralize, relativeTime } from '../utils/format'

function StatCard({ icon: Icon, label, value, loading }) {
  return (
    <div className="card flex items-center gap-3 p-4">
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
        <Icon className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        {loading ? (
          <Skeleton className="h-6 w-10" />
        ) : (
          <p className="text-xl font-semibold leading-none">{value}</p>
        )}
        <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{label}</p>
      </div>
    </div>
  )
}

/** One domain card. Clicking it opens the list of agents inside the domain. */
function DomainCard({ domain, agents = [] }) {
  const Icon = agentIcon(domain.icon)
  const tone = accent(domain.accent)
  const configured = domain.configured_agents > 0
  const visualCount = domain.visual_agents?.length ?? 0

  return (
    <Link
      to={`/domain/${domain.key}`}
      className={`card group flex flex-col p-5 transition-all hover:-translate-y-0.5 hover:shadow-md ${tone.hoverBorder}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className={`grid h-10 w-10 place-items-center rounded-lg ${tone.bg} ${tone.text}`}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        <Badge tone={configured ? 'green' : 'amber'}>
          {configured ? (
            <>
              <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
              {domain.configured_agents} of {domain.agent_count} set up
            </>
          ) : (
            <>
              <Settings2 className="h-3 w-3" aria-hidden="true" /> Not configured
            </>
          )}
        </Badge>
      </div>

      <h3 className="mt-3.5 font-semibold text-slate-900 dark:text-slate-100">{domain.name}</h3>
      <p className={`mt-0.5 text-xs font-medium ${tone.text}`}>{domain.tagline}</p>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{domain.description}</p>

      {/* A preview of the narrow agents this domain contains. */}
      <ul className="mt-3.5 flex flex-1 flex-wrap gap-1.5 content-start">
        {agents.slice(0, 4).map((agent) => (
          <li
            key={agent.key}
            className="rounded-md bg-slate-100 px-2 py-0.5 text-[0.7rem] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
          >
            {agent.name}
          </li>
        ))}
        {agents.length > 4 && (
          <li className="rounded-md px-2 py-0.5 text-[0.7rem] font-medium text-slate-400 dark:text-slate-500">
            +{agents.length - 4} more
          </li>
        )}
      </ul>

      <div className="mt-4 flex items-center justify-between border-t divider pt-3 text-xs text-slate-500 dark:text-slate-400">
        <span className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" aria-hidden="true" />
            {pluralize(domain.agent_count, 'agent')}
          </span>
          {domain.conversation_count > 0 && (
            <span className="flex items-center gap-1">
              <MessageSquare className="h-3.5 w-3.5" aria-hidden="true" />
              {domain.conversation_count}
            </span>
          )}
          {visualCount > 0 && (
            <span className="flex items-center gap-1" title="Agents that produce images or charts">
              <ImageIcon className="h-3.5 w-3.5" aria-hidden="true" />
              {visualCount}
            </span>
          )}
        </span>
        <span className="flex items-center gap-1 font-medium text-brand-600 opacity-0 transition-opacity group-hover:opacity-100 dark:text-brand-400">
          Browse agents
          <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
        </span>
      </div>

      {domain.last_used_at && (
        <p className="mt-2 text-[0.7rem] text-slate-400 dark:text-slate-500">
          Last used {relativeTime(domain.last_used_at)}
        </p>
      )}
    </Link>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { domains, agentsByDomain, agents, loadingCatalog, catalogError, reloadCatalog } =
    useAppShell()
  const { isDark, toggle } = useTheme()
  const [stats, setStats] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)

  useEffect(() => {
    let cancelled = false
    dashboardApi
      .stats()
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((error) => console.warn('stats failed:', errorMessage(error)))
      .finally(() => {
        if (!cancelled) setLoadingStats(false)
      })
    return () => {
      cancelled = true
    }
  }, [agents])

  const firstName = (user?.name || '').split(' ')[0] || 'there'
  const visualAgents = agents.filter((agent) => agent.output_kind !== 'text')

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Hi {firstName}</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Pick a domain, then the agent for the exact job. Each agent does one thing and keeps
              its own profile and memory.
            </p>
          </div>
          <button
            type="button"
            onClick={toggle}
            className="btn-secondary hidden lg:inline-flex"
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? (
              <Sun className="h-4 w-4" aria-hidden="true" />
            ) : (
              <Moon className="h-4 w-4" aria-hidden="true" />
            )}
            {isDark ? 'Light' : 'Dark'}
          </button>
        </header>

        <section className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Your activity">
          <StatCard
            icon={MessageSquare}
            label="Conversations"
            value={stats?.total_conversations ?? 0}
            loading={loadingStats}
          />
          <StatCard
            icon={Brain}
            label="Memories learned"
            value={stats?.total_memories ?? 0}
            loading={loadingStats}
          />
          <StatCard
            icon={CheckCircle2}
            label="Agents personalized"
            value={`${stats?.configured_agents ?? 0}/${stats?.total_agents ?? agents.length}`}
            loading={loadingStats}
          />
          <StatCard
            icon={BarChart3}
            label="Images & charts made"
            value={stats?.images_generated ?? 0}
            loading={loadingStats}
          />
        </section>

        {visualAgents.length > 0 && !loadingCatalog && (
          <section className="mt-6" aria-label="Agents that produce visuals">
            <div className="rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 dark:border-brand-500/30 dark:bg-brand-500/10">
              <p className="text-sm font-medium text-brand-900 dark:text-brand-200">
                Some agents hand back a file, not text
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {visualAgents.map((agent) => {
                  const Icon = agentIcon(agent.icon)
                  return (
                    <Link
                      key={agent.key}
                      to={`/agent/${agent.key}`}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-brand-200 bg-white px-2.5 py-1 text-xs font-medium text-brand-800 transition-colors hover:bg-brand-100 dark:border-brand-500/30 dark:bg-slate-900 dark:text-brand-200 dark:hover:bg-brand-500/20"
                    >
                      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                      {agent.name}
                      <span className="text-brand-500 dark:text-brand-400">
                        · {agent.output_kind}
                      </span>
                    </Link>
                  )
                })}
              </div>
            </div>
          </section>
        )}

        <section className="mt-8" aria-label="Domains">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Domains</h2>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {domains.length || 7} domains · {agents.length || 34} agents
            </span>
          </div>

          {catalogError ? (
            <ErrorState message={catalogError} onRetry={reloadCatalog} />
          ) : loadingCatalog ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <CardSkeleton key={index} />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {domains.map((domain) => (
                <DomainCard
                  key={domain.key}
                  domain={domain}
                  agents={agentsByDomain[domain.key] ?? []}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
