import * as Dialog from '@radix-ui/react-dialog'
import * as Tooltip from '@radix-ui/react-tooltip'
import {
  Boxes,
  ChevronLeft,
  ClipboardList,
  LayoutDashboard,
  Menu,
  Route,
  Sparkles,
  Truck,
  UserRound,
  UsersRound,
  LogOut,
  X,
} from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/auth'

import { Button } from '@/components/ui'
import { cn } from '@/lib/utils'

const primaryNavigation = [
  { label: 'Inicio', to: '/app', icon: LayoutDashboard },
  { label: 'Pedidos', to: '/app/pedidos', icon: ClipboardList },
  { label: 'Asignaciones', to: '/app/asignaciones', icon: Route },
  { label: 'Clientes', to: '/app/clientes', icon: UserRound },
  { label: 'Conductores', to: '/app/conductores', icon: UsersRound },
  { label: 'Vehículos', to: '/app/vehiculos', icon: Truck },
]

const pageMeta: Record<string, { title: string; breadcrumb: string }> = {
  '/': { title: 'Centro de operaciones', breadcrumb: 'Operación / Inicio' },
  '/pedidos': { title: 'Gestión de pedidos', breadcrumb: 'Operación / Pedidos' },
  '/pedidos/nuevo': { title: 'Nuevo pedido', breadcrumb: 'Operación / Pedidos / Nuevo' },
  '/conductores': { title: 'Equipo de conductores', breadcrumb: 'Operación / Conductores' },
  '/vehiculos': { title: 'Flota de vehículos', breadcrumb: 'Operación / Vehículos' },
  '/asignaciones': { title: 'Planificación operativa', breadcrumb: 'Operación / Asignaciones' },
}

function TooltipLabel({ children, label, active }: { children: ReactNode; label: string; active: boolean }) {
  if (!active) return children
  return <Tooltip.Root><Tooltip.Trigger asChild>{children}</Tooltip.Trigger><Tooltip.Portal><Tooltip.Content side='right' sideOffset={10} className='z-[70] rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-lg'>{label}<Tooltip.Arrow className='fill-slate-900' /></Tooltip.Content></Tooltip.Portal></Tooltip.Root>
}

function SidebarContent({ collapsed, closeMobile }: { collapsed: boolean; closeMobile?: () => void }) {
  return <Tooltip.Provider delayDuration={250}>
    <div className={cn('flex h-20 items-center border-b border-white/10 px-5', collapsed ? 'justify-center px-2' : 'gap-3')}>
      <span className='grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-400 text-slate-950 shadow-sm'><Boxes size={21} aria-hidden='true' /></span>
      {!collapsed && <div className='min-w-0 leading-tight'><p className='text-sm font-extrabold tracking-[0.2em] text-white'>CAMPO</p><p className='mt-0.5 text-[11px] font-bold uppercase tracking-[0.14em] text-emerald-400'>Logística DSS</p></div>}
    </div>
    <nav className='flex-1 overflow-y-auto p-3' aria-label='Navegación principal'>
      {!collapsed && <p className='mb-2 px-3 pt-2 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500'>Operación</p>}
      <div className='space-y-1'>
        {primaryNavigation.map(({ label, to, icon: Icon }) => <TooltipLabel key={to} label={label} active={collapsed}><NavLink to={to} end={to === '/'} onClick={closeMobile} className={({ isActive }) => cn('flex h-11 items-center rounded-xl text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400', collapsed ? 'justify-center px-2' : 'gap-3 px-3', isActive ? 'bg-emerald-400 text-slate-950 shadow-sm' : 'text-slate-300 hover:bg-white/[0.07] hover:text-white')}><Icon size={19} aria-hidden='true' /><span className={cn(collapsed && 'sr-only')}>{label}</span></NavLink></TooltipLabel>)}
      </div>
    </nav>
    {!collapsed && <div className='border-t border-white/10 p-4'><div className='flex items-center gap-3 rounded-xl bg-white/5 p-3 text-slate-300'><Sparkles size={17} className='text-emerald-400' aria-hidden='true' /><div><p className='text-xs font-semibold text-white'>Sistema operacional</p><p className='text-[11px] text-slate-400'>Motor DSS · Próximamente</p></div></div></div>}
  </Tooltip.Provider>
}

function currentDate() {
  const value = new Intl.DateTimeFormat('es-BO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const meta = pageMeta[location.pathname] ?? (location.pathname.startsWith('/pedidos/')
    ? { title: 'Detalle del pedido', breadcrumb: 'Operación / Pedidos / Detalle' }
    : { title: 'Operaciones', breadcrumb: 'Operación' })

  return <div className='min-h-screen w-full max-w-full overflow-x-hidden bg-slate-50 text-slate-950'>
    <aside className={cn('fixed inset-y-0 left-0 z-30 hidden flex-col bg-slate-950 transition-[width] duration-200 lg:flex', collapsed ? 'w-20' : 'w-64')}><SidebarContent collapsed={collapsed} /><Button variant='secondary' size='icon' className='absolute -right-4 top-[86px] h-8 w-8 rounded-full shadow-md' aria-label={collapsed ? 'Expandir menú' : 'Contraer menú'} onClick={() => setCollapsed((value) => !value)}><ChevronLeft className={cn('transition-transform', collapsed && 'rotate-180')} size={15} /></Button></aside>
    <Dialog.Root open={mobileOpen} onOpenChange={setMobileOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className='fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm lg:hidden' />
        <Dialog.Content className='fixed inset-y-0 left-0 z-50 flex w-[min(19rem,88vw)] flex-col bg-slate-950 shadow-2xl outline-none lg:hidden'>
          <Dialog.Title className='sr-only'>Menú de navegación</Dialog.Title>
          <Dialog.Description className='sr-only'>Navegación principal de Campo Logística DSS</Dialog.Description>
          <Dialog.Close asChild><button className='absolute right-3 top-5 z-10 rounded-lg p-2 text-slate-300 hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400' aria-label='Cerrar menú'><X size={19} /></button></Dialog.Close>
          <SidebarContent collapsed={false} closeMobile={() => setMobileOpen(false)} />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
    <div className={cn('min-h-screen w-full max-w-full overflow-x-hidden transition-[padding] duration-200', collapsed ? 'lg:pl-20' : 'lg:pl-64')}>
      <header className='sticky top-0 z-20 flex min-h-16 items-center justify-between gap-3 border-b border-slate-200/80 bg-white/95 px-4 py-2 backdrop-blur sm:px-6 lg:px-8'>
        <div className='flex min-w-0 items-center gap-3'><Button className='shrink-0 lg:hidden' variant='ghost' size='icon' aria-label='Abrir menú' onClick={() => setMobileOpen(true)}><Menu size={21} /></Button><div className='min-w-0'><p className='hidden truncate text-[11px] font-medium text-slate-400 sm:block'>{meta.breadcrumb}</p><p className='truncate text-sm font-semibold text-slate-900'>{meta.title}</p><p className='hidden text-[11px] text-slate-500 md:block'>{currentDate()}</p></div></div>
        <div className='flex shrink-0 items-center gap-2 sm:border-l sm:border-slate-200 sm:pl-4'><span className='grid h-9 w-9 place-items-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-800' aria-hidden='true'>{user?.nombre?.slice(0,2).toUpperCase()}</span><div className='hidden sm:block'><p className='text-xs font-semibold text-slate-800'>{user?.nombre}</p><p className='text-[11px] text-slate-500'>Administrador</p></div><button aria-label='Cerrar sesión' className='rounded-lg p-2 text-slate-500 hover:bg-slate-100' onClick={() => void logout().then(()=>navigate('/login'))}><LogOut size={18}/></button></div>
      </header>
      <main className='mx-auto w-full max-w-[1500px] p-4 sm:p-6 lg:p-8'>{children}</main>
    </div>
  </div>
}
