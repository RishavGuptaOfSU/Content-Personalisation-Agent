import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRightLeft,
  Brain,
  ChevronDown,
  Cpu,
  Globe,
  Layers,
  Pencil,
  Pin,
  Route,
  Settings2,
  Target,
  Trash2,
  X,
} from 'lucide-react'
import { Badge, Skeleton } from './ui'
import { accent, agentIcon, ROUTING_SOURCE_LABELS } from '../utils/agents'
import { displayValue, titleCase, truncate } from '../utils/format'

function Section({ icon: Icon, title, subtitle, children, defaultOpen = true, action }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <section className="border-b divider last:border-b-0">
      <div className="flex items-center gap-1 px-4 py-3">
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="flex min-w-0 flex-1 items-center gap-2 text-left"
          aria-expanded={open}
        >
          <Icon className="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-semibold">{title}</span>
            {subtitle && (
              <span className="block truncate text-xs text-slate-400 dark:text-slate-500">
                {subtitle}
              </span>
            )}
          </span>
          <ChevronDown
            className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${open ? '' : '-rotate-90'}`}
            aria-hidden="true"
          />
        </button>
        {action}
      </div>
      {open && <div className="px-4 pb-4">{children}</div>}
    </section>
  )
}

function KeyValueList({ data, fields, emptyLabel }) {
  const rows = (fields || [])
    .map((field) => ({ label: field.label, value: displayValue(data?.[field.key]) }))
    .filter((row) => row.value)

  if (rows.length === 0) {
    return <p className="text-xs text-slate-500 dark:text-slate-400">{emptyLabel}</p>
  }

  return (
    <dl className="space-y-2 text-xs">
      {rows.map((row) => (
        <div key={row.label}>
          <dt className="font-medium text-slate-500 dark:text-slate-400">{row.label}</dt>
          <dd className="mt-0.5 text-slate-800 dark:text-slate-200">{row.value}</dd>
        </div>
      ))}
    </dl>
  )
}

/**
 * Right panel: exactly which signals shaped the last response, in the same
 * order the prompt assembles them — global, then domain, then agent, then the
 * memories that were recalled, then the routing/scope decision.
 */
export default function PersonalizationPanel({
  agent,
  globalProfile,
  status,
  memories = [],
  memoryTotal = 0,
  lastTrace,
  lastRouting,
  lastScope,
  loading,
  onDeleteMemory,
  onClose,
}) {
  const Icon = agentIcon(agent?.icon)
  const DomainIcon = agentIcon(agent?.domain_icon)
  const tone = accent(agent?.domain_accent)
  const agentConfigured = Boolean(status?.agent_configured)
  const domainConfigured = Boolean(status?.domain_configured)

  return (
    <div className="flex h-full flex-col bg-white dark:bg-slate-900">
      <div className="flex items-center justify-between gap-2 border-b divider px-4 py-3">
        <h2 className="text-sm font-semibold">Personalization in use</h2>
        {onClose && (
          <button
            type="button"
            className="btn-ghost p-1.5"
            onClick={onClose}
            aria-label="Close panel"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <div className="space-y-3 p-4">
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-4/5" />
            <Skeleton className="mt-4 h-4 w-1/3" />
            <Skeleton className="h-3 w-full" />
          </div>
        ) : (
          <>
            {/* What this agent will and will not do */}
            {agent && (
              <Section icon={Target} title="This agent's job" subtitle={agent.tagline}>
                <p className={`text-xs ${tone.text}`}>{agent.scope}</p>
                {agent.out_of_scope?.length > 0 && (
                  <>
                    <p className="mt-2.5 text-[0.7rem] font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                      Hands off instead
                    </p>
                    <ul className="mt-1 space-y-0.5">
                      {agent.out_of_scope.map((item) => (
                        <li key={item} className="text-xs text-slate-500 dark:text-slate-400">
                          · {item}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </Section>
            )}

            {/* Level 3: this agent's own profile */}
            <Section
              icon={Icon}
              title={`${agent?.name ?? 'Agent'} profile`}
              subtitle="This agent only"
              action={
                agent && (
                  <Link
                    to={`/agent/${agent.key}/setup?step=agent&mode=edit`}
                    className="btn-ghost p-1.5"
                    aria-label={`Edit ${agent.name} profile`}
                    title="Edit this agent's profile"
                  >
                    <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
                  </Link>
                )
              }
            >
              <div className="mb-2.5">
                <Badge tone={agentConfigured ? 'green' : 'amber'}>
                  {agentConfigured ? 'Personalized' : 'Not configured'}
                </Badge>
              </div>
              <KeyValueList
                data={agent?.profile_data}
                fields={agent?.profile_fields}
                emptyLabel="Nothing set yet — the agent falls back to the domain profile."
              />
              {!agentConfigured && agent && (
                <Link
                  to={`/agent/${agent.key}/setup`}
                  className="btn-secondary mt-3 w-full text-xs"
                >
                  <Settings2 className="h-3.5 w-3.5" aria-hidden="true" />
                  Run the setup
                </Link>
              )}
            </Section>

            {/* Level 2: the domain profile shared with sibling agents */}
            <Section
              icon={DomainIcon}
              title={`${agent?.domain_name ?? 'Domain'} profile`}
              subtitle={`Shared by every ${agent?.domain_name ?? 'domain'} agent`}
              action={
                agent && (
                  <Link
                    to={`/agent/${agent.key}/setup?step=domain`}
                    className="btn-ghost p-1.5"
                    aria-label={`Edit ${agent.domain_name} domain profile`}
                    title="Edit the shared domain profile"
                  >
                    <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
                  </Link>
                )
              }
            >
              <div className="mb-2.5">
                <Badge tone={domainConfigured ? 'green' : 'amber'}>
                  {domainConfigured ? 'Saved' : 'Not answered yet'}
                </Badge>
              </div>
              <KeyValueList
                data={agent?.domain_profile_data}
                fields={agent?.domain_profile_fields}
                emptyLabel="Answer these once and every agent in the domain reuses them."
              />
            </Section>

            {/* Level 1: global */}
            <Section
              icon={Globe}
              title="Global profile"
              subtitle="Shared by every agent everywhere"
              action={
                <Link to="/profile" className="btn-ghost p-1.5" aria-label="Edit global profile">
                  <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
                </Link>
              }
            >
              {globalProfile ? (
                <dl className="space-y-2 text-xs">
                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">
                      Response length
                    </dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {titleCase(globalProfile.preferred_response_length)}
                    </dd>
                  </div>
                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">
                      Communication style
                    </dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {titleCase(globalProfile.communication_style)}
                    </dd>
                  </div>
                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">Skill level</dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {titleCase(globalProfile.general_skill_level)}
                    </dd>
                  </div>
                  {globalProfile.interests?.length > 0 && (
                    <div>
                      <dt className="font-medium text-slate-500 dark:text-slate-400">Interests</dt>
                      <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                        {globalProfile.interests.join(', ')}
                      </dd>
                    </div>
                  )}
                </dl>
              ) : (
                <p className="text-xs text-slate-500">Not loaded.</p>
              )}
            </Section>

            {/* Memories */}
            <Section
              icon={Brain}
              title="Memory"
              subtitle={`${memoryTotal} stored · ${memories.length} used in the last reply`}
            >
              {memories.length === 0 ? (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  No memories applied yet. Give feedback like “keep it concise” and it will be
                  remembered and reused here.
                </p>
              ) : (
                <ul className="space-y-2">
                  {memories.map((memory) => (
                    <li
                      key={memory.id}
                      className="group rounded-lg border divider bg-slate-50 p-2.5 text-xs dark:bg-slate-800/50"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="min-w-0 flex-1 text-slate-800 dark:text-slate-200">
                          {memory.content}
                        </p>
                        {onDeleteMemory && (
                          <button
                            type="button"
                            onClick={() => onDeleteMemory(memory)}
                            className="shrink-0 rounded p-1 text-slate-400 opacity-0 transition-opacity hover:text-rose-600 focus-visible:opacity-100 group-hover:opacity-100"
                            aria-label="Forget this memory"
                          >
                            <Trash2 className="h-3 w-3" aria-hidden="true" />
                          </button>
                        )}
                      </div>
                      <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[0.65rem] text-slate-500 dark:text-slate-400">
                        {memory.pinned && (
                          <span className="inline-flex items-center gap-0.5 rounded bg-brand-100 px-1.5 py-0.5 font-medium text-brand-700 dark:bg-brand-500/20 dark:text-brand-300">
                            <Pin className="h-2.5 w-2.5" aria-hidden="true" />
                            standing
                          </span>
                        )}
                        <span className="rounded bg-slate-200 px-1.5 py-0.5 dark:bg-slate-700">
                          {memory.kind}
                        </span>
                        {/* Which level this memory is attached to. */}
                        <span
                          className="inline-flex items-center gap-0.5"
                          title="Memory scope: agent, domain or global"
                        >
                          <Layers className="h-2.5 w-2.5" aria-hidden="true" />
                          {memory.scope || memory.agent_key || memory.domain || 'global'}
                        </span>
                        {typeof memory.similarity === 'number' && (
                          <span>relevance {(memory.similarity * 100).toFixed(0)}%</span>
                        )}
                        {memory.occurrences > 1 && <span>seen {memory.occurrences}×</span>}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
              <Link to="/settings" className="btn-ghost mt-3 w-full text-xs">
                Manage all memories
              </Link>
            </Section>

            {/* Routing + scope + provider */}
            <Section icon={Route} title="Last request" defaultOpen={Boolean(lastTrace)}>
              {lastTrace ? (
                <dl className="space-y-2 text-xs">
                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">Routed to</dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {lastRouting?.agent_name ?? lastRouting?.agent_key} —{' '}
                      {ROUTING_SOURCE_LABELS[lastRouting?.source] ?? lastRouting?.source}
                      {lastRouting?.source !== 'explicit' &&
                        typeof lastRouting?.confidence === 'number' &&
                        ` (${Math.round(lastRouting.confidence * 100)}%)`}
                    </dd>
                    {lastRouting?.reason && (
                      <dd className="mt-0.5 text-slate-500 dark:text-slate-400">
                        {lastRouting.reason}
                      </dd>
                    )}
                  </div>

                  {lastScope && lastScope.in_scope === false && (
                    <div className="rounded-lg border border-amber-200 bg-amber-50 p-2 dark:border-amber-500/30 dark:bg-amber-500/10">
                      <dt className="flex items-center gap-1 font-medium text-amber-800 dark:text-amber-200">
                        <ArrowRightLeft className="h-3 w-3" aria-hidden="true" />
                        Out of scope
                      </dt>
                      <dd className="mt-0.5 text-amber-900 dark:text-amber-200">
                        {lastScope.reason}
                      </dd>
                      {lastScope.suggested_agent_key && (
                        <dd className="mt-1.5">
                          <Link
                            to={`/agent/${lastScope.suggested_agent_key}`}
                            className="btn-secondary w-full px-2 py-1 text-xs"
                          >
                            Switch to {lastScope.suggested_agent_name}
                          </Link>
                        </dd>
                      )}
                    </div>
                  )}

                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">
                      Deliverable
                    </dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {lastTrace.output_kind}
                    </dd>
                  </div>
                  <div>
                    <dt className="font-medium text-slate-500 dark:text-slate-400">
                      Context assembled
                    </dt>
                    <dd className="mt-0.5 text-slate-800 dark:text-slate-200">
                      {lastTrace.context_characters.toLocaleString()} characters ·{' '}
                      {lastTrace.short_term_messages} recent messages ·{' '}
                      {lastTrace.memories_used?.length ?? 0} memories
                    </dd>
                    <dd className="mt-0.5 text-slate-500 dark:text-slate-400">
                      profile lines — global {lastTrace.global_profile_summary?.length ?? 0} ·
                      domain {lastTrace.domain_profile_summary?.length ?? 0} · agent{' '}
                      {lastTrace.agent_profile_summary?.length ?? 0}
                    </dd>
                  </div>
                  <div>
                    <dt className="flex items-center gap-1 font-medium text-slate-500 dark:text-slate-400">
                      <Cpu className="h-3 w-3" aria-hidden="true" /> Provider
                    </dt>
                    <dd className="mt-0.5 break-all text-slate-800 dark:text-slate-200">
                      {lastTrace.provider} · {lastTrace.model}
                    </dd>
                  </div>
                  <details className="mt-2">
                    <summary className="cursor-pointer font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200">
                      System prompt preview
                    </summary>
                    <pre className="mt-1.5 max-h-40 overflow-auto whitespace-pre-wrap rounded bg-slate-100 p-2 font-mono text-[0.65rem] leading-relaxed text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                      {truncate(lastTrace.system_prompt_preview, 1200)}
                    </pre>
                  </details>
                </dl>
              ) : (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Send a message to see how it was routed and what context was used.
                </p>
              )}
            </Section>
          </>
        )}
      </div>
    </div>
  )
}
