import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { CheckCircle2, LoaderCircle, MapPin, Package, Play, Plus, Search, Truck, UserRound, XCircle } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { Badge, Button, Card, ConfirmDialog, DataTable, EmptyState, ErrorState, Field, Input, LoadingTable, Modal, PageHeader, Pagination, Select } from '@/components/ui'
import { api, errorMessage, type Asignacion, type AsignacionEstado } from '@/lib/api'

const assignmentSchema = z.object({
  id_pedido: z.string().min(1, 'Selecciona un pedido'),
  id_conductor: z.string().min(1, 'Selecciona un conductor'),
  id_vehiculo: z.string().min(1, 'Selecciona un vehículo'),
})

type AssignmentValues = z.infer<typeof assignmentSchema>

function date(value?: string | null) {
  if (!value) return 'Sin registro'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.valueOf())) return value
  return new Intl.DateTimeFormat('es-BO', { dateStyle: 'medium', timeStyle: 'short' }).format(parsed)
}

function AssignmentForm({ close }: { close: () => void }) {
  const client = useQueryClient()
  const orders = useQuery({
    queryKey: ['pedidos', 'disponibles-asignacion'],
    queryFn: () => api.pedidos({ page: 1, page_size: 100, estado: 'pendiente', sort_by: 'fecha_limite', sort_order: 'asc' }),
  })
  const drivers = useQuery({
    queryKey: ['conductores', 'disponibles-asignacion'],
    queryFn: () => api.conductores({ page: 1, page_size: 100, disponible: true, sort_by: 'nombre', sort_order: 'asc' }),
  })
  const vehicles = useQuery({
    queryKey: ['vehiculos', 'disponibles-asignacion'],
    queryFn: () => api.vehiculos({ page: 1, page_size: 100, disponible: true, sort_by: 'capacidad_kg', sort_order: 'asc' }),
  })
  const { register, handleSubmit, watch, formState: { errors } } = useForm<AssignmentValues>({
    resolver: zodResolver(assignmentSchema),
    defaultValues: { id_pedido: '', id_conductor: '', id_vehiculo: '' },
  })
  const [orderId, driverId, vehicleId] = watch(['id_pedido', 'id_conductor', 'id_vehiculo'])
  const order = orders.data?.items.find((item) => item.id_pedido === Number(orderId))
  const driver = drivers.data?.items.find((item) => item.id_conductor === Number(driverId))
  const vehicle = vehicles.data?.items.find((item) => item.id_vehiculo === Number(vehicleId))
  const capacityIsEnough = Boolean(order && vehicle && Number(vehicle.capacidad_kg) >= Number(order.peso_kg))
  const selectionsReady = Boolean(order && driver && vehicle && capacityIsEnough)

  const create = useMutation({
    mutationFn: (values: AssignmentValues) => api.crearAsignacion({
      id_pedido: Number(values.id_pedido),
      id_conductor: Number(values.id_conductor),
      id_vehiculo: Number(values.id_vehiculo),
    }),
    onSuccess: async () => {
      toast.success('Asignación creada correctamente')
      await Promise.all([
        client.invalidateQueries({ queryKey: ['asignaciones'] }),
        client.invalidateQueries({ queryKey: ['pedidos'] }),
        client.invalidateQueries({ queryKey: ['conductores'] }),
        client.invalidateQueries({ queryKey: ['vehiculos'] }),
        client.invalidateQueries({ queryKey: ['resumen'] }),
      ])
      close()
    },
    onError: (error) => toast.error(errorMessage(error)),
  })

  const resourcesPending = orders.isPending || drivers.isPending || vehicles.isPending
  const resourcesError = orders.error ?? drivers.error ?? vehicles.error
  if (resourcesPending) return <div className='space-y-3' aria-label='Cargando recursos para asignación'><LoadingTable label='Cargando recursos para asignación' /></div>
  if (resourcesError) return <ErrorState title='No pudimos cargar los recursos disponibles' message={errorMessage(resourcesError)} onRetry={() => { void orders.refetch(); void drivers.refetch(); void vehicles.refetch() }} />

  return <form className='space-y-5' onSubmit={handleSubmit((values) => create.mutate(values))} noValidate>
    <div className='grid gap-4 sm:grid-cols-3'>
      <Field label='Pedido' error={errors.id_pedido?.message} required>
        <Select {...register('id_pedido')}>
          <option value=''>Seleccionar…</option>
          {orders.data?.items.map((item) => <option key={item.id_pedido} value={item.id_pedido}>{item.codigo} · {Number(item.peso_kg).toLocaleString('es-BO')} kg</option>)}
        </Select>
      </Field>
      <Field label='Conductor' error={errors.id_conductor?.message} required>
        <Select {...register('id_conductor')}>
          <option value=''>Seleccionar…</option>
          {drivers.data?.items.map((item) => <option key={item.id_conductor} value={item.id_conductor}>{item.nombre} · {item.licencia ?? 'sin licencia'}</option>)}
        </Select>
      </Field>
      <Field label='Vehículo' error={errors.id_vehiculo?.message} required>
        <Select {...register('id_vehiculo')} disabled={!order}>
          <option value=''>{order ? 'Seleccionar…' : 'Selecciona un pedido primero'}</option>
          {vehicles.data?.items.map((item) => {
            const insufficient = order ? Number(item.capacidad_kg) < Number(order.peso_kg) : false
            return <option key={item.id_vehiculo} value={item.id_vehiculo} disabled={insufficient}>{item.placa ?? 'Sin placa'} · {Number(item.capacidad_kg).toLocaleString('es-BO')} kg{insufficient ? ' · capacidad insuficiente' : ''}</option>
          })}
        </Select>
      </Field>
    </div>

    <section className='rounded-2xl border border-slate-200 bg-slate-50 p-4' aria-label='Resumen de la asignación'>
      <h3 className='text-sm font-bold text-slate-900'>Resumen antes de confirmar</h3>
      {!order && !driver && !vehicle ? <p className='mt-2 text-sm text-slate-500'>Selecciona los tres recursos para comprobar la operación.</p> : <div className='mt-4 grid gap-3 sm:grid-cols-3'>
        <div className='rounded-xl bg-white p-3 ring-1 ring-slate-200'><span className='mb-2 grid h-8 w-8 place-items-center rounded-lg bg-amber-50 text-amber-700'><Package size={16} /></span><p className='text-[10px] font-bold uppercase tracking-wider text-slate-400'>Pedido</p><p className='mt-1 font-semibold text-slate-900'>{order?.codigo ?? 'Pendiente'}</p>{order && <><p className='text-xs text-slate-500'>{Number(order.peso_kg).toLocaleString('es-BO')} kg · urgencia {order.urgencia}</p><p className='mt-1 flex items-start gap-1 text-xs text-slate-500'><MapPin className='mt-0.5 shrink-0' size={12} />{order.ubicacion.direccion}</p></>}</div>
        <div className='rounded-xl bg-white p-3 ring-1 ring-slate-200'><span className='mb-2 grid h-8 w-8 place-items-center rounded-lg bg-sky-50 text-sky-700'><UserRound size={16} /></span><p className='text-[10px] font-bold uppercase tracking-wider text-slate-400'>Conductor</p><p className='mt-1 font-semibold text-slate-900'>{driver?.nombre ?? 'Pendiente'}</p>{driver && <p className='text-xs text-emerald-700'>Disponible</p>}</div>
        <div className='rounded-xl bg-white p-3 ring-1 ring-slate-200'><span className='mb-2 grid h-8 w-8 place-items-center rounded-lg bg-cyan-50 text-cyan-700'><Truck size={16} /></span><p className='text-[10px] font-bold uppercase tracking-wider text-slate-400'>Vehículo</p><p className='mt-1 font-semibold text-slate-900'>{vehicle?.placa ?? 'Pendiente'}</p>{vehicle && <p className={capacityIsEnough ? 'text-xs text-emerald-700' : 'text-xs font-medium text-rose-600'}>{Number(vehicle.capacidad_kg).toLocaleString('es-BO')} kg · {capacityIsEnough ? 'capacidad válida' : 'capacidad insuficiente'}</p>}</div>
      </div>}
    </section>
    <div className='flex flex-col-reverse justify-end gap-3 sm:flex-row'><Button type='button' variant='secondary' onClick={close}>Cancelar</Button><Button type='submit' disabled={create.isPending || !selectionsReady}>{create.isPending && <LoaderCircle className='animate-spin' size={16} />}Confirmar asignación</Button></div>
  </form>
}

export function AsignacionesPage() {
  const client = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<'' | AsignacionEstado>('')
  const [createOpen, setCreateOpen] = useState(false)
  const [cancelTarget, setCancelTarget] = useState<Asignacion | null>(null)
  const query = useQuery({
    queryKey: ['asignaciones', page, search, status],
    queryFn: () => api.asignaciones({ page, page_size: 10, q: search, estado: status, sort_by: 'fecha_asignacion', sort_order: 'desc' }),
  })
  const update = useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: AsignacionEstado }) => api.estadoAsignacion(id, estado),
    onSuccess: async (_, variables) => {
      toast.success(variables.estado === 'en_camino' ? 'Ruta iniciada correctamente' : variables.estado === 'entregada' ? 'Entrega registrada correctamente' : 'Asignación cancelada correctamente')
      setCancelTarget(null)
      await Promise.all([
        client.invalidateQueries({ queryKey: ['asignaciones'] }),
        client.invalidateQueries({ queryKey: ['pedidos'] }),
        client.invalidateQueries({ queryKey: ['conductores'] }),
        client.invalidateQueries({ queryKey: ['vehiculos'] }),
        client.invalidateQueries({ queryKey: ['resumen'] }),
      ])
    },
    onError: (error) => toast.error(errorMessage(error)),
  })

  const actions = (assignment: Asignacion) => <div className='flex flex-wrap justify-end gap-1.5'>
    {assignment.estado === 'asignada' && <Button variant='secondary' size='sm' onClick={() => update.mutate({ id: assignment.id_asignacion, estado: 'en_camino' })} disabled={update.isPending}><Play size={15} />Iniciar</Button>}
    {assignment.estado === 'en_camino' && <Button size='sm' onClick={() => update.mutate({ id: assignment.id_asignacion, estado: 'entregada' })} disabled={update.isPending}><CheckCircle2 size={15} />Entregada</Button>}
    {(assignment.estado === 'asignada' || assignment.estado === 'en_camino') && <Button variant='ghost' size='icon' className='h-9 w-9 text-rose-600 hover:bg-rose-50' aria-label={`Cancelar asignación de ${assignment.pedido.codigo}`} onClick={() => setCancelTarget(assignment)}><XCircle size={17} /></Button>}
  </div>

  const columns = useMemo<ColumnDef<Asignacion, unknown>[]>(() => [
    { id: 'pedido', header: 'Pedido', cell: ({ row }) => <div><p className='font-semibold text-slate-900'>{row.original.pedido.codigo}</p><p className='mt-0.5 text-xs text-slate-400'>{Number(row.original.pedido.peso_kg).toLocaleString('es-BO')} kg · {row.original.pedido.ubicacion.zona}</p></div> },
    { id: 'conductor', header: 'Conductor', cell: ({ row }) => <span className='font-medium text-slate-800'>{row.original.conductor.nombre}</span> },
    { id: 'vehiculo', header: 'Vehículo', cell: ({ row }) => <div><p className='font-mono text-xs font-bold text-slate-800'>{row.original.vehiculo.placa ?? 'Sin placa'}</p><p className='mt-0.5 text-xs text-slate-400'>{Number(row.original.vehiculo.capacidad_kg).toLocaleString('es-BO')} kg</p></div> },
    { accessorKey: 'fecha_asignacion', header: 'Asignada', cell: ({ row }) => <span className='text-xs'>{date(row.original.fecha_asignacion)}</span> },
    { accessorKey: 'estado', header: 'Estado', cell: ({ row }) => <Badge value={row.original.estado} /> },
    { id: 'actions', header: () => <span className='sr-only'>Acciones</span>, cell: ({ row }) => actions(row.original) },
  // `actions` only captures stable setters/mutation functions for row rendering.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  ], [])

  return <div className='space-y-6'>
    <PageHeader eyebrow='Planificación operacional' title='Asignaciones' description='Vincula pedidos pendientes con recursos disponibles y controla su ejecución.' action={<Button onClick={() => setCreateOpen(true)}><Plus size={17} />Nueva asignación</Button>} />
    <Card>
      <div className='flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row'>
        <label className='relative flex-1'><span className='sr-only'>Buscar asignaciones</span><Search className='pointer-events-none absolute left-3 top-3 text-slate-400' size={18} /><Input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} className='pl-10' placeholder='Buscar por pedido, conductor o placa…' /></label>
        <Select aria-label='Filtrar asignaciones por estado' value={status} onChange={(event) => { setStatus(event.target.value as typeof status); setPage(1) }} className='sm:w-52'><option value=''>Todos los estados</option><option value='asignada'>Asignadas</option><option value='en_camino'>En camino</option><option value='entregada'>Entregadas</option><option value='cancelada'>Canceladas</option></Select>
      </div>
      {query.isPending ? <LoadingTable label='Cargando asignaciones' /> : query.isError ? <ErrorState title='No pudimos cargar las asignaciones' message={errorMessage(query.error)} onRetry={() => void query.refetch()} /> : !query.data.items.length ? <EmptyState title={search || status ? 'No encontramos asignaciones' : 'Aún no hay asignaciones'} description={search || status ? 'Prueba cambiando los filtros de búsqueda.' : 'Selecciona un pedido, un conductor y un vehículo para planificar la primera entrega.'} action={!search && !status && <Button onClick={() => setCreateOpen(true)}><Plus size={16} />Nueva asignación</Button>} /> : <>
        <div className='hidden lg:block'><DataTable data={query.data.items} columns={columns} getRowLabel={(row) => `Asignación ${row.pedido.codigo}`} /></div>
        <div className='divide-y divide-slate-100 lg:hidden'>{query.data.items.map((item) => <article key={item.id_asignacion} className='p-4'><div className='flex items-start justify-between gap-3'><div><p className='font-semibold text-slate-900'>{item.pedido.codigo}</p><p className='mt-1 text-sm text-slate-600'>{item.conductor.nombre} · {item.vehiculo.placa}</p></div><Badge value={item.estado} /></div><p className='mt-2 text-xs text-slate-500'>{item.pedido.ubicacion.direccion} · {Number(item.pedido.peso_kg).toLocaleString('es-BO')} kg</p><div className='mt-3 border-t border-slate-100 pt-3'>{actions(item)}</div></article>)}</div>
        <Pagination page={query.data.page} totalPages={query.data.total_pages} total={query.data.total} onChange={setPage} />
      </>}
    </Card>
    <Modal open={createOpen} onOpenChange={setCreateOpen} title='Nueva asignación' description='Solo se muestran recursos disponibles. La capacidad se valida antes de guardar.' className='max-w-4xl'>{createOpen && <AssignmentForm close={() => setCreateOpen(false)} />}</Modal>
    <ConfirmDialog open={Boolean(cancelTarget)} onOpenChange={(open) => !open && setCancelTarget(null)} title='Cancelar asignación' description={`El pedido ${cancelTarget?.pedido.codigo ?? ''}, el conductor y el vehículo volverán a quedar disponibles.`} confirmLabel='Cancelar asignación' onConfirm={() => cancelTarget && update.mutate({ id: cancelTarget.id_asignacion, estado: 'cancelada' })} busy={update.isPending} />
  </div>
}
