import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, type User } from '@/lib/api'

type AuthValue = { user: User | null; loading: boolean; login: (email: string, password: string) => Promise<User>; logout: () => Promise<void> }
const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(Boolean(localStorage.getItem('campo_token')))
  useEffect(() => {
    if (!localStorage.getItem('campo_token')) return
    api.me().then(setUser).catch(() => localStorage.removeItem('campo_token')).finally(() => setLoading(false))
  }, [])
  const value = useMemo<AuthValue>(() => ({
    user, loading,
    login: async (email, password) => { const session = await api.login(email, password); localStorage.setItem('campo_token', session.access_token); setUser(session.user); return session.user },
    logout: async () => { try { await api.logout() } finally { localStorage.removeItem('campo_token'); setUser(null) } },
  }), [user, loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error('AuthProvider requerido'); return value }
