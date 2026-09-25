import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/app/auth'

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 15_000, refetchOnWindowFocus: false },
      mutations: { retry: false },
    },
  }))

  return <QueryClientProvider client={queryClient}>
    <BrowserRouter><AuthProvider>{children}</AuthProvider></BrowserRouter>
    <Toaster richColors closeButton position='top-right' />
  </QueryClientProvider>
}
