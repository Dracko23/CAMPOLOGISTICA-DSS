import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, CalendarDays, Clock3, Edit3, LoaderCircle, MapPin, Package, Route, Trash2, UserRound } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { Badge, Button, Card, ConfirmDialog, ErrorState, Field, Input, LoadingTable, Modal, Select } from '@/components/ui'
import { api, errorMessage, type Pedido } from '@/lib/api'

const editSchema = z.object({
  codigo: z.string().trim().min(1, 'El código es obligatorio'),
  fecha_limite: z.string().min(1, 'La fecha límite es obligatoria'),
  peso_kg: z.string().refine((value) => Number(value) > 0, 'El peso debe ser mayor a cero'),
  urgencia: z.enum(['1', '2', '3', '4', '5']),
})

type EditValues = z.infer<typeof editSchema>

function date(value?: string | null) {
  if (!value) return 'Sin registro'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.valueOf())) return value
  return new Intl.DateTimeFormat('es-BO', { dateStyle: 'medium', timeStyle: 'short' }).format(parsed)
}

function EditPedidoForm({ pedido, close }: { pedido: Pedido; close: () => void }) {
  const client = useQueryClient()
  const localDate = pedido.fecha_limite ? new Date(pedido.fecha_limite).toISOString().slice(0, 16) : ''
  const { register, handleSubmit, formState: { errors } } = useForm<EditValues>({ resolver: zodResolver(editSchema), mode: 'onBlur', defaultValues: { codigo: pedido.codigo, fecha_limite: localDate, peso_kg: String(pedido.peso_kg), urgencia: String(pedido.urgencia) as EditValues['urgencia'] } })
  const update = useMutation({
    mutationFn: (values: EditValues) => api.editarPedido(pedido.id_pedido, { pedido: { codigo: values.codigo.toUpperCase(), fecha_limite: new Date(values.fecha_limite).toISOString(), peso_kg: Number(values.peso_kg), urgencia: Number(values.urgencia) } }),
    onSuccess: async () => { toast.success('Pedido actualizado correctamente'); await client.invalidateQueries({ queryKey: ['pedido', pedido.id_pedido] }); await client.invalidateQueries({ queryKey: ['pedidos'] }); close() },
    onError: (error) => toast.error(errorMessage(error)),
  })
  return <form className='space-y-4' onSubmit={handleSubmit((values) => update.mutate(values))} noValidate><Field label='Código del pedido' error={errors.codigo?.message} required><Input {...register('codigo')} /></Field><div className='grid gap-4 sm:grid-cols-2'><Field label='Peso (kg)' error={errors.peso_kg?.message} required><Input {...register('peso_kg')} type='number' min='0.01' step='0.01' /></Field><Field label='Urgencia' error={errors.urgencia?.message} required><Select {...register('urgencia')}><option value='1'>1 · Baja</option><option value='2'>2</option><option value='3'>3 · Media</option><option value='4'>4</option><option value='5'>5 · Crítica</option></Select></Field></div><Field label='Fecha límite' error={errors.fecha_limite?.message} required><Input {...register('fecha_limite')} type='datetime-local' /></Field><div className='flex justify-end gap-3 pt-2'><Button type='button' variant='secondary' onClick={close}>Cancelar</Button><Button type='submit' disabled={update.isPending}>{update.isPending && <LoaderCircle className='animate-spin' size={16} />}Guardar cambios</Button></div></form>
}

export function PedidoDetailPage() {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const client = useQueryClient()
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const validId = Number.isInteger(id) && id > 0
  const query = useQuery({ queryKey: ['pedido', id], queryFn: () => api.pedido(id), enabled: validId })
  const remove = useMutation({ mutationFn: () => api.eliminarPedido(id), onSuccess: async () => { toast.success('Pedido eliminado correctamente'); await Promise.all([client.invalidateQueries({ queryKey: ['pedidos'] }), client.invalidateQueries({ queryKey: ['resumen'] })]); navigate('/pedidos') }, onError: (error) => toast.error(errorMessage(error)) })

  if (!validId) return <Card><ErrorState title='El identificador del pedido no es válido' onRetry={() => navigate('/pedidos')} /></Card>
  if (query.isPending) return <Card><LoadingTable label='Cargando detalle del pedido' /></Card>
  if (query.isError || !query.data) return <Card><ErrorState title='No pudimos cargar el pedido' message={errorMessage(query.error)} onRetry={() => void query.refetch()} /></Card>
  const pedido = query.data
  return <div className='space-y-6'>
    <div><Link to='/pedidos' className='mb-4 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900'><ArrowLeft size={16} />Volver a pedidos</Link><div className='flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between'><div><div className='flex flex-wrap items-center gap-3'><h1 className='text-3xl font-bold tracking-tight text-slate-950'>{pedido.codigo}</h1><Badge value={pedido.estado} /></div><p className='mt-1 text-sm text-slate-500'>Pedido #{pedido.id_pedido} · registrado {date(pedido.fecha_registro)}</p></div><div className='flex flex-wrap gap-2'><Button variant='secondary' onClick={() => setEditOpen(true)}><Edit3 size={16} />Editar</Button><Button variant='secondary' className='text-rose-600' onClick={() => setDeleteOpen(true)}><Trash2 size={16} />Eliminar</Button></div></div></div>
    <section className='grid gap-5 xl:grid-cols-[1.25fr_0.75fr]'>
      <div className='space-y-5'>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Información de entrega</h2><div className='mt-5 grid gap-5 sm:grid-cols-2'><div className='flex gap-3'><span className='grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-sky-50 text-sky-700'><UserRound size={19} /></span><div><p className='text-xs font-semibold uppercase tracking-wide text-slate-400'>Cliente</p><p className='mt-1 font-semibold text-slate-900'>{pedido.cliente.nombre}</p>{pedido.cliente.telefono && <p className='text-sm text-slate-500'>{pedido.cliente.telefono}</p>}{pedido.cliente.email && <p className='text-sm text-slate-500'>{pedido.cliente.email}</p>}</div></div><div className='flex gap-3'><span className='grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-700'><MapPin size={19} /></span><div><p className='text-xs font-semibold uppercase tracking-wide text-slate-400'>Destino</p><p className='mt-1 font-semibold text-slate-900'>{pedido.ubicacion.direccion}</p><p className='text-sm text-slate-500'>Zona {pedido.ubicacion.zona}</p></div></div></div></Card>
        {pedido.asignacion_actual && <Card className='border-sky-200 bg-sky-50/40 p-5'><div className='flex flex-wrap items-start justify-between gap-3'><div><p className='text-xs font-bold uppercase tracking-wider text-sky-700'>Asignación actual</p><h2 className='mt-1 font-bold text-slate-900'>{pedido.asignacion_actual.conductor.nombre} · {pedido.asignacion_actual.vehiculo.placa ?? 'Sin placa'}</h2><p className='mt-1 text-sm text-slate-600'>Asignada {date(pedido.asignacion_actual.fecha_asignacion)}</p></div><Badge value={pedido.asignacion_actual.estado} /></div></Card>}
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Historial de asignaciones</h2>{pedido.asignaciones?.length ? <div className='mt-5 space-y-4'>{pedido.asignaciones.map((assignment) => <div key={assignment.id_asignacion} className='flex gap-3 border-l-2 border-emerald-200 pl-4'><span className='mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-emerald-50 text-emerald-700'><Route size={16} /></span><div className='flex-1'><div className='flex flex-wrap items-center justify-between gap-2'><p className='text-sm font-semibold text-slate-900'>{assignment.conductor.nombre} · {assignment.vehiculo.placa ?? 'Sin placa'}</p><Badge value={assignment.estado} /></div><p className='mt-1 text-xs text-slate-500'>Asignada {date(assignment.fecha_asignacion)}</p></div></div>)}</div> : <p className='mt-4 text-sm text-slate-500'>El pedido todavía no tiene asignaciones.</p>}</Card>
      </div>
      <div className='space-y-5'>
        <Card className='p-5'><h2 className='font-bold text-slate-900'>Condiciones</h2><dl className='mt-5 space-y-4'><div className='flex items-center justify-between gap-4'><dt className='flex items-center gap-2 text-sm text-slate-500'><Package size={16} />Peso</dt><dd className='font-semibold text-slate-900'>{Number(pedido.peso_kg).toLocaleString('es-BO')} kg</dd></div><div className='flex items-center justify-between gap-4'><dt className='flex items-center gap-2 text-sm text-slate-500'><Clock3 size={16} />Urgencia</dt><dd className='font-semibold text-slate-900'>Nivel {pedido.urgencia}</dd></div><div className='flex items-center justify-between gap-4'><dt className='flex items-center gap-2 text-sm text-slate-500'><CalendarDays size={16} />Fecha límite</dt><dd className='text-right text-sm font-semibold text-slate-900'>{date(pedido.fecha_limite)}</dd></div></dl></Card>
        {!pedido.asignacion_actual && pedido.estado === 'pendiente' && <Card className='border-emerald-200 bg-emerald-50/60 p-5'><h2 className='font-bold text-emerald-950'>Listo para planificar</h2><p className='mt-1 text-sm leading-6 text-emerald-800'>Asigna un conductor y un vehículo disponible para iniciar la operación.</p><Link to='/asignaciones' className='mt-4 inline-flex h-10 items-center gap-2 rounded-xl bg-emerald-600 px-4 text-sm font-semibold text-white hover:bg-emerald-500'>Crear asignación <Route size={16} /></Link></Card>}
      </div>
    </section>
    <Modal open={editOpen} onOpenChange={setEditOpen} title='Editar pedido' description='Actualiza las condiciones operativas del pedido.'>{editOpen && <EditPedidoForm pedido={pedido} close={() => setEditOpen(false)} />}</Modal>
    <ConfirmDialog open={deleteOpen} onOpenChange={setDeleteOpen} title='Eliminar pedido' description={`Se eliminará ${pedido.codigo}. No es posible deshacer esta acción.`} onConfirm={() => remove.mutate()} busy={remove.isPending} />
  </div>
}
