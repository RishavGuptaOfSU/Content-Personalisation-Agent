import { Link } from 'react-router-dom'
import { Compass } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <div className="grid h-full place-items-center px-6 py-16">
      <div className="text-center">
        <span className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500">
          <Compass className="h-6 w-6" aria-hidden="true" />
        </span>
        <h1 className="mt-4 text-xl font-semibold">Page not found</h1>
        <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
          That route does not exist in this app.
        </p>
        <Link to="/dashboard" className="btn-primary mt-5">
          Back to dashboard
        </Link>
      </div>
    </div>
  )
}
