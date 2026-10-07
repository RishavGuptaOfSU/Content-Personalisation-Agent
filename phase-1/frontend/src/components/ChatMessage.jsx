import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRightLeft,
  Bot,
  Check,
  Copy,
  Cpu,
  Download,
  ExternalLink,
  ImageOff,
  Maximize2,
  MessageSquareQuote,
  Paperclip,
  ThumbsDown,
  ThumbsUp,
  Zap,
} from 'lucide-react'
import Markdown from './Markdown'
import { Badge, Spinner } from './ui'
import { accent, agentIcon, ROUTING_SOURCE_LABELS } from '../utils/agents'
import { mediaUrl } from '../services/api'
import { formatDateTime } from '../utils/format'

/**
 * A generated image or chart. For the visual agents this *is* the answer, so it
 * is rendered large, with its alt text visible and a download link — the caption
 * beside it is only metadata.
 */
function MediaAttachment({ item }) {
  const [failed, setFailed] = useState(false)
  const src = mediaUrl(item.url)
  const kilobytes = item.bytes ? Math.max(1, Math.round(item.bytes / 1024)) : null

  if (failed) {
    return (
      <div className="mt-3 flex items-center gap-2 rounded-xl border border-dashed divider px-4 py-6 text-sm text-slate-500 dark:text-slate-400">
        <ImageOff className="h-4 w-4 shrink-0" aria-hidden="true" />
        <span>
          The generated file could not be loaded. It may have been pruned by the media retention
          limit — ask again to regenerate it.
        </span>
      </div>
    )
  }

  return (
    <figure className="mt-3">
      <a
        href={src}
        target="_blank"
        rel="noreferrer"
        className="group relative block overflow-hidden rounded-xl border divider bg-slate-50 dark:bg-slate-800/50"
        title="Open full size"
      >
        <img
          src={src}
          alt={item.alt_text || 'Generated image'}
          width={item.width || undefined}
          height={item.height || undefined}
          loading="lazy"
          onError={() => setFailed(true)}
          className="block h-auto w-full"
        />
        <span className="absolute right-2 top-2 rounded-md bg-slate-900/70 p-1.5 text-white opacity-0 transition-opacity group-hover:opacity-100">
          <Maximize2 className="h-3.5 w-3.5" aria-hidden="true" />
        </span>
      </a>

      <figcaption className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[0.7rem] text-slate-500 dark:text-slate-400">
        <span>
          {item.width}×{item.height}
          {kilobytes ? ` · ${kilobytes} KB` : ''}
          {item.renderer ? ` · ${item.renderer}` : ''}
        </span>
        <a
          href={src}
          download={item.filename}
          className="inline-flex items-center gap-1 font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          <Download className="h-3 w-3" aria-hidden="true" />
          Download
        </a>
        <a
          href={src}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          <ExternalLink className="h-3 w-3" aria-hidden="true" />
          Open
        </a>
      </figcaption>
      {item.alt_text && (
        <p className="mt-1 text-[0.7rem] italic text-slate-400 dark:text-slate-500">
          Alt text: {item.alt_text}
        </p>
      )}
    </figure>
  )
}

/**
 * Shown when the scope guard decided this agent does not own the request. The
 * button is the whole point: the user can move to the right agent in one click
 * instead of being told "no".
 */
function HandoffNotice({ suggestedKey, suggestedName }) {
  if (!suggestedKey) return null
  return (
    <div className="mt-3 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 dark:border-amber-500/30 dark:bg-amber-500/10">
      <p className="text-xs text-amber-900 dark:text-amber-200">
        This belongs to another agent. Your message is not lost — switch and send it again.
      </p>
      <Link to={`/agent/${suggestedKey}`} className="btn-primary px-2.5 py-1 text-xs">
        <ArrowRightLeft className="h-3.5 w-3.5" aria-hidden="true" />
        Switch to {suggestedName || suggestedKey}
      </Link>
    </div>
  )
}

function UserMessage({ message }) {
  return (
    <div className="flex animate-fade-in justify-end">
      <div className="max-w-[85%] sm:max-w-[75%]">
        <div className="rounded-2xl rounded-br-md bg-brand-600 px-4 py-2.5 text-[0.9375rem] leading-relaxed text-white">
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        <div className="mt-1 flex items-center justify-end gap-2 pr-1 text-[0.7rem] text-slate-400 dark:text-slate-500">
          {message.meta?.attachment_name && (
            <span className="flex items-center gap-1">
              <Paperclip className="h-3 w-3" aria-hidden="true" />
              {message.meta.attachment_name}
            </span>
          )}
          <time dateTime={message.created_at}>{formatDateTime(message.created_at)}</time>
        </div>
      </div>
    </div>
  )
}

function AssistantMessage({ message, agentMeta, agentName, onFeedback, feedbackBusy }) {
  const [copied, setCopied] = useState(false)
  const [commentOpen, setCommentOpen] = useState(false)
  const [comment, setComment] = useState('')
  const [pendingRating, setPendingRating] = useState(null)

  const Icon = agentIcon(agentMeta?.icon)
  const tone = accent(agentMeta?.accent)
  const routing = message.meta?.routing
  const rating = message.feedback_rating
  const provider = message.meta?.provider
  const isLocalProvider = provider === 'local-dev'
  const media = message.media ?? []
  const outOfScope = Boolean(message.meta?.out_of_scope)
  const suggestedKey = message.meta?.suggested_agent
  const incomplete = message.meta?.incomplete_reason

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* ignore */
    }
  }

  const submitRating = (value) => {
    if (value === -1) {
      setPendingRating(-1)
      setCommentOpen(true)
      return
    }
    onFeedback(message, value, null)
  }

  const submitComment = (event) => {
    event.preventDefault()
    onFeedback(message, pendingRating ?? -1, comment.trim() || null)
    setCommentOpen(false)
    setComment('')
    setPendingRating(null)
  }

  return (
    <div className="flex animate-fade-in gap-3">
      <span
        className={`mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg ${tone.bg} ${tone.text}`}
      >
        {agentMeta ? <Icon className="h-4 w-4" aria-hidden="true" /> : <Bot className="h-4 w-4" />}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold">{agentMeta?.name ?? 'Assistant'}</span>
          {outOfScope ? (
            <Badge tone="amber">
              <ArrowRightLeft className="h-3 w-3" aria-hidden="true" />
              Out of scope — handed off
            </Badge>
          ) : (
            routing?.source && (
              <Badge tone={routing.source === 'explicit' ? 'slate' : 'brand'}>
                <Zap className="h-3 w-3" aria-hidden="true" />
                {ROUTING_SOURCE_LABELS[routing.source] ?? routing.source}
                {routing.source !== 'explicit' && routing.confidence
                  ? ` · ${Math.round(routing.confidence * 100)}%`
                  : ''}
              </Badge>
            )
          )}
          {message.output_kind && message.output_kind !== 'text' && (
            <Badge tone="brand">{message.output_kind}</Badge>
          )}
          {isLocalProvider && (
            <Badge tone="amber" className="cursor-help">
              <Cpu className="h-3 w-3" aria-hidden="true" />
              Local dev provider
            </Badge>
          )}
        </div>

        <div className="mt-2 rounded-2xl rounded-tl-md border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
          <Markdown>{message.content}</Markdown>
          {media.map((item) => (
            <MediaAttachment key={item.filename || item.url} item={item} />
          ))}
          {incomplete && media.length === 0 && !outOfScope && (
            <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">
              Nothing was rendered: {incomplete}
            </p>
          )}
        </div>

        {outOfScope && (
          <HandoffNotice suggestedKey={suggestedKey} suggestedName={agentName} />
        )}

        {/* Actions + feedback */}
        <div className="mt-1.5 flex flex-wrap items-center gap-1">
          <button
            type="button"
            onClick={copy}
            className="btn-ghost px-2 py-1 text-xs"
            aria-label="Copy response"
          >
            {copied ? (
              <Check className="h-3.5 w-3.5" aria-hidden="true" />
            ) : (
              <Copy className="h-3.5 w-3.5" aria-hidden="true" />
            )}
            {copied ? 'Copied' : 'Copy'}
          </button>

          <span className="mx-1 h-4 w-px bg-slate-200 dark:bg-slate-700" aria-hidden="true" />

          <button
            type="button"
            onClick={() => submitRating(1)}
            disabled={feedbackBusy}
            aria-pressed={rating === 1}
            className={`btn-ghost px-2 py-1 text-xs ${
              rating === 1 ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300' : ''
            }`}
          >
            <ThumbsUp className="h-3.5 w-3.5" aria-hidden="true" />
            Helpful
          </button>
          <button
            type="button"
            onClick={() => submitRating(-1)}
            disabled={feedbackBusy}
            aria-pressed={rating === -1}
            className={`btn-ghost px-2 py-1 text-xs ${
              rating === -1 ? 'bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300' : ''
            }`}
          >
            <ThumbsDown className="h-3.5 w-3.5" aria-hidden="true" />
            Not helpful
          </button>
          <button
            type="button"
            onClick={() => {
              setPendingRating(rating ?? 1)
              setCommentOpen((open) => !open)
            }}
            className="btn-ghost px-2 py-1 text-xs"
          >
            <MessageSquareQuote className="h-3.5 w-3.5" aria-hidden="true" />
            Tell it what to change
          </button>
          {feedbackBusy && <Spinner className="ml-1 h-3.5 w-3.5" />}
        </div>

        {commentOpen && (
          <form
            onSubmit={submitComment}
            className="mt-2 rounded-lg border divider bg-slate-50 p-3 dark:bg-slate-800/50"
          >
            <label className="label text-xs" htmlFor={`feedback-${message.id}`}>
              What should change next time?
            </label>
            <textarea
              id={`feedback-${message.id}`}
              autoFocus
              rows={2}
              className="input text-sm"
              placeholder="e.g. Make future posts more concise."
              value={comment}
              onChange={(event) => setComment(event.target.value)}
            />
            <div className="mt-2 flex items-center justify-between gap-2">
              <p className="text-[0.7rem] text-slate-500 dark:text-slate-400">
                Saved as a preference. Repeated feedback also updates your profile.
              </p>
              <span className="flex gap-2">
                <button
                  type="button"
                  className="btn-ghost px-2.5 py-1 text-xs"
                  onClick={() => {
                    setCommentOpen(false)
                    setComment('')
                  }}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-3 py-1 text-xs" disabled={feedbackBusy}>
                  Send feedback
                </button>
              </span>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default function ChatMessage({
  message,
  agentMeta,
  suggestedAgentName,
  onFeedback,
  feedbackBusy,
}) {
  if (message.role === 'user') return <UserMessage message={message} />
  return (
    <AssistantMessage
      message={message}
      agentMeta={agentMeta}
      agentName={suggestedAgentName}
      onFeedback={onFeedback}
      feedbackBusy={feedbackBusy}
    />
  )
}

/**
 * The in-flight assistant turn. Shows a skeleton until the first token, then
 * renders the partial markdown as it streams. The elapsed counter matters for
 * local CPU models, where a full answer can legitimately take a minute.
 */
export function StreamingMessage({ agentMeta, text = '', status = '' }) {
  const Icon = agentIcon(agentMeta?.icon)
  const tone = accent(agentMeta?.accent)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const startedAt = Date.now()
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000)
    return () => clearInterval(timer)
  }, [])

  const hasText = text.trim().length > 0

  return (
    <div className="flex animate-fade-in gap-3">
      <span
        className={`mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg ${tone.bg} ${tone.text}`}
      >
        <Icon className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">{agentMeta?.name ?? 'Assistant'}</span>
          <span className="text-[0.7rem] text-slate-400 dark:text-slate-500">
            {/* Visual agents send a status line instead of tokens: an image has
                to be fully rendered before it can be shown. */}
            {status || (hasText ? 'writing…' : 'loading your profile and memories…')}
            {elapsed > 2 && ` ${elapsed}s`}
          </span>
        </div>

        <div
          className="mt-2 rounded-2xl rounded-tl-md border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900"
          aria-live="polite"
          aria-busy="true"
        >
          {hasText ? (
            <>
              <Markdown>{text}</Markdown>
              <span
                className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-slate-400 align-text-bottom dark:bg-slate-500"
                aria-hidden="true"
              />
            </>
          ) : (
            <>
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <span className="flex gap-1" aria-hidden="true">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
                </span>
              </div>
              <div className="mt-3 space-y-2">
                <div className="skeleton h-3 w-full" />
                <div className="skeleton h-3 w-5/6" />
                <div className="skeleton h-3 w-2/3" />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
