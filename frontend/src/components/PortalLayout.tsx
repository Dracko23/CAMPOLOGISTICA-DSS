import { CircleUserRound, History, Home, LogOut, Map, Navigation, Package, Route } from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/auth'
import type { ReactNode } from 'react'

export function PortalLayout({ kind, children }: { kind: 'driver' | 'client'; children: ReactNode }) {
  const { logout } = useAuth(); const navigate = useNavigate()
  const driver = kind === 'driver'
  const links = driver
    ? [{ to: '/driver', label: 'Hoy', icon: Home }, { to: '/driver/delivery', label: 'Mi entrega', icon: Package }, { to: '/driver/route', label: 'Ruta', icon: Navigation }, { to: '/driver/history', label: 'Historial', icon: History }, { to: '/driver/profile', label: 'Perfil', icon: CircleUserRound }]
    : [{ to: '/client', label: 'Inicio', icon: Home }, { to: '/client/shipments', label: 'Mis envíos', icon: Package }, { to: '/client/tracking', label: 'Seguimiento', icon: Map }, { to: '/client/history', label: 'Historial', icon: History }, { to: '/client/profile', label: 'Perfil', icon: CircleUserRound }]
  return <div className='min-h-screen bg-slate-50 pb-24 text-slate-950'><header className='sticky top-0 z-20 border-b bg-slate-950 px-4 py-4 text-white'><div className='mx-auto flex max-w-5xl items-center justify-between'><div className='flex items-center gap-2 font-bold'><Route className='text-emerald-400'/>CAMPO <span className='text-xs text-slate-400'>{driver ? 'CONDUCTOR' : 'CLIENTE'}</span></div><button aria-label='Cerrar sesión' onClick={() => void logout().then(() => navigate('/login'))} className='rounded-lg p-2 hover:bg-white/10'><LogOut size={19}/></button></div></header><main className='mx-auto max-w-5xl p-4 sm:p-6'>{children}</main><nav className='fixed inset-x-0 bottom-0 z-30 border-t bg-white/95 backdrop-blur'><div className='mx-auto grid max-w-xl grid-cols-5'>{links.map(({to,label,icon:Icon}) => <NavLink key={to} to={to} end={to === `/${kind}`} className={({isActive}) => `flex min-h-16 flex-col items-center justify-center gap-1 text-[10px] font-semibold ${isActive ? 'text-emerald-700' : 'text-slate-500'}`}><Icon size={20}/>{label}</NavLink>)}</div></nav></div>
}
