import { useQuery } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'
import { Activity, ArrowRight, ClipboardCheck, Clock3, Route, Truck } from 'lucide-react'
import { Link } from 'react-router-dom'

import { OperationalMap } from '@/components/OperationalMap'
import { TrackingPanel } from '@/components/TrackingPanel'
import { Card, ErrorState, PageHeader, Skeleton } from '@/components/ui'
import { api } from '@/lib/api'
import type { Pedido } from '@/lib/api'

const statesValue = (orders: Pedido[], state: string) => orders.filter((order) => order.estado === state).length

function relativeDate(value?: string | null) {
  if (!value) return 'Actualizado recientemente'
  return new Intl.DateTimeFormat('es-BO', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

export function OverviewPage() {
  const summary = useQuery({ queryKey: ['resumen'], queryFn: api.resumen })
  const operations = useQuery({ queryKey: ['pedidos', 'mapa'], queryFn: () => api.pedidos({ page_size: 100 }) })
  const fleet = useQuery({ queryKey: ['vehiculos', 'control-tower'], queryFn: () => api.vehiculos({ page_size: 100 }) })
  const orders = operations.data?.items ?? []
  const vehicles = fleet.data?.items ?? []
  const active = orders.filter((order) => ['asignado', 'en_camino'].includes(order.estado)).length
  const trackedAssignment = orders.find((order) => order.asignacion_actual)?.asignacion_actual
  const cards = [
    { label: 'Pedidos', value: summary.data?.pedidos_registrados, icon: ClipboardCheck, color: 'bg-sky-50 text-sky-700' },
    { label: 'Pendientes', value: summary.data?.pedidos_pendientes, icon: Clock3, color: 'bg-amber-50 text-amber-700' },
    { label: 'Asignados', value: summary.data?.pedidos_asignados, icon: Route, color: 'bg-violet-50 text-violet-700' },
    { label: 'En camino', value: statesValue(orders, 'en_camino'), icon: Route, color: 'bg-blue-50 text-blue-700' },
    { label: 'Entregados', value: statesValue(orders, 'entregado'), icon: ClipboardCheck, color: 'bg-teal-50 text-teal-700' },
    { label: 'Vehículos disponibles', value: summary.data?.vehiculos_disponibles, icon: Truck, color: 'bg-cyan-50 text-cyan-700' },
    { label: 'Operaciones activas', value: active, icon: Activity, color: 'bg-emerald-50 text-emerald-700' },
  ]
  const states = orders.reduce<Record<string, number>>((result, order) => ({ ...result, [order.estado]: (result[order.estado] ?? 0) + 1 }), {})
  const cities = orders.reduce<Record<string, number>>((result, order) => { const city = order.ubicacion.ciudad || 'Sin ciudad'; result[city] = (result[city] ?? 0) + 1; return result }, {})
  const tooltip = { trigger: 'item' as const, backgroundColor: '#0f172a', borderWidth: 0, textStyle: { color: '#fff' } }

  return <div className='space-y-7'>
    <PageHeader eyebrow='Control Tower · operación en tiempo real' title='Control Tower · Resumen operacional' description='Demanda, flota y cobertura multiciudad en una sola vista operacional.' action={<Link to='/pedidos/nuevo' className='inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400'>Nuevo pedido <ArrowRight size={17} /></Link>} />
    {summary.isError ? <Card><ErrorState title='No pudimos cargar el resumen operacional' onRetry={() => void summary.refetch()} /></Card> : <>
      <section className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7' aria-label='Indicadores operacionales'>
        {cards.map(({ label, value, icon: Icon, color }) => <Card key={label} className='p-5'><div className='flex items-start justify-between gap-3'><div><p className='text-sm font-medium text-slate-500'>{label}</p>{summary.isPending ? <Skeleton className='mt-3 h-8 w-16' /> : <p className='mt-2 text-3xl font-bold text-slate-950'>{value ?? 0}</p>}</div><span className={`grid h-10 w-10 place-items-center rounded-xl ${color}`}><Icon size={20} /></span></div></Card>)}
      </section>
      <section aria-label='Mapa operacional' className='rounded-2xl border border-slate-200 bg-white p-3 shadow-sm'><div className='flex items-center justify-between px-2 pb-3'><div><h2 className='font-bold text-slate-900'>Mapa operacional</h2><p className='text-xs text-slate-500'>Cobertura nacional · selecciona un punto para ver el detalle</p></div><span className='rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700'>{operations.data?.total ?? 0} operaciones</span></div><OperationalMap orders={orders} /></section>
      {trackedAssignment && <section aria-label='Simulación de seguimiento'><div className='mb-3'><h2 className='font-bold text-slate-900'>Seguimiento de operación</h2><p className='text-xs text-slate-500'>Recorrido reproducible para demostración</p></div><TrackingPanel assignmentId={trackedAssignment.id_asignacion} admin /></section>}
      <section className='grid gap-5 lg:grid-cols-3' aria-label='Analítica operacional'>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Pedidos por estado</h2><ReactECharts opts={{ renderer: 'svg' }} style={{ height: 230 }} option={{ tooltip, legend: { bottom: 0 }, series: [{ type: 'pie', radius: ['45%', '70%'], center: ['50%', '43%'], label: { show: false }, data: Object.entries(states).map(([name, value]) => ({ name: name.replace('_', ' '), value })) }] }} /></Card>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Disponibilidad de flota</h2><ReactECharts opts={{ renderer: 'svg' }} style={{ height: 230 }} option={{ tooltip, legend: { bottom: 0 }, color: ['#10b981', '#64748b'], series: [{ type: 'pie', radius: ['45%', '70%'], center: ['50%', '43%'], label: { show: false }, data: [{ name: 'Disponible', value: vehicles.filter((item) => item.disponible).length }, { name: 'Ocupada', value: vehicles.filter((item) => !item.disponible).length }] }] }} /></Card>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Pedidos por ciudad</h2><ReactECharts opts={{ renderer: 'svg' }} style={{ height: 230 }} option={{ tooltip: { ...tooltip, trigger: 'axis' }, grid: { left: 8, right: 8, top: 24, bottom: 8, containLabel: true }, xAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#e2e8f0' } } }, yAxis: { type: 'category', data: Object.keys(cities) }, series: [{ type: 'bar', data: Object.values(cities), itemStyle: { color: '#0ea5e9', borderRadius: [0, 6, 6, 0] }, barMaxWidth: 20 }] }} /></Card>
      </section>
      <section className='grid gap-5 xl:grid-cols-[1.5fr_1fr]'>
        <Card><div className='flex items-center justify-between border-b border-slate-100 px-5 py-4'><div><h2 className='font-bold text-slate-900'>Actividad reciente</h2><p className='text-xs text-slate-500'>Movimientos persistidos en PostgreSQL</p></div><Link to='/pedidos' className='text-sm font-semibold text-emerald-700'>Ver pedidos</Link></div>{summary.data?.actividad_reciente.length ? <div className='divide-y divide-slate-100'>{summary.data.actividad_reciente.map((item) => <div key={`${item.tipo}-${item.id}`} className='flex gap-3 px-5 py-4'><span className='mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-50' /><div><p className='text-sm font-semibold text-slate-900'>{item.titulo}</p><p className='text-xs text-slate-500'>{item.detalle}</p><p className='mt-1 text-[11px] text-slate-400'>{relativeDate(item.fecha)}</p></div></div>)}</div> : <p className='p-8 text-sm text-slate-500'>Sin actividad por ahora.</p>}</Card>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Próximo incremento</h2><p className='mt-3 text-sm leading-6 text-slate-600'>Plataforma operacional preparada para incorporar el Motor DSS.</p><div className='mt-5 space-y-3'><Link to='/pedidos/nuevo' className='flex items-center justify-between rounded-xl border border-slate-200 p-4 text-sm font-semibold'>Registrar pedido <ArrowRight size={16} /></Link><Link to='/asignaciones' className='flex items-center justify-between rounded-xl border border-slate-200 p-4 text-sm font-semibold'>Crear asignación <ArrowRight size={16} /></Link></div></Card>
      </section>
    </>}
  </div>
}
