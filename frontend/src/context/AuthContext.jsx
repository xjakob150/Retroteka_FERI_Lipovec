import { createContext, useContext, useState } from 'react'

const REFRESH_TOKEN_KEY = 'refreshToken'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [accessToken, setAccessToken] = useState(null)

  function startSession({ access, refresh, user }) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    setAccessToken(access)
    setUser(user)
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, startSession }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
