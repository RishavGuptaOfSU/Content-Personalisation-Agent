import { Component } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

/**
 * Catches render/lifecycle errors anywhere below it.
 *
 * Without this, a single thrown error unmounts the whole tree and the user sees
 * an empty page with the reason only in the devtools console. Showing the error
 * inline makes the failure diagnosable by whoever is looking at the screen.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null, info: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    this.setState({ info })
    // Keep the console trace for devtools users.
    console.error('Unhandled UI error:', error, info)
  }

  render() {
    const { error, info } = this.state
    if (!error) return this.props.children

    return (
      <div className="flex min-h-full items-start justify-center bg-slate-50 p-6 dark:bg-slate-950">
        <div className="card mt-10 w-full max-w-2xl p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-rose-50 text-rose-600 dark:bg-rose-500/15 dark:text-rose-400">
              <AlertTriangle className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <h1 className="text-lg font-semibold">Something in the interface crashed</h1>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Your data is safe — this is a rendering error in the browser only.
              </p>
            </div>
          </div>

          <div className="mt-5 rounded-lg border border-rose-200 bg-rose-50 p-3 dark:border-rose-500/30 dark:bg-rose-500/10">
            <p className="font-mono text-sm text-rose-800 dark:text-rose-200">
              {error.name}: {error.message}
            </p>
          </div>

          {(error.stack || info?.componentStack) && (
            <details className="mt-3">
              <summary className="cursor-pointer text-sm font-medium text-slate-600 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200">
                Technical details
              </summary>
              <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-100 p-3 font-mono text-[0.7rem] leading-relaxed text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                {error.stack}
                {info?.componentStack ? `\n\nComponent stack:${info.componentStack}` : ''}
              </pre>
            </details>
          )}

          <div className="mt-6 flex flex-wrap gap-2">
            <button type="button" className="btn-primary" onClick={() => window.location.reload()}>
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              Reload the page
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => this.setState({ error: null, info: null })}
            >
              Try to continue
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => {
                try {
                  localStorage.removeItem('cpa.token')
                } catch {
                  /* ignore */
                }
                window.location.replace('/login')
              }}
            >
              Clear session and sign in
            </button>
          </div>
        </div>
      </div>
    )
  }
}
