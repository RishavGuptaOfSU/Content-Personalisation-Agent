import { createContext, useContext, useState } from 'react'
import { Outlet, useSearchParams } from 'react-router-dom'
import { Menu, Moon, Sun } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import { ConfirmDialog } from '../components/Modal'
import { useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'
import { useAppData } from '../hooks/useAppData'
import { errorMessage } from '../services/api'

const AppDataContext = createContext(null)

export function useAppShell() {
  const context = useContext(AppDataContext)
  if (!context) throw new Error('useAppShell must be used inside AppLayout')
  return context
}

export default function AppLayout() {
  const data = useAppData()
  const { isDark, toggle } = useTheme()
  const toast = useToast()
  const [searchParams] = useSearchParams()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)

  const activeConversationId = searchParams.get('conversation')

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await data.deleteConversation(pendingDelete.id)
      toast.success('Conversation deleted')
      setPendingDelete(null)
    } catch (error) {
      toast.error(errorMessage(error, 'Delete failed'))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <AppDataContext.Provider value={data}>
      <div className="flex h-full overflow-hidden">
        {/* Desktop sidebar */}
        <aside className="hidden w-72 shrink-0 border-r divider lg:block">
          <Sidebar
            domains={data.domains}
            agentsByDomain={data.agentsByDomain}
            agentsByKey={data.agentsByKey}
            conversations={data.conversations}
            loadingConversations={data.loadingConversations}
            activeConversationId={activeConversationId}
            onRenameConversation={data.renameConversation}
            onDeleteConversation={setPendingDelete}
          />
        </aside>

        {/* Mobile drawer */}
        {mobileOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div
              className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
              onClick={() => setMobileOpen(false)}
              aria-hidden="true"
            />
            <aside className="absolute left-0 top-0 h-full w-72 animate-slide-in-right border-r divider shadow-xl">
              <Sidebar
                domains={data.domains}
                agentsByDomain={data.agentsByDomain}
                agentsByKey={data.agentsByKey}
                conversations={data.conversations}
                loadingConversations={data.loadingConversations}
                activeConversationId={activeConversationId}
                onRenameConversation={data.renameConversation}
                onDeleteConversation={(conversation) => {
                  setMobileOpen(false)
                  setPendingDelete(conversation)
                }}
                onClose={() => setMobileOpen(false)}
              />
            </aside>
          </div>
        )}

        <div className="flex min-w-0 flex-1 flex-col">
          {/* Mobile top bar */}
          <header className="flex items-center justify-between gap-2 border-b divider bg-white px-3 py-2 lg:hidden dark:bg-slate-900">
            <button
              type="button"
              className="btn-ghost p-2"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" aria-hidden="true" />
            </button>
            <span className="text-sm font-semibold">Content Personalization</span>
            <button
              type="button"
              className="btn-ghost p-2"
              onClick={toggle}
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? (
                <Sun className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Moon className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          </header>

          <main className="min-h-0 flex-1 overflow-hidden">
            <Outlet />
          </main>
        </div>
      </div>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        onClose={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
        title="Delete conversation?"
        description={`"${pendingDelete?.title ?? ''}" and all of its messages will be permanently deleted. Long-term memories learned from it are kept.`}
        confirmLabel="Delete"
        busy={deleting}
      />
    </AppDataContext.Provider>
  )
}
