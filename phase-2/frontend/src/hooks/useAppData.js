import { useCallback, useEffect, useMemo, useState } from 'react'
import { catalogApi, conversationsApi, errorMessage, profileApi } from '../services/api'
import { useToast } from '../context/ToastContext'

/**
 * Shared app-shell data for the single-domain build: the five marketing agents
 * with this user's per-agent status, the brand profile they all share, and the
 * conversation list in the sidebar. Lives in the layout so the sidebar and
 * pages stay in sync after a chat, a setup, a rename or a delete.
 */
export function useAppData() {
  const toast = useToast()
  const [agents, setAgents] = useState([])
  const [brand, setBrand] = useState(null)
  const [brandProfile, setBrandProfile] = useState(null)
  const [conversations, setConversations] = useState([])
  const [loadingCatalog, setLoadingCatalog] = useState(true)
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [catalogError, setCatalogError] = useState(null)

  const loadCatalog = useCallback(async () => {
    setCatalogError(null)
    try {
      const [agentList, brandCard, savedBrand] = await Promise.all([
        catalogApi.agents(),
        catalogApi.brand(),
        profileApi.getBrand(),
      ])
      setAgents(agentList)
      setBrand(brandCard)
      setBrandProfile(savedBrand)
    } catch (error) {
      setCatalogError(errorMessage(error, 'Could not load the agents'))
    } finally {
      setLoadingCatalog(false)
    }
  }, [])

  const loadConversations = useCallback(async () => {
    try {
      setConversations(await conversationsApi.list({ limit: 60 }))
    } catch (error) {
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

  const visualAgents = useMemo(
    () => agents.filter((agent) => agent.output_kind !== 'text'),
    [agents],
  )

  const brandConfigured = Boolean(brandProfile?.is_configured)

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
    agents,
    agentsByKey,
    visualAgents,
    brand,
    brandProfile,
    brandConfigured,
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
