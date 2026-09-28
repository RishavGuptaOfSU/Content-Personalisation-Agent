import { useCallback, useEffect, useMemo, useState } from 'react'
import { catalogApi, conversationsApi, errorMessage } from '../services/api'
import { useToast } from '../context/ToastContext'

/**
 * Shared app-shell data: the two-level catalog (domains, and every agent with
 * this user's per-agent status) plus the conversation list in the sidebar.
 * Lives in the layout so the sidebar and pages stay in sync after a chat,
 * a setup, a rename or a delete.
 */
export function useAppData() {
  const toast = useToast()
  const [domains, setDomains] = useState([])
  const [agents, setAgents] = useState([])
  const [conversations, setConversations] = useState([])
  const [loadingCatalog, setLoadingCatalog] = useState(true)
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [catalogError, setCatalogError] = useState(null)

  const loadCatalog = useCallback(async () => {
    setCatalogError(null)
    try {
      const [domainList, agentList] = await Promise.all([
        catalogApi.domains(),
        catalogApi.agents(),
      ])
      setDomains(domainList)
      setAgents(agentList)
    } catch (error) {
      setCatalogError(errorMessage(error, 'Could not load the agent catalog'))
    } finally {
      setLoadingCatalog(false)
    }
  }, [])

  const loadConversations = useCallback(async () => {
    try {
      setConversations(await conversationsApi.list({ limit: 60 }))
    } catch (error) {
      // Non-fatal for the shell: surfaced quietly.
      console.warn('conversation load failed:', errorMessage(error))
    } finally {
      setLoadingConversations(false)
    }
  }, [])

  useEffect(() => {
    loadCatalog()
    loadConversations()
  }, [loadCatalog, loadConversations])

  /** agent key -> agent summary, for O(1) lookups in message lists. */
  const agentsByKey = useMemo(
    () => Object.fromEntries(agents.map((agent) => [agent.key, agent])),
    [agents],
  )

  /** domain key -> its agents, in catalog order. */
  const agentsByDomain = useMemo(() => {
    const grouped = {}
    for (const agent of agents) {
      grouped[agent.domain] = grouped[agent.domain] || []
      grouped[agent.domain].push(agent)
    }
    return grouped
  }, [agents])

  const domainsByKey = useMemo(
    () => Object.fromEntries(domains.map((domain) => [domain.key, domain])),
    [domains],
  )

  const renameConversation = useCallback(
    async (conversation, title) => {
      try {
        const updated = await conversationsApi.update(conversation.id, { title })
        setConversations((current) =>
          current.map((item) => (item.id === updated.id ? { ...item, ...updated } : item)),
        )
        toast.success('Conversation renamed')
      } catch (error) {
        toast.error(errorMessage(error, 'Rename failed'))
      }
    },
    [toast],
  )

  const deleteConversation = useCallback(
    async (conversationId) => {
      await conversationsApi.remove(conversationId)
      setConversations((current) => current.filter((item) => item.id !== conversationId))
      loadCatalog()
    },
    [loadCatalog],
  )

  return {
    domains,
    domainsByKey,
    agents,
    agentsByKey,
    agentsByDomain,
    conversations,
    loadingCatalog,
    loadingConversations,
    catalogError,
    reloadCatalog: loadCatalog,
    reloadConversations: loadConversations,
    setConversations,
    renameConversation,
    deleteConversation,
  }
}
