import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authApi, errorMessage, setUnauthorizedHandler, tokenStore } from '../services/api'
import { useToast } from './ToastContext'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const toast = useToast()
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)

  const signOut = useCallback(
    (message) => {
      tokenStore.clear()
      setUser(null)
      if (message) toast.info(message)
    },
    [toast],
  )

  // Any 401 from the API (expired token) ends the session cleanly.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      if (tokenStore.get()) signOut('Your session expired. Please sign in again.')
    })
    return () => setUnauthorizedHandler(null)
  }, [signOut])

  // Restore the session on a hard refresh.
  useEffect(() => {
    let cancelled = false
    async function restore() {
      if (!tokenStore.get()) {
        setInitializing(false)
        return
      }
      try {
        const profile = await authApi.me()
        if (!cancelled) setUser(profile)
      } catch {
        tokenStore.clear()
      } finally {
        if (!cancelled) setInitializing(false)
      }
    }
    restore()
    return () => {
      cancelled = true
    }
  }, [])

  const signIn = useCallback(async (credentials) => {
    const data = await authApi.login(credentials)
    tokenStore.set(data.access_token)
    setUser(data.user)
    return data.user
  }, [])

  const signUp = useCallback(async (payload) => {
    const data = await authApi.register(payload)
    tokenStore.set(data.access_token)
    setUser(data.user)
    return data.user
  }, [])

  const refresh = useCallback(async () => {
    try {
      const profile = await authApi.me()
      setUser(profile)
      return profile
    } catch (error) {
      toast.error(errorMessage(error))
      return null
    }
  }, [toast])

  const value = useMemo(
    () => ({
      user,
      initializing,
      isAuthenticated: Boolean(user),
      signIn,
      signUp,
      signOut,
      refresh,
    }),
    [user, initializing, signIn, signUp, signOut, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside an AuthProvider')
  return context
}
