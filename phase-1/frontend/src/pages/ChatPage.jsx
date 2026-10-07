import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  ArrowDown,
  ArrowLeft,
  Ban,
  Info,
  Loader2,
  Moon,
  Paperclip,
  PanelRightClose,
  PanelRightOpen,
  Plus,
  SendHorizontal,
  Settings2,
  Square,
  Sun,
  X,
} from 'lucide-react'
import ChatMessage, { StreamingMessage } from '../components/ChatMessage'
import PersonalizationPanel from '../components/PersonalizationPanel'
import { Badge, EmptyState, ErrorState, LoadingScreen } from '../components/ui'
import { useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'
import { useAppShell } from '../layouts/AppLayout'
import {
  catalogApi,
  chatApi,
  conversationsApi,
  errorMessage,
  feedbackApi,
  memoryApi,
  profileApi,
} from '../services/api'
import { accent, agentIcon, OUTPUT_KIND_ICONS, OUTPUT_KIND_LABELS } from '../utils/agents'

const MAX_ATTACHMENT_HINT = '.txt, .md, .csv, .json, .py, .sql, .log (max 1 MB)'

export default function ChatPage() {
  const { agentKey } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const toast = useToast()
  const { isDark, toggle } = useTheme()
  const { agentsByKey, reloadCatalog, reloadConversations } = useAppShell()

  const conversationId = searchParams.get('conversation')

  const [detail, setDetail] = useState(null)
  const [globalProfile, setGlobalProfile] = useState(null)
  const [status, setStatus] = useState(null) // profile status for this agent
  const [messages, setMessages] = useState([])
  const [memoriesUsed, setMemoriesUsed] = useState([])
  const [memoryTotal, setMemoryTotal] = useState(0)
  const [lastTrace, setLastTrace] = useState(null)
  const [lastRouting, setLastRouting] = useState(null)
  const [lastScope, setLastScope] = useState(null)

  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [sending, setSending] = useState(false)
  const [feedbackBusy, setFeedbackBusy] = useState(false)
  const [panelOpen, setPanelOpen] = useState(
    () => typeof window !== 'undefined' && window.innerWidth >= 1280,
  )
  const [showScrollButton, setShowScrollButton] = useState(false)

  const [input, setInput] = useState('')
  const [attachment, setAttachment] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  //: Progress line for visual agents, which cannot stream tokens.
  const [streamStatus, setStreamStatus] = useState('')

  const abortRef = useRef(null)
  const scrollRef = useRef(null)
  const bottomRef = useRef(null)
  const fileRef = useRef(null)
  const textareaRef = useRef(null)

  const agentMeta = useMemo(() => agentsByKey[agentKey] ?? detail, [agentsByKey, agentKey, detail])
  const Icon = agentIcon(agentMeta?.icon)
  const tone = accent(detail?.domain_accent ?? agentMeta?.accent)
  const outputKind = detail?.output_kind ?? agentMeta?.output_kind ?? 'text'
  const isVisual = outputKind !== 'text'
  const KindIcon = OUTPUT_KIND_ICONS[outputKind]

  // ---------------------------------------------------------------- loading
  const loadAgentContext = useCallback(async () => {
    setLoading(true)
    setLoadError(null)
    try {
      const [agentDetail, profileStatus, global, memorySummary] = await Promise.all([
        catalogApi.agent(agentKey),
        profileApi.getAgent(agentKey),
        profileApi.getGlobal(),
        memoryApi.summary({ agent_key: agentKey }),
      ])
      setDetail(agentDetail)
      setStatus(profileStatus)
      setGlobalProfile(global)
      setMemoryTotal(memorySummary.total)

      // First run for this agent: go straight to the two-step setup.
      if (profileStatus.needs_setup && !profileStatus.agent_exists && !conversationId) {
        navigate(`/agent/${agentKey}/setup`, { replace: true })
        return
      }
      if (!conversationId) {
        setMemoriesUsed(
          (memorySummary.recent || []).slice(0, 5).map((memory) => ({
            ...memory,
            scope: memory.agent_key || memory.domain || 'global',
            similarity: null,
            pinned: false,
          })),
        )
      }
    } catch (error) {
      if (error.response?.status === 404) setLoadError(`There is no “${agentKey}” agent.`)
      else setLoadError(errorMessage(error, 'Could not load this agent'))
    } finally {
      setLoading(false)
    }
  }, [agentKey, conversationId, navigate])

  const loadConversation = useCallback(async () => {
    if (!conversationId) {
      setMessages([])
      setLastTrace(null)
      setLastRouting(null)
      setLastScope(null)
      return
    }
    try {
      const conversation = await conversationsApi.get(conversationId)
      setMessages(conversation.messages || [])
      const lastAssistant = [...(conversation.messages || [])]
        .reverse()
        .find((message) => message.role === 'assistant')
      if (lastAssistant?.meta?.routing) setLastRouting(lastAssistant.meta.routing)
    } catch (error) {
      if (error.response?.status === 404) {
        toast.error('That conversation no longer exists.')
        setSearchParams({}, { replace: true })
      } else {
        toast.error(errorMessage(error, 'Could not load the conversation'))
      }
    }
  }, [conversationId, setSearchParams, toast])

  useEffect(() => {
    loadAgentContext()
  }, [loadAgentContext])

  useEffect(() => {
    loadConversation()
  }, [loadConversation])

  // ------------------------------------------------------------- scrolling
  const scrollToBottom = useCallback((behavior = 'smooth') => {
    bottomRef.current?.scrollIntoView({ behavior, block: 'end' })
  }, [])

  useEffect(() => {
    scrollToBottom(messages.length > 2 ? 'smooth' : 'auto')
  }, [messages, sending, scrollToBottom])

  useEffect(() => {
    if (streamingText && !showScrollButton) scrollToBottom('auto')
  }, [streamingText, showScrollButton, scrollToBottom])

  const onScroll = () => {
    const element = scrollRef.current
    if (!element) return
    const distance = element.scrollHeight - element.scrollTop - element.clientHeight
    setShowScrollButton(distance > 240)
  }

  // ------------------------------------------------------------------ send
  const applyFinalTurn = useCallback(
    (response, optimisticId) => {
      setMessages((current) => [
        ...current.filter((message) => message.id !== optimisticId),
        response.user_message,
        response.assistant_message,
      ])
      setStreamingText('')
      setStreamStatus('')
      setLastTrace(response.personalization)
      setLastRouting(response.routing)
      setLastScope(response.scope)
      setMemoriesUsed(response.personalization.memories_used || [])
      setAttachment(null)

      if (!conversationId) {
        setSearchParams({ conversation: response.conversation_id }, { replace: true })
      }
      if (response.new_memories?.length) {
        toast.success(`Learned: ${response.new_memories[0]}`, { title: 'New memory' })
        setMemoryTotal((total) => total + response.new_memories.length)
      }
      if (response.scope && response.scope.in_scope === false) {
        toast.info(response.scope.reason, { title: 'Handed off' })
      }
      reloadConversations()
      reloadCatalog()
    },
    [conversationId, reloadCatalog, reloadConversations, setSearchParams, toast],
  )

  const handleSend = async (event) => {
    event?.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    const optimisticUser = {
      id: `pending-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      meta: attachment ? { attachment_name: attachment.name } : {},
      pending: true,
    }
    setMessages((current) => [...current, optimisticUser])
    setInput('')
    setSending(true)
    setStreamingText('')
    setStreamStatus(isVisual ? `Designing the ${outputKind}…` : '')

    const payload = {
      message: text,
      agent_key: agentKey,
      conversation_id: conversationId || undefined,
      attachment_name: attachment?.name,
      attachment_text: attachment?.text,
    }

    const controller = new AbortController()
    abortRef.current = controller

    try {
      let finished = false
      await chatApi.stream(payload, {
        signal: controller.signal,
        // Routing + personalization arrive before generation starts, so the
        // right panel is populated while the model is still working.
        onMeta: (meta) => {
          setLastRouting(meta.routing)
          setLastScope(meta.scope)
          setLastTrace(meta.personalization)
          setMemoriesUsed(meta.personalization.memories_used || [])
        },
        onStatus: (message) => setStreamStatus(message),
        onDelta: (chunk) => setStreamingText((current) => current + chunk),
        onDone: (response) => {
          finished = true
          applyFinalTurn(response, optimisticUser.id)
        },
      })
      if (!finished) throw new Error('The response ended before it was saved.')
    } catch (error) {
      if (controller.signal.aborted) {
        setMessages((current) => current.filter((message) => message.id !== optimisticUser.id))
        setStreamingText('')
        setStreamStatus('')
        toast.info('Generation stopped.')
      } else {
        // Fall back to the non-streaming endpoint (e.g. a proxy buffering SSE).
        try {
          const response = await chatApi.send(payload)
          applyFinalTurn(response, optimisticUser.id)
        } catch (fallbackError) {
          setMessages((current) =>
            current.filter((message) => message.id !== optimisticUser.id),
          )
          setStreamingText('')
          setStreamStatus('')
          setInput(text)
          toast.error(
            errorMessage(fallbackError, error.message || 'The agent could not respond'),
          )
        }
      }
    } finally {
      abortRef.current = null
      setSending(false)
      textareaRef.current?.focus()
    }
  }

  const stopGeneration = () => abortRef.current?.abort()

  // -------------------------------------------------------------- feedback
  const handleFeedback = async (message, rating, feedbackText) => {
    setFeedbackBusy(true)
    try {
      const result = await feedbackApi.submit({
        message_id: message.id,
        rating,
        feedback_text: feedbackText,
      })
      setMessages((current) =>
        current.map((item) =>
          item.id === message.id ? { ...item, feedback_rating: rating } : item,
        ),
      )
      toast.success(result.message || 'Thanks for the feedback.')

      if (result.memories_created?.length) {
        setMemoryTotal((total) => total + result.memories_created.length)
      }
      if (result.profile_updated) {
        const [global, profileStatus] = await Promise.all([
          profileApi.getGlobal(),
          profileApi.getAgent(agentKey),
        ])
        setGlobalProfile(global)
        setStatus(profileStatus)
        toast.info(
          `Profile updated: ${Object.entries(result.profile_changes)
            .map(([key, value]) => `${key} → ${value}`)
            .join(', ')}`,
          { title: 'Learned from repeated feedback' },
        )
      }
    } catch (error) {
      toast.error(errorMessage(error, 'Could not save feedback'))
    } finally {
      setFeedbackBusy(false)
    }
  }

  // ------------------------------------------------------------ attachment
  const handleFile = async (event) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    setUploading(true)
    try {
      const uploaded = await chatApi.upload(file)
      setAttachment(uploaded)
      toast.success(
        `${uploaded.name} attached (${uploaded.characters.toLocaleString()} characters read)`,
      )
    } catch (error) {
      toast.error(errorMessage(error, 'Could not read that file'))
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteMemory = async (memory) => {
    try {
      await memoryApi.remove(memory.id)
      setMemoriesUsed((current) => current.filter((item) => item.id !== memory.id))
      setMemoryTotal((total) => Math.max(0, total - 1))
      toast.success('Memory forgotten')
    } catch (error) {
      toast.error(errorMessage(error, 'Could not delete the memory'))
    }
  }

  const startNewConversation = () => {
    setSearchParams({}, { replace: false })
    setMessages([])
    setLastTrace(null)
    setLastRouting(null)
    setLastScope(null)
    setInput('')
    setAttachment(null)
    textareaRef.current?.focus()
  }

  if (loading) return <LoadingScreen label="Loading agent…" />
  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl px-5 py-10">
        <ErrorState message={loadError} onRetry={loadAgentContext} />
        <button type="button" className="btn-secondary mt-4" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to domains
        </button>
      </div>
    )
  }

  const suggestions = detail?.examples ?? []
  const needsSetup = status?.needs_setup

  return (
    <div className="flex h-full min-w-0">
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Agent header */}
        <header className="flex items-center gap-3 border-b divider bg-white px-4 py-3 dark:bg-slate-900">
          <Link
            to={`/domain/${detail?.domain ?? ''}`}
            className="btn-ghost -ml-1.5 hidden p-2 sm:inline-flex"
            title={`Back to ${detail?.domain_name ?? 'domain'}`}
            aria-label={`Back to ${detail?.domain_name ?? 'domain'}`}
          >
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          </Link>
          <span
            className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${tone.bg} ${tone.text}`}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-sm font-semibold">{agentMeta?.name}</h1>
              <span className="text-[0.7rem] text-slate-400 dark:text-slate-500">
                {detail?.domain_name}
              </span>
              <Badge tone={needsSetup ? 'amber' : 'green'}>
                {needsSetup ? 'Not configured' : 'Personalized'}
              </Badge>
              {isVisual && (
                <Badge tone="brand">
                  {KindIcon && <KindIcon className="h-3 w-3" aria-hidden="true" />}
                  {OUTPUT_KIND_LABELS[outputKind]}
                </Badge>
              )}
            </div>
            <p className="truncate text-xs text-slate-500 dark:text-slate-400">
              {detail?.scope ?? agentMeta?.description}
            </p>
          </div>

          <button
            type="button"
            className="btn-ghost p-2"
            onClick={startNewConversation}
            title="New chat"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            <span className="sr-only">New chat</span>
          </button>
          <button
            type="button"
            className="btn-ghost hidden p-2 lg:inline-flex"
            onClick={toggle}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? (
              <Sun className="h-4 w-4" aria-hidden="true" />
            ) : (
              <Moon className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
          <button
            type="button"
            className="btn-ghost p-2"
            onClick={() => setPanelOpen((open) => !open)}
            aria-label={panelOpen ? 'Hide personalization panel' : 'Show personalization panel'}
            aria-expanded={panelOpen}
          >
            {panelOpen ? (
              <PanelRightClose className="h-4 w-4" aria-hidden="true" />
            ) : (
              <PanelRightOpen className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
        </header>

        {needsSetup && (
          <div className="flex flex-wrap items-center justify-between gap-2 border-b divider bg-amber-50 px-4 py-2 text-xs text-amber-900 dark:bg-amber-500/10 dark:text-amber-200">
            <span className="flex items-center gap-1.5">
              <Info className="h-3.5 w-3.5" aria-hidden="true" />
              {status?.domain_configured
                ? `Only the ${agentMeta?.name} specifics are missing.`
                : `The shared ${detail?.domain_name} answers are missing.`}{' '}
              Answers improve a lot once this is filled in.
            </span>
            <Link to={`/agent/${agentKey}/setup`} className="btn-secondary px-2.5 py-1 text-xs">
              <Settings2 className="h-3.5 w-3.5" aria-hidden="true" />
              Run setup
            </Link>
          </div>
        )}

        {/* Messages */}
        <div
          ref={scrollRef}
          onScroll={onScroll}
          className="relative min-h-0 flex-1 overflow-y-auto"
        >
          <div className="mx-auto max-w-3xl space-y-5 px-4 py-6">
            {messages.length === 0 && !sending ? (
              <div className="pt-6">
                <EmptyState
                  icon={Icon}
                  title={`${agentMeta?.name}`}
                  description={
                    isVisual
                      ? `This agent returns ${
                          outputKind === 'chart' ? 'a rendered chart' : 'an image file'
                        }, not text. ${detail?.scope ?? ''}`
                      : detail?.scope
                  }
                />

                {detail?.out_of_scope?.length > 0 && (
                  <div className="mx-auto mt-4 max-w-md rounded-lg border border-dashed divider px-4 py-3">
                    <p className="flex items-center gap-1.5 text-[0.7rem] font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                      <Ban className="h-3 w-3" aria-hidden="true" />
                      Not this agent&apos;s job
                    </p>
                    <ul className="mt-1.5 space-y-0.5">
                      {detail.out_of_scope.slice(0, 3).map((item) => (
                        <li key={item} className="text-xs text-slate-500 dark:text-slate-400">
                          · {item}
                        </li>
                      ))}
                    </ul>
                    <p className="mt-1.5 text-[0.7rem] text-slate-400 dark:text-slate-500">
                      Ask for one of those and it will point you at the right agent.
                    </p>
                  </div>
                )}

                {suggestions.length > 0 && (
                  <div className="mt-5">
                    <p className="mb-2 text-center text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">
                      Try one of these
                    </p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          type="button"
                          className="chip-idle"
                          onClick={() => {
                            setInput(suggestion)
                            textareaRef.current?.focus()
                          }}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  agentMeta={
                    message.agent_key ? (agentsByKey[message.agent_key] ?? agentMeta) : agentMeta
                  }
                  suggestedAgentName={
                    message.meta?.suggested_agent
                      ? (agentsByKey[message.meta.suggested_agent]?.name ??
                        message.meta.suggested_agent)
                      : null
                  }
                  onFeedback={handleFeedback}
                  feedbackBusy={feedbackBusy}
                />
              ))
            )}
            {sending && (
              <StreamingMessage
                agentMeta={agentMeta}
                text={streamingText}
                status={streamStatus}
              />
            )}
            <div ref={bottomRef} />
          </div>

          {showScrollButton && (
            <button
              type="button"
              onClick={() => scrollToBottom()}
              className="btn-secondary sticky bottom-4 left-1/2 -translate-x-1/2 shadow-md"
              aria-label="Scroll to latest message"
            >
              <ArrowDown className="h-4 w-4" aria-hidden="true" />
              Latest
            </button>
          )}
        </div>

        {/* Composer */}
        <div className="border-t divider bg-white px-4 py-3 dark:bg-slate-900">
          <div className="mx-auto max-w-3xl">
            {attachment && (
              <div className="mb-2 flex items-center gap-2 rounded-lg border divider bg-slate-50 px-3 py-2 text-xs dark:bg-slate-800/60">
                <Paperclip className="h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />
                <span className="min-w-0 flex-1 truncate">
                  <strong className="font-medium">{attachment.name}</strong>{' '}
                  <span className="text-slate-500 dark:text-slate-400">
                    · {attachment.characters.toLocaleString()} characters
                    {attachment.truncated ? ' (truncated)' : ''}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => setAttachment(null)}
                  className="rounded p-1 text-slate-400 hover:text-rose-600"
                  aria-label="Remove attachment"
                >
                  <X className="h-3.5 w-3.5" aria-hidden="true" />
                </button>
              </div>
            )}

            <form onSubmit={handleSend} className="flex items-end gap-2">
              <input
                ref={fileRef}
                type="file"
                className="hidden"
                accept=".txt,.md,.csv,.json,.tsv,.log,.py,.sql,.yaml,.yml"
                onChange={handleFile}
              />
              <button
                type="button"
                className="btn-secondary mb-0.5 shrink-0 p-2.5"
                onClick={() => fileRef.current?.click()}
                disabled={uploading || sending}
                title={`Attach a text file — ${MAX_ATTACHMENT_HINT}`}
                aria-label="Attach a file"
              >
                {uploading ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Paperclip className="h-4 w-4" aria-hidden="true" />
                )}
              </button>

              <label className="sr-only" htmlFor="chat-input">
                Message the {agentMeta?.name}
              </label>
              <textarea
                id="chat-input"
                ref={textareaRef}
                rows={1}
                value={input}
                onChange={(event) => {
                  setInput(event.target.value)
                  const element = event.target
                  element.style.height = 'auto'
                  element.style.height = `${Math.min(element.scrollHeight, 200)}px`
                }}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault()
                    handleSend()
                  }
                }}
                placeholder={
                  outputKind === 'chart'
                    ? 'Paste the data to plot, e.g. Jan 120, Feb 150, Mar 180…'
                    : outputKind === 'image'
                      ? 'Describe the graphic you need…'
                      : `Ask the ${agentMeta?.name ?? 'agent'}…  (Shift+Enter for a new line)`
                }
                className="input max-h-[200px] min-h-[42px] resize-none py-2.5"
                disabled={sending}
              />

              {sending ? (
                <button
                  type="button"
                  onClick={stopGeneration}
                  className="btn-secondary mb-0.5 shrink-0 p-2.5"
                  aria-label="Stop generating"
                  title="Stop generating"
                >
                  <Square className="h-4 w-4" aria-hidden="true" />
                </button>
              ) : (
                <button
                  type="submit"
                  className="btn-primary mb-0.5 shrink-0 p-2.5"
                  disabled={!input.trim()}
                  aria-label="Send message"
                >
                  <SendHorizontal className="h-4 w-4" aria-hidden="true" />
                </button>
              )}
            </form>

            <p className="mt-1.5 text-center text-[0.7rem] text-slate-400 dark:text-slate-500">
              Uses your global profile, the {detail?.domain_name} domain profile, this agent&apos;s
              own profile and{' '}
              {memoryTotal > 0
                ? `${memoryTotal} learned ${memoryTotal === 1 ? 'memory' : 'memories'}`
                : 'no memories yet'}
              .
            </p>
          </div>
        </div>
      </div>

      {panelOpen && (
        <aside className="hidden w-80 shrink-0 border-l divider xl:block">
          <PersonalizationPanel
            agent={detail}
            globalProfile={globalProfile}
            status={status}
            memories={memoriesUsed}
            memoryTotal={memoryTotal}
            lastTrace={lastTrace}
            lastRouting={lastRouting}
            lastScope={lastScope}
            onDeleteMemory={handleDeleteMemory}
          />
        </aside>
      )}

      {/* Mobile/tablet drawer for the panel */}
      {panelOpen && (
        <div
          className="fixed inset-0 z-40 xl:hidden"
          role="dialog"
          aria-label="Personalization panel"
        >
          <div
            className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            onClick={() => setPanelOpen(false)}
            aria-hidden="true"
          />
          <aside className="absolute right-0 top-0 h-full w-80 max-w-[85vw] animate-slide-in-right border-l divider shadow-xl">
            <PersonalizationPanel
              agent={detail}
              globalProfile={globalProfile}
              status={status}
              memories={memoriesUsed}
              memoryTotal={memoryTotal}
              lastTrace={lastTrace}
              lastRouting={lastRouting}
              lastScope={lastScope}
              onDeleteMemory={handleDeleteMemory}
              onClose={() => setPanelOpen(false)}
            />
          </aside>
        </div>
      )}
    </div>
  )
}
