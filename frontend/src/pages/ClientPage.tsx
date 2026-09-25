import { useQuery } from '@tanstack/react-query'
import { CalendarClock, CheckCircle, Circle, MapPin, Navigation, Package } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '@/app/auth'
import { TrackingPanel } from '@/components/TrackingPanel'
import { Card, ErrorState, Skeleton } from '@/components/ui'
import { api, type AsignacionResumen } from '@/lib/api'

const stages = [
  { key:'registrado', label:'Pedido registrado' }, { key:'asignada', label:'Asignado' },
  { key:'aceptada', label:'Aceptado' }, { key:'en_camino', label:'En camino' },
  { key:'llegue', label:'Llegó al destino' }, { key:'entregada', label:'Entregado' },
]
const orderOf: Record<string,number>={asignada:1,aceptada:2,en_camino:3,llegue:4,entregada:5,cancelada:0}
function stageDate(stage:string, assignment?:AsignacionResumen){if(stage==='asignada')return assignment?.fecha_asignacion;if(stage==='aceptada')return assignment?.fecha_aceptacion;if(stage==='en_camino')return assignment?.fecha_salida;if(stage==='llegue')return assignment?.fecha_llegada;if(stage==='entregada')return assignment?.fecha_entrega}

export function ClientPage({ view = 'home' }: { view?: 'home'|'shipments'|'history'|'profile'|'tracking' }) {
 const { user }=useAuth(); const params=useParams(); const query=useQuery({queryKey:['client-orders'],queryFn:api.clientOrders,refetchInterval:15_000})
 if(view==='profile')return <section><h1 className='text-2xl font-bold'>Mi perfil</h1><Card className='mt-5 p-5'><p className='font-semibold'>{user?.nombre}</p><p className='text-sm text-slate-500'>{user?.email}</p><p className='mt-4 text-xs font-bold uppercase text-emerald-700'>Cliente</p></Card></section>
 if(query.isPending)return <Skeleton className='h-72 w-full'/>; if(query.isError)return <ErrorState title='No pudimos cargar tus envíos' onRetry={()=>void query.refetch()}/>
 const orders=query.data??[]; const selected=orders.find(x=>x.id_pedido===Number(params.pedido))??orders.find(x=>!['entregado','cancelado'].includes(x.estado)); const assignment=selected?.asignacion_actual??selected?.asignaciones?.[0]
 if(view==='tracking')return <section><h1 className='text-2xl font-bold'>Seguimiento</h1>{selected?<><p className='mt-1 text-sm text-slate-500'>{selected.codigo} · {selected.ubicacion.ciudad}</p>{assignment&&<div className='mt-4'><TrackingPanel assignmentId={assignment.id_asignacion}/></div>}<Card className='mt-4 p-5'><p className='flex gap-2 text-sm text-slate-600'><MapPin size={18}/>{selected.ubicacion.direccion}</p><div className='mt-5 space-y-4'>{stages.map((stage,index)=>{const completed=index===0||index<=orderOf[assignment?.estado??''];const date=index===0?selected.fecha_registro:stageDate(stage.key,assignment);const Icon=completed?CheckCircle:Circle;return <div key={stage.key} className={`flex gap-3 text-sm ${completed?'text-emerald-700':'text-slate-400'}`}><Icon size={18}/><div><p className='font-semibold'>{stage.label}</p>{date&&<p className='text-xs opacity-75'>{new Date(date).toLocaleString('es-BO')}</p>}</div></div>})}</div></Card></>:<Card className='mt-5 p-8 text-center'>No tienes envíos activos.</Card>}</section>
 const filtered=view==='history'?orders.filter(x=>x.estado==='entregado'):orders
 return <section><p className='text-sm font-semibold text-emerald-700'>PORTAL CLIENTE</p><h1 className='mt-1 text-2xl font-bold'>{view==='home'?`Hola, ${user?.nombre?.split(' ')[0]}`:view==='history'?'Historial':'Mis envíos'}</h1>{view==='home'&&<p className='mt-2 text-slate-500'>¿Dónde está mi entrega?</p>}<div className='mt-5 space-y-3'>{filtered.map(order=><Card key={order.id_pedido} className='p-5'><div className='flex items-start justify-between'><div><p className='font-bold'>{order.codigo}</p><p className='mt-1 text-sm text-slate-500'>{order.ubicacion.ciudad} · {order.ubicacion.direccion}</p></div><span className='rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700'>{order.estado.replace('_',' ')}</span></div><div className='mt-4 flex items-center justify-between border-t pt-4'><span className='flex gap-2 text-xs text-slate-500'><CalendarClock size={16}/>{order.fecha_limite?new Date(order.fecha_limite).toLocaleDateString('es-BO'):'Sin fecha'}</span><Link to={`/client/tracking/${order.id_pedido}`} className='flex items-center gap-1 text-sm font-bold text-emerald-700'><Navigation size={16}/>Seguir entrega</Link></div></Card>)}{!filtered.length&&<Card className='p-8 text-center'><Package className='mx-auto text-slate-400'/><p className='mt-3 text-slate-500'>No tienes envíos en esta sección.</p></Card>}</div></section>
}
