import { createContext, useContext, useEffect, useState } from 'react'
import client, {
  REFRESH_TOKEN_KEY,
  refreshAccessToken,
  setAccessToken,
  setOnSessionExpired,
} from '../api/client'

const AuthContext = createContext(null)

function initialStatus() {
  return localStorage.getItem(REFRESH_TOKEN_KEY) ? 'restoring' : 'ready'
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState(initialStatus)

  function startSession({ access, refresh, user }) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    setAccessToken(access)
    setUser(user)
  }

  function endSession() {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    setAccessToken(null)
    setUser(null)
  }

  function logout() {
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
    client.post('/auth/logout/', { refresh }).catch(() => {})
    endSession()
  }

  async function restoreSession() {
    if (!localStorage.getItem(REFRESH_TOKEN_KEY)) {
      return
    }
    setStatus('restoring')
    try {
      await refreshAccessToken()
      const me = await client.get('/auth/me/')
      setUser(me.data)
      setStatus('ready')
    } catch (error) {
      if (error.response?.status === 401) {
        endSession()
        setStatus('ready')
      } else {
        setStatus('failed')
      }
    }
  }

  useEffect(() => {
    setOnSessionExpired(endSession)
    restoreSession()
  }, [])

  if (status === 'restoring') {
    return <p className="p-6 text-center text-gray-500">Loading…</p>
  }

  if (status === 'failed') {
    return (
      <div role="alert" className="p-6 text-center">
        <p className="mb-4">Could not connect. Please try again.</p>
        <button
          type="button"
          onClick={restoreSession}
          className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700"
        >
          Try again
        </button>
      </div>
    )
  }

  return (
    <AuthContext.Provider value={{ user, startSession, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
