import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { ArrowDownAZ, ArrowUpAZ, Eye, Plus, Search, Trash2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'

import { Badge, Button, Card, ConfirmDialog, DataTable, EmptyState, ErrorState, Input, LoadingTable, PageHeader, Pagination, Select } from '@/components/ui'
import { api, errorMessage, type Pedido, type PedidoEstado } from '@/lib/api'

const states: Array<{ value: '' | PedidoEstado; label: string }> = [
  { value: '', label: 'Todos los estados' },
  { value: 'pendiente', label: 'Pendientes' },
  { value: 'asignado', label: 'Asignados' },
  { value: 'en_camino', label: 'En camino' },
  { value: 'entregado', label: 'Entregados' },
  { value: 'cancelado', label: 'Cancelados' },
]

function number(value: number | string) {
  return new Intl.NumberFormat('es-BO', { maximumFractionDigits: 2 }).format(Number(value))
}

function date(value?: string | null) {
  if (!value) return 'Sin fecha'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.valueOf())) return value
  return new Intl.DateTimeFormat('es-BO', { dateStyle: 'medium' }).format(parsed)
}

export function PedidosPage() {
  const client = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [estado, setEstado] = useState<'' | PedidoEstado>('')
  const [urgencia, setUrgencia] = useState('')
  const [zona, setZona] = useState('')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [deleteTarget, setDeleteTarget] = useState<Pedido | null>(null)
  const query = useQuery({
    queryKey: ['pedidos', page, search, estado, urgencia, zona, sortOrder],
    queryFn: () => api.pedidos({ page, page_size: 10, q: search, estado, urgencia, zona, sort_by: 'fecha_registro', sort_order: sortOrder }),
  })
  const remove = useMutation({
    mutationFn: (id: number) => api.eliminarPedido(id),
    onSuccess: async () => {
      toast.success('Pedido eliminado correctamente')
      setDeleteTarget(null)
      await Promise.all([client.invalidateQueries({ queryKey: ['pedidos'] }), client.invalidateQueries({ queryKey: ['resumen'] })])
    },
    onError: (error) => toast.error(errorMessage(error)),
  })

  const columns = useMemo<ColumnDef<Pedido, unknown>[]>(() => [
    { accessorKey: 'codigo', header: 'Código', cell: ({ row }) => <div><p className='font-semibold text-slate-900'>{row.original.codigo}</p><p className='mt-0.5 text-xs text-slate-400'>#{row.original.id_pedido}</p></div> },
    { id: 'cliente', header: 'Cliente', cell: ({ row }) => <p className='font-medium text-slate-800'>{row.original.cliente.nombre}</p> },
    { id: 'ubicacion', header: 'Ubicación', cell: ({ row }) => <div><p className='max-w-[200px] truncate text-sm text-slate-700'>{row.original.ubicacion.direccion}</p><p className='mt-0.5 text-xs text-slate-400'>{row.original.ubicacion.zona}</p></div> },
    { accessorKey: 'fecha_limite', header: 'Fecha límite', cell: ({ row }) => <span className='whitespace-nowrap text-xs'>{date(row.original.fecha_limite)}</span> },
    { accessorKey: 'peso_kg', header: 'Carga', cell: ({ row }) => <span>{number(row.original.peso_kg)} kg</span> },
    { accessorKey: 'urgencia', header: 'Prioridad', cell: ({ row }) => <span className='font-medium'>Nivel {row.original.urgencia}</span> },
    { accessorKey: 'estado', header: 'Estado', cell: ({ row }) => <Badge value={row.original.estado} /> },
    { id: 'actions', header: () => <span className='sr-only'>Acciones</span>, cell: ({ row }) => <div className='flex justify-end gap-1'><Link to={`/pedidos/${row.original.id_pedido}`} className='inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-900' aria-label={`Ver pedido ${row.original.codigo}`}><Eye size={17} /></Link><Button variant='ghost' size='icon' className='h-9 w-9 text-rose-600 hover:bg-rose-50 hover:text-rose-700' aria-label={`Eliminar pedido ${row.original.codigo}`} onClick={() => setDeleteTarget(row.original)}><Trash2 size={17} /></Button></div> },
  ], [])

  const clearFilters = () => { setSearch(''); setEstado(''); setUrgencia(''); setZona(''); setPage(1) }
  const hasFilters = Boolean(search || estado || urgencia || zona)
  return <div className='space-y-6'>
    <PageHeader eyebrow='Gestión operacional' title='Pedidos' description='Registra, consulta y da seguimiento al ciclo de cada pedido.' action={<Link to='/pedidos/nuevo' className='inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 text-sm font-semibold text-slate-950 hover:bg-emerald-400'><Plus size={17} />Nuevo pedido</Link>} />
    <Card>
      <div className='grid gap-3 border-b border-slate-100 p-4 sm:grid-cols-2 xl:grid-cols-[minmax(18rem,1fr)_12rem_9rem_12rem_auto]'>
        <label className='relative'><span className='sr-only'>Buscar pedidos</span><Search className='pointer-events-none absolute left-3 top-3 text-slate-400' size={18} /><Input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} className='pl-10' placeholder='Código, cliente o dirección…' /></label>
        <Select aria-label='Filtrar por estado' value={estado} onChange={(event) => { setEstado(event.target.value as typeof estado); setPage(1) }}>{states.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</Select>
        <Select aria-label='Filtrar por urgencia' value={urgencia} onChange={(event) => { setUrgencia(event.target.value); setPage(1) }}><option value=''>Urgencia</option>{[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>Nivel {level}</option>)}</Select>
        <label><span className='sr-only'>Filtrar por zona</span><Input value={zona} onChange={(event) => { setZona(event.target.value); setPage(1) }} placeholder='Zona' /></label>
        <Button variant='secondary' onClick={() => setSortOrder((value) => value === 'asc' ? 'desc' : 'asc')} aria-label={`Orden ${sortOrder === 'asc' ? 'ascendente' : 'descendente'} por fecha de registro`}>{sortOrder === 'asc' ? <ArrowUpAZ size={17} /> : <ArrowDownAZ size={17} />}Registro</Button>
      </div>
      {query.isPending ? <LoadingTable label='Cargando pedidos' /> : query.isError ? <ErrorState title='No pudimos cargar los pedidos' message={errorMessage(query.error)} onRetry={() => void query.refetch()} /> : !query.data.items.length ? <EmptyState title={hasFilters ? 'No encontramos coincidencias' : 'Aún no hay pedidos'} description={hasFilters ? 'Prueba otros criterios para ampliar la búsqueda.' : 'Registra el primer pedido para comenzar a planificar la operación.'} action={hasFilters ? <Button variant='secondary' onClick={clearFilters}>Limpiar filtros</Button> : <Link to='/pedidos/nuevo' className='inline-flex h-10 items-center gap-2 rounded-xl bg-emerald-500 px-4 text-sm font-semibold text-slate-950'><Plus size={16} />Registrar pedido</Link>} /> : <><div className='hidden lg:block'><DataTable data={query.data.items} columns={columns} getRowLabel={(row) => `Pedido ${row.codigo}`} /></div><div className='divide-y divide-slate-100 lg:hidden'>{query.data.items.map((pedido) => <article key={pedido.id_pedido} className='p-4'><div className='flex items-start justify-between gap-3'><div><Link to={`/pedidos/${pedido.id_pedido}`} className='font-bold text-slate-900'>{pedido.codigo}</Link><p className='mt-1 text-sm text-slate-600'>{pedido.cliente.nombre}</p></div><Badge value={pedido.estado} /></div><p className='mt-3 text-xs text-slate-500'>{pedido.ubicacion.direccion} · {pedido.ubicacion.zona}</p><div className='mt-2 flex items-center justify-between gap-3 text-xs text-slate-500'><span>{number(pedido.peso_kg)} kg · urgencia {pedido.urgencia}</span><span>{date(pedido.fecha_limite)}</span></div><div className='mt-3 flex justify-end gap-2 border-t border-slate-100 pt-3'><Link to={`/pedidos/${pedido.id_pedido}`} className='inline-flex h-9 items-center gap-2 rounded-lg px-3 text-sm font-semibold text-slate-700 hover:bg-slate-100'><Eye size={16} />Ver</Link><Button variant='ghost' size='sm' className='text-rose-600 hover:bg-rose-50' onClick={() => setDeleteTarget(pedido)}><Trash2 size={16} />Eliminar</Button></div></article>)}</div><Pagination page={query.data.page} totalPages={query.data.total_pages} total={query.data.total} onChange={setPage} /></>}
    </Card>
    <ConfirmDialog open={Boolean(deleteTarget)} onOpenChange={(open) => !open && setDeleteTarget(null)} title='Eliminar pedido' description={`Se eliminará ${deleteTarget?.codigo ?? 'este pedido'}. Esta acción solo es posible si no tiene una asignación activa.`} onConfirm={() => deleteTarget && remove.mutate(deleteTarget.id_pedido)} busy={remove.isPending} />
  </div>
}
