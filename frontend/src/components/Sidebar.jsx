import { useEffect, useMemo, useState } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  Check,
  ChevronDown,
  LayoutDashboard,
  LogOut,
  MessageSquarePlus,
  MoreHorizontal,
  Pencil,
  Settings,
  Sparkles,
  Trash2,
  User,
  X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { accent, agentIcon, OUTPUT_KIND_ICONS } from '../utils/agents'
import { groupByDay, truncate } from '../utils/format'
import { Skeleton } from './ui'

function navClasses({ isActive }) {
  return `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? 'bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-200'
      : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
  }`
}

function ConversationRow({ conversation, agentsByKey, active, onRename, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [renaming, setRenaming] = useState(false)
  const [draft, setDraft] = useState(conversation.title)

  const definition = agentsByKey[conversation.agent_key]
  const Icon = agentIcon(definition?.icon)
  const tone = accent(definition?.accent)

  useEffect(() => setDraft(conversation.title), [conversation.title])

  if (renaming) {
    return (
      <li className="px-1 py-0.5">
        <form
          className="flex items-center gap-1"
          onSubmit={(event) => {
            event.preventDefault()
            const next = draft.trim()
            if (next && next !== conversation.title) onRename(conversation, next)
            setRenaming(false)
          }}
        >
          <input
            autoFocus
            className="input px-2 py-1 text-xs"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                setDraft(conversation.title)
                setRenaming(false)
              }
            }}
            aria-label="Conversation title"
          />
          <button type="submit" className="btn-ghost p-1" aria-label="Save title">
            <Check className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
          <button
            type="button"
            className="btn-ghost p-1"
            onClick={() => {
              setDraft(conversation.title)
              setRenaming(false)
            }}
            aria-label="Cancel rename"
          >
            <X className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </form>
      </li>
    )
  }

  return (
    <li className="group relative">
      <Link
        to={`/agent/${conversation.agent_key}?conversation=${conversation.id}`}
        className={`flex items-start gap-2 rounded-lg px-2.5 py-2 text-sm transition-colors ${
          active
            ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
            : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/70'
        }`}
        title={`${conversation.title} — ${definition?.name ?? conversation.agent_key}`}
      >
        <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${tone.text}`} aria-hidden="true" />
        <span className="min-w-0 flex-1">
          <span className="block truncate font-medium">{truncate(conversation.title, 30)}</span>
          <span className="mt-0.5 block truncate text-xs text-slate-400 dark:text-slate-500">
            {definition?.name ?? conversation.agent_key}
          </span>
        </span>
      </Link>

      <button
        type="button"
        onClick={(event) => {
          event.preventDefault()
          setMenuOpen((open) => !open)
        }}
        className="absolute right-1 top-1.5 rounded p-1 text-slate-400 opacity-0 transition-opacity hover:bg-slate-200 focus-visible:opacity-100 group-hover:opacity-100 dark:hover:bg-slate-700"
        aria-label={`Actions for ${conversation.title}`}
        aria-expanded={menuOpen}
      >
        <MoreHorizontal className="h-3.5 w-3.5" aria-hidden="true" />
      </button>

      {menuOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setMenuOpen(false)}
            aria-hidden="true"
          />
          <div className="card absolute right-1 top-8 z-20 w-36 p-1 text-sm shadow-lg">
            <button
              type="button"
              className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={() => {
                setMenuOpen(false)
                setRenaming(true)
              }}
            >
              <Pencil className="h-3.5 w-3.5" aria-hidden="true" /> Rename
            </button>
            <button
              type="button"
              className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-500/10"
              onClick={() => {
                setMenuOpen(false)
                onDelete(conversation)
              }}
            >
              <Trash2 className="h-3.5 w-3.5" aria-hidden="true" /> Delete
            </button>
          </div>
        </>
      )}
    </li>
  )
}

/** One collapsible domain with the narrow agents it contains. */
function DomainGroup({ domain, agents, activeAgentKey, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  const DomainIcon = agentIcon(domain.icon)
  const tone = accent(domain.accent)

  useEffect(() => {
    if (defaultOpen) setOpen(true)
  }, [defaultOpen])

  return (
    <li>
      <div className="flex items-center gap-1">
        <button
          type="button"
          className="flex min-w-0 flex-1 items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/70"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
        >
          <DomainIcon className={`h-4 w-4 shrink-0 ${tone.text}`} aria-hidden="true" />
          <span className="min-w-0 flex-1 truncate font-medium">{domain.name}</span>
          <span className="shrink-0 text-[0.65rem] text-slate-400 dark:text-slate-500">
            {domain.configured_agents}/{domain.agent_count}
          </span>
          <ChevronDown
            className={`h-3.5 w-3.5 shrink-0 text-slate-400 transition-transform ${open ? '' : '-rotate-90'}`}
            aria-hidden="true"
          />
        </button>
      </div>

      {open && (
        <ul className="mb-1 ml-3 space-y-0.5 border-l divider pl-2">
          <li>
            <Link
              to={`/domain/${domain.key}`}
              className="block rounded-lg px-2 py-1 text-[0.7rem] font-medium text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:text-slate-500 dark:hover:bg-slate-800/70 dark:hover:text-slate-300"
            >
              All {domain.name.toLowerCase()} agents
            </Link>
          </li>
          {agents.map((agent) => {
            const Icon = agentIcon(agent.icon)
            const KindIcon = OUTPUT_KIND_ICONS[agent.output_kind]
            const active = activeAgentKey === agent.key
            return (
              <li key={agent.key}>
                <Link
                  to={`/agent/${agent.key}`}
                  className={`flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs transition-colors ${
                    active
                      ? 'bg-slate-100 font-medium text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                      : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/70'
                  }`}
                  title={agent.scope}
                >
                  <Icon className={`h-3.5 w-3.5 shrink-0 ${tone.text}`} aria-hidden="true" />
                  <span className="min-w-0 flex-1 truncate">{agent.name}</span>
                  {agent.output_kind !== 'text' && KindIcon && (
                    <KindIcon
                      className="h-3 w-3 shrink-0 text-brand-500 dark:text-brand-400"
                      aria-label={`Produces ${agent.output_kind}`}
                    />
                  )}
                  {agent.is_configured ? (
                    <span
                      className="h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500"
                      title="Personalized"
                      aria-label="Personalized"
                    />
                  ) : (
                    <span
                      className="h-1.5 w-1.5 shrink-0 rounded-full bg-slate-300 dark:bg-slate-600"
                      title="Not configured"
                      aria-label="Not configured"
                    />
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      )}
    </li>
  )
}

export default function Sidebar({
  domains = [],
  agentsByDomain = {},
  agentsByKey = {},
  conversations = [],
  loadingConversations,
  activeConversationId,
  onRenameConversation,
  onDeleteConversation,
  onClose,
}) {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [catalogOpen, setCatalogOpen] = useState(true)

  const grouped = useMemo(
    () => groupByDay(conversations, (item) => item.updated_at),
    [conversations],
  )

  // `/agent/marketing.post-image` -> `marketing.post-image`
  const activeAgentKey = location.pathname.startsWith('/agent/')
    ? decodeURIComponent(location.pathname.split('/')[2] ?? '')
    : null
  const activeDomain = activeAgentKey
    ? activeAgentKey.split('.')[0]
    : location.pathname.startsWith('/domain/')
      ? location.pathname.split('/')[2]
      : null

  return (
    <div className="flex h-full w-full flex-col bg-white dark:bg-slate-900">
      {/* Logo */}
      <div className="flex items-center justify-between gap-2 px-4 py-4">
        <Link to="/dashboard" className="flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="text-sm font-semibold leading-tight">
            Content
            <br />
            Personalization
          </span>
        </Link>
        {onClose && (
          <button
            type="button"
            className="btn-ghost p-1.5 lg:hidden"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
      </div>

      <div className="px-3">
        <button
          type="button"
          className="btn-primary w-full"
          onClick={() => navigate(activeAgentKey ? `/agent/${activeAgentKey}` : '/dashboard')}
        >
          <MessageSquarePlus className="h-4 w-4" aria-hidden="true" />
          New chat
        </button>
      </div>

      <nav className="mt-4 space-y-1 px-3" aria-label="Main">
        <NavLink to="/dashboard" className={navClasses}>
          <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
          Domains
        </NavLink>
        <NavLink to="/profile" className={navClasses}>
          <User className="h-4 w-4" aria-hidden="true" />
          Profiles
        </NavLink>
        <NavLink to="/settings" className={navClasses}>
          <Settings className="h-4 w-4" aria-hidden="true" />
          Settings
        </NavLink>
      </nav>

      {/* Catalog: domain → agents */}
      <div className="mt-5 max-h-[45%] overflow-y-auto px-3">
        <button
          type="button"
          className="flex w-full items-center justify-between px-1 text-[0.7rem] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500"
          onClick={() => setCatalogOpen((open) => !open)}
          aria-expanded={catalogOpen}
        >
          Catalog
          <ChevronDown
            className={`h-3.5 w-3.5 transition-transform ${catalogOpen ? '' : '-rotate-90'}`}
            aria-hidden="true"
          />
        </button>
        {catalogOpen && (
          <ul className="mt-1.5 space-y-0.5">
            {domains.length === 0 &&
              Array.from({ length: 7 }).map((_, index) => (
                <li key={index} className="px-2 py-1.5">
                  <Skeleton className="h-4 w-full" />
                </li>
              ))}
            {domains.map((domain) => (
              <DomainGroup
                key={domain.key}
                domain={domain}
                agents={agentsByDomain[domain.key] ?? []}
                activeAgentKey={activeAgentKey}
                defaultOpen={activeDomain === domain.key}
              />
            ))}
          </ul>
        )}
      </div>

      {/* Recent conversations */}
      <div className="mt-5 min-h-0 flex-1 overflow-y-auto px-3 pb-2">
        <p className="px-1 text-[0.7rem] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          Recent
        </p>
        {loadingConversations ? (
          <ul className="mt-2 space-y-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <li key={index} className="px-2">
                <Skeleton className="h-4 w-full" />
              </li>
            ))}
          </ul>
        ) : conversations.length === 0 ? (
          <p className="mt-2 px-1 text-xs text-slate-400 dark:text-slate-500">
            No conversations yet. Pick a domain, then an agent.
          </p>
        ) : (
          <div className="mt-1.5 space-y-3">
            {grouped.map(([label, items]) => (
              <div key={label}>
                <p className="px-1 py-1 text-[0.65rem] font-medium uppercase tracking-wider text-slate-400 dark:text-slate-600">
                  {label}
                </p>
                <ul className="space-y-0.5">
                  {items.map((conversation) => (
                    <ConversationRow
                      key={conversation.id}
                      conversation={conversation}
                      agentsByKey={agentsByKey}
                      active={conversation.id === activeConversationId}
                      onRename={onRenameConversation}
                      onDelete={onDeleteConversation}
                    />
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* User */}
      <div className="border-t divider p-3">
        <div className="flex items-center gap-2.5">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-200 text-xs font-semibold uppercase text-slate-600 dark:bg-slate-700 dark:text-slate-200">
            {(user?.name || 'U').slice(0, 2)}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-medium">{user?.name}</span>
            <span className="block truncate text-xs text-slate-400 dark:text-slate-500">
              {user?.email}
            </span>
          </span>
          <button
            type="button"
            className="btn-ghost p-1.5"
            onClick={() => signOut('Signed out.')}
            aria-label="Sign out"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  )
}
