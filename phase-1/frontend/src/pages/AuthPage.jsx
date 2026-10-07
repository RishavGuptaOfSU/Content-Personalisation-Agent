import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart3,
  BookOpen,
  Briefcase,
  Code2,
  Eye,
  EyeOff,
  GraduationCap,
  Megaphone,
  Moon,
  Sparkles,
  Sun,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'
import { errorMessage } from '../services/api'
import { Spinner, TextInput } from '../components/ui'

const AGENT_PREVIEW = [
  { name: 'Education', Icon: GraduationCap, tone: 'text-emerald-500' },
  { name: 'Technical', Icon: Code2, tone: 'text-sky-500' },
  { name: 'Career', Icon: Briefcase, tone: 'text-amber-500' },
  { name: 'Marketing', Icon: Megaphone, tone: 'text-fuchsia-500' },
  { name: 'Analytics', Icon: BarChart3, tone: 'text-cyan-500' },
  { name: 'Research', Icon: BookOpen, tone: 'text-violet-500' },
  { name: 'Creative', Icon: Sparkles, tone: 'text-rose-500' },
]

export default function AuthPage({ mode = 'login' }) {
  const isSignup = mode === 'signup'
  const { signIn, signUp } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const location = useLocation()
  const { isDark, toggle } = useTheme()

  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const redirectTo = location.state?.from?.pathname || '/dashboard'

  const update = (key) => (event) => {
    setForm((current) => ({ ...current, [key]: event.target.value }))
    setErrors((current) => ({ ...current, [key]: undefined }))
  }

  const validate = () => {
    const next = {}
    if (isSignup && !form.name.trim()) next.name = 'Please enter your name'
    if (!form.email.trim()) next.email = 'Please enter your email'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))
      next.email = 'Enter a valid email address'
    if (!form.password) next.password = 'Please enter your password'
    else if (isSignup) {
      if (form.password.length < 8) next.password = 'At least 8 characters'
      else if (!/[A-Za-z]/.test(form.password)) next.password = 'Include at least one letter'
      else if (!/\d/.test(form.password)) next.password = 'Include at least one number'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      if (isSignup) {
        await signUp({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
        })
        toast.success('Account created. Let’s personalize your agents.')
      } else {
        await signIn({ email: form.email.trim(), password: form.password })
        toast.success('Welcome back.')
      }
      navigate(redirectTo, { replace: true })
    } catch (error) {
      toast.error(errorMessage(error, isSignup ? 'Could not create account' : 'Could not sign in'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid min-h-full lg:grid-cols-2">
      {/* Marketing panel */}
      <div className="relative hidden flex-col justify-between bg-slate-900 p-10 text-white lg:flex">
        <div className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600">
            <Sparkles className="h-5 w-5" aria-hidden="true" />
          </span>
          <span className="font-semibold">Content Personalization Agent</span>
        </div>

        <div className="max-w-md">
          <h1 className="text-3xl font-semibold leading-tight">
            Seven specialists. One profile that actually remembers you.
          </h1>
          <p className="mt-4 text-slate-300">
            A router picks the right agent for every request. Each agent keeps its own profile, and
            a semantic memory layer learns your preferences from the feedback you give.
          </p>
          <ul className="mt-8 grid grid-cols-2 gap-3">
            {AGENT_PREVIEW.map(({ name, Icon, tone }) => (
              <li
                key={name}
                className="flex items-center gap-2.5 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm"
              >
                <Icon className={`h-4 w-4 ${tone}`} aria-hidden="true" />
                {name}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-slate-500">
          Your profiles and memories are private to your account.
        </p>
      </div>

      {/* Form panel */}
      <div className="flex flex-col justify-center px-5 py-10 sm:px-10">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-2 lg:hidden">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
                <Sparkles className="h-4 w-4" aria-hidden="true" />
              </span>
              <span className="text-sm font-semibold">Content Personalization</span>
            </div>
            <button
              type="button"
              onClick={toggle}
              className="btn-ghost ml-auto p-2"
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? (
                <Sun className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Moon className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          </div>

          <h2 className="text-2xl font-semibold">
            {isSignup ? 'Create your account' : 'Sign in'}
          </h2>
          <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
            {isSignup
              ? 'Set up once, then personalize each agent as you go.'
              : 'Welcome back. Your agents are where you left them.'}
          </p>

          <form onSubmit={handleSubmit} className="mt-7 space-y-4" noValidate>
            {isSignup && (
              <TextInput
                label="Name"
                name="name"
                autoComplete="name"
                placeholder="Ada Lovelace"
                value={form.name}
                onChange={update('name')}
                error={errors.name}
              />
            )}
            <TextInput
              label="Email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={update('email')}
              error={errors.email}
            />
            <div>
              <label className="label" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete={isSignup ? 'new-password' : 'current-password'}
                  className={`input pr-10 ${errors.password ? 'border-rose-400' : ''}`}
                  placeholder={isSignup ? 'At least 8 characters' : '••••••••'}
                  value={form.password}
                  onChange={update('password')}
                  aria-invalid={errors.password ? 'true' : undefined}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((visible) => !visible)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" aria-hidden="true" />
                  ) : (
                    <Eye className="h-4 w-4" aria-hidden="true" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p id="password-error" className="mt-1 text-xs text-rose-600 dark:text-rose-400">
                  {errors.password}
                </p>
              )}
              {isSignup && !errors.password && (
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Minimum 8 characters, with at least one letter and one number.
                </p>
              )}
            </div>

            <button type="submit" className="btn-primary w-full" disabled={submitting}>
              {submitting && <Spinner />}
              {isSignup ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            {isSignup ? 'Already have an account? ' : 'New here? '}
            <Link
              to={isSignup ? '/login' : '/signup'}
              className="font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
            >
              {isSignup ? 'Sign in' : 'Create an account'}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
