import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Brain,
  CheckCircle2,
  Image as ImageIcon,
  MessageSquare,
  Moon,
  Palette,
  Settings2,
  Sparkles,
  Sun,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { useAppShell } from '../layouts/AppLayout'
import { dashboardApi, errorMessage } from '../services/api'
import { accent, agentIcon, OUTPUT_KIND_ICONS, OUTPUT_KIND_LABELS } from '../utils/agents'
import { Badge, CardSkeleton, ErrorState, Skeleton } from '../components/ui'
import { relativeTime } from '../utils/format'

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

/** One marketing agent. Clicking it opens the chat (or setup on first run). */
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

export default function DashboardPage() {
  const { user } = useAuth()
  const { agents, brand, brandProfile, brandConfigured, loadingCatalog, catalogError, reloadCatalog } =
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
  const tone = accent(brand?.accent)
  const brandName = brandProfile?.profile_data?.brand_name

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Hi {firstName}</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Five marketing agents, one deliverable each. They share your brand profile and keep
              their own specifics and memory.
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

        {/* The brand profile gates output quality for all five agents, so it is
            the first thing on the page until it is answered. */}
        <Link
          to="/brand"
          className={`card mt-6 flex flex-wrap items-center justify-between gap-3 p-4 transition-colors ${
            brandConfigured ? 'hover:border-brand-300' : 'border-amber-300 bg-amber-50 dark:border-amber-500/40 dark:bg-amber-500/10'
          }`}
        >
          <span className="flex items-center gap-3">
            <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${tone.bg} ${tone.text}`}>
              <Palette className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold">
                  {brandName ? `Brand: ${brandName}` : 'Brand profile'}
                </span>
                <Badge tone={brandConfigured ? 'green' : 'amber'}>
                  {brandConfigured ? 'Saved' : 'Not answered yet'}
                </Badge>
              </span>
              <span className="mt-0.5 block text-xs text-slate-600 dark:text-slate-400">
                {brandConfigured
                  ? 'Shared by all five agents — tone, audience and colours come from here.'
                  : 'Answer this once and every agent uses it. Output quality depends on it.'}
              </span>
            </span>
          </span>
          <span className="flex items-center gap-1 text-xs font-medium text-brand-600 dark:text-brand-400">
            {brandConfigured ? 'Edit brand' : 'Set up brand'}
            <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
          </span>
        </Link>

        <section className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Your activity">
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
            icon={ImageIcon}
            label="Graphics generated"
            value={stats?.images_generated ?? 0}
            loading={loadingStats}
          />
        </section>

        <section className="mt-8" aria-label="Marketing agents">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Pick the agent for your job</h2>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {agents.filter((a) => a.is_configured).length}/{agents.length || 5} personalized
            </span>
          </div>

          {catalogError ? (
            <ErrorState message={catalogError} onRetry={reloadCatalog} />
          ) : loadingCatalog ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 5 }).map((_, index) => (
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

        <p className="mt-6 flex items-start gap-2 px-1 text-xs text-slate-500 dark:text-slate-400">
          <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          Each agent refuses work that belongs to another and points you at the right one, so you
          never get a caption from the image generator.
        </p>
      </div>
    </div>
  )
}
