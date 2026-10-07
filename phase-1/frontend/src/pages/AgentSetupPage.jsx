import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Check, Layers, ShieldCheck, Sparkles } from 'lucide-react'
import AgentProfileForm from '../components/AgentProfileForm'
import { Badge, ErrorState, LoadingScreen } from '../components/ui'
import { useToast } from '../context/ToastContext'
import { useAppShell } from '../layouts/AppLayout'
import { catalogApi, errorMessage, profileApi } from '../services/api'
import { accent, agentIcon, OUTPUT_KIND_LABELS } from '../utils/agents'

/**
 * Two-step personalization for one agent:
 *
 *   1. the **domain** profile — shared by every agent in the domain, asked once
 *   2. the **agent** profile — the narrow specifics of this one job
 *
 * Step 1 is skipped automatically when the domain has already been answered, so
 * the second agent you set up in a domain only ever sees its own questions.
 */
export default function AgentSetupPage() {
  const { agentKey } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const toast = useToast()
  const { reloadCatalog } = useAppShell()

  const requestedStep = searchParams.get('step') // 'domain' | 'agent' | null
  const isEditing = searchParams.get('mode') === 'edit'

  const [detail, setDetail] = useState(null)
  const [step, setStep] = useState('domain')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await catalogApi.agent(agentKey)
      setDetail(data)
      // Land on the step that still needs answers, unless the URL asked for one.
      if (requestedStep === 'domain' || requestedStep === 'agent') setStep(requestedStep)
      else if (data.domain_configured || data.domain_profile_fields.length === 0) setStep('agent')
      else setStep('domain')
    } catch (requestError) {
      if (requestError.response?.status === 404) setError(`There is no “${agentKey}” agent.`)
      else setError(errorMessage(requestError, 'Could not load this agent'))
    } finally {
      setLoading(false)
    }
  }, [agentKey, requestedStep])

  useEffect(() => {
    load()
  }, [load])

  const saveDomain = async (values) => {
    setSubmitting(true)
    try {
      const saved = await profileApi.saveDomain(detail.domain, values)
      setDetail((current) => ({
        ...current,
        domain_profile_data: saved.profile_data,
        domain_configured: saved.is_configured,
        domain_exists: true,
      }))
      await reloadCatalog()
      if (requestedStep === 'domain') {
        toast.success(`${detail.domain_name} profile saved.`)
        navigate(`/domain/${detail.domain}`, { replace: true })
        return
      }
      toast.success(`${detail.domain_name} answers saved. Now the ${detail.name} specifics.`)
      setStep('agent')
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Could not save the domain profile'))
    } finally {
      setSubmitting(false)
    }
  }

  const saveAgent = async (values) => {
    setSubmitting(true)
    try {
      await profileApi.saveAgent(agentKey, values)
      await reloadCatalog()
      toast.success(
        isEditing
          ? `${detail.name} profile updated.`
          : `${detail.name} is personalized. Ask it anything.`,
      )
      navigate(isEditing ? '/profile' : `/agent/${agentKey}`, { replace: true })
    } catch (requestError) {
      toast.error(errorMessage(requestError, 'Could not save the profile'))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingScreen label="Loading setup…" />
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
  if (!detail) return null

  const Icon = agentIcon(detail.icon)
  const tone = accent(detail.domain_accent)
  const DomainIcon = agentIcon(detail.domain_icon)
  const onDomainStep = step === 'domain'
  const hasDomainStep = detail.domain_profile_fields.length > 0

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-2xl px-5 py-8 sm:px-8">
        <button
          type="button"
          className="btn-ghost -ml-2 mb-5 text-sm"
          onClick={() =>
            navigate(isEditing ? '/profile' : `/domain/${detail.domain}`)
          }
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          {isEditing ? 'Back to profiles' : `Back to ${detail.domain_name}`}
        </button>

        {/* Step indicator: makes it obvious the domain answers are shared. */}
        {hasDomainStep && !isEditing && (
          <ol className="mb-5 flex items-center gap-2 text-xs" aria-label="Setup steps">
            <li
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 font-medium ${
                onDomainStep
                  ? 'border-brand-300 bg-brand-50 text-brand-700 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-200'
                  : 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300'
              }`}
            >
              {onDomainStep ? (
                <span aria-hidden="true">1</span>
              ) : (
                <Check className="h-3 w-3" aria-hidden="true" />
              )}
              {detail.domain_name} (shared)
            </li>
            <li className="text-slate-300 dark:text-slate-600" aria-hidden="true">
              →
            </li>
            <li
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 font-medium ${
                onDomainStep
                  ? 'border-slate-200 bg-slate-50 text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400'
                  : 'border-brand-300 bg-brand-50 text-brand-700 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-200'
              }`}
            >
              <span aria-hidden="true">2</span>
              {detail.name}
            </li>
          </ol>
        )}

        <div className="card p-6 sm:p-8">
          <div className="flex items-start gap-4">
            <span
              className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl ${tone.bg} ${tone.text}`}
            >
              {onDomainStep ? (
                <DomainIcon className="h-6 w-6" aria-hidden="true" />
              ) : (
                <Icon className="h-6 w-6" aria-hidden="true" />
              )}
            </span>
            <div className="min-w-0">
              <h1 className="text-xl font-semibold">
                {onDomainStep
                  ? detail.domain_setup_headline || `Tell us about your ${detail.domain_name}`
                  : isEditing
                    ? `Edit your ${detail.name} profile`
                    : detail.setup_headline}
              </h1>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {onDomainStep
                  ? `Answered once for the whole ${detail.domain_name} domain — every agent in it reuses this.`
                  : isEditing
                    ? 'Changes apply to your next message with this agent.'
                    : `Only about ${detail.name.toLowerCase()} work. ${detail.scope}`}
              </p>
              {!onDomainStep && detail.output_kind !== 'text' && (
                <Badge tone="brand" className="mt-2">
                  {OUTPUT_KIND_LABELS[detail.output_kind]}
                </Badge>
              )}
            </div>
          </div>

          <div className="mt-5 flex items-start gap-2 rounded-lg bg-slate-50 p-3 text-xs text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
            {onDomainStep ? (
              <>
                <Layers className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                <p>
                  Shared by all {detail.domain_name} agents. Your{' '}
                  <strong>global profile</strong> (name, tone, response length) sits above this and
                  is edited from Profiles.
                </p>
              </>
            ) : (
              <>
                <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                <p>
                  Stored on the <strong>{detail.name}</strong> profile only. Sibling agents in{' '}
                  {detail.domain_name} never see these answers.
                </p>
              </>
            )}
          </div>

          <div className="mt-6">
            {onDomainStep ? (
              <AgentProfileForm
                key={`domain-${detail.domain}`}
                fields={detail.domain_profile_fields}
                initialData={detail.domain_profile_data || {}}
                onSubmit={saveDomain}
                submitting={submitting}
                submitLabel={
                  requestedStep === 'domain' ? 'Save domain profile' : 'Continue to agent setup'
                }
                onCancel={() => navigate(`/domain/${detail.domain}`)}
                columns={2}
              />
            ) : (
              <AgentProfileForm
                key={`agent-${detail.key}`}
                fields={detail.profile_fields}
                initialData={detail.profile_data || {}}
                onSubmit={saveAgent}
                submitting={submitting}
                submitLabel={isEditing ? 'Save changes' : 'Save and start chatting'}
                onCancel={() =>
                  navigate(isEditing ? '/profile' : `/agent/${agentKey}`)
                }
                columns={2}
              />
            )}
          </div>

          {!onDomainStep && hasDomainStep && !isEditing && (
            <button
              type="button"
              className="btn-ghost mt-3 text-xs"
              onClick={() => setStep('domain')}
            >
              <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
              Back to the shared {detail.domain_name} answers
            </button>
          )}
        </div>

        {!isEditing && (
          <div className="mt-4 flex items-start gap-2 px-1 text-xs text-slate-500 dark:text-slate-400">
            <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            <p>
              You can skip this and{' '}
              <Link to={`/agent/${agentKey}`} className="underline hover:no-underline">
                chat right away
              </Link>{' '}
              — the agent will use your global profile until you fill it in.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
