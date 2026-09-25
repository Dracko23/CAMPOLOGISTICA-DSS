import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { Edit3, LoaderCircle, Plus, Search, Trash2, UserRound } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { Badge, Button, Card, ConfirmDialog, DataTable, EmptyState, ErrorState, Field, Input, LoadingTable, Modal, PageHeader, Pagination, Select } from '@/components/ui'
import { api, errorMessage, type Conductor } from '@/lib/api'

const schema = z.object({ nombre: z.string().trim().min(1, 'El nombre es obligatorio'), licencia: z.string().trim().min(1, 'La licencia es obligatoria'), disponible: z.boolean() })
type Values = z.infer<typeof schema>

function ConductorForm({ conductor, close }: { conductor?: Conductor; close: () => void }) {
  const client = useQueryClient()
  const { register, handleSubmit, formState: { errors } } = useForm<Values>({ resolver: zodResolver(schema), mode: 'onBlur', defaultValues: { nombre: conductor?.nombre ?? '', licencia: conductor?.licencia ?? '', disponible: conductor?.disponible ?? true } })
  const save = useMutation({
    mutationFn: (values: Values) => conductor ? api.editarConductor(conductor.id_conductor, values) : api.crearConductor(values),
    onSuccess: async () => { toast.success(conductor ? 'Conductor actualizado correctamente' : 'Conductor registrado correctamente'); await Promise.all([client.invalidateQueries({ queryKey: ['conductores'] }), client.invalidateQueries({ queryKey: ['resumen'] })]); close() },
    onError: (error) => toast.error(errorMessage(error)),
  })
  return <form onSubmit={handleSubmit((values) => save.mutate(values))} className='space-y-4' noValidate><Field label='Nombre' error={errors.nombre?.message} required><Input {...register('nombre')} autoComplete='name' placeholder='Ej. Carlos Mendoza' /></Field><Field label='Licencia' error={errors.licencia?.message} required><Input {...register('licencia')} className='uppercase' placeholder='LIC-TJA-001' /></Field><label className='flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-slate-200 p-4'><span><span className='block text-sm font-semibold text-slate-800'>Disponible</span><span className='mt-0.5 block text-xs text-slate-500'>Puede recibir nuevas asignaciones.</span></span><input {...register('disponible')} type='checkbox' className='h-5 w-5 rounded border-slate-300 accent-emerald-500' /></label><div className='flex justify-end gap-3 pt-2'><Button type='button' variant='secondary' onClick={close}>Cancelar</Button><Button type='submit' disabled={save.isPending}>{save.isPending && <LoaderCircle className='animate-spin' size={16} />}Guardar conductor</Button></div></form>
}

export function ConductoresPage() {
  const client = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [availability, setAvailability] = useState('')
  const [editing, setEditing] = useState<Conductor | 'new' | null>(null)
  const [deleting, setDeleting] = useState<Conductor | null>(null)
  const query = useQuery({ queryKey: ['conductores', page, search, availability], queryFn: () => api.conductores({ page, page_size: 10, q: search, disponible: availability === '' ? undefined : availability === 'true', sort_by: 'nombre', sort_order: 'asc' }) })
  const remove = useMutation({ mutationFn: (id: number) => api.eliminarConductor(id), onSuccess: async () => { toast.success('Conductor eliminado correctamente'); setDeleting(null); await Promise.all([client.invalidateQueries({ queryKey: ['conductores'] }), client.invalidateQueries({ queryKey: ['resumen'] })]) }, onError: (error) => toast.error(errorMessage(error)) })
  const columns = useMemo<ColumnDef<Conductor, unknown>[]>(() => [
    { accessorKey: 'nombre', header: 'Conductor', cell: ({ row }) => <div className='flex items-center gap-3'><span className='grid h-9 w-9 place-items-center rounded-full bg-sky-50 text-sky-700'><UserRound size={17} /></span><span className='font-semibold text-slate-900'>{row.original.nombre}</span></div> },
    { accessorKey: 'licencia', header: 'Licencia', cell: ({ row }) => <span className='font-mono text-xs font-semibold text-slate-700'>{row.original.licencia ?? 'Sin licencia'}</span> },
    { accessorKey: 'disponible', header: 'Disponibilidad', cell: ({ row }) => <Badge value={row.original.disponible ? 'disponible' : 'no_disponible'} /> },
    { id: 'actions', header: () => <span className='sr-only'>Acciones</span>, cell: ({ row }) => <div className='flex justify-end gap-1'><Button variant='ghost' size='icon' className='h-9 w-9' aria-label={`Editar ${row.original.nombre}`} onClick={() => setEditing(row.original)}><Edit3 size={17} /></Button><Button variant='ghost' size='icon' className='h-9 w-9 text-rose-600 hover:bg-rose-50' aria-label={`Eliminar ${row.original.nombre}`} onClick={() => setDeleting(row.original)}><Trash2 size={17} /></Button></div> },
  ], [])
  return <div className='space-y-6'>
    <PageHeader eyebrow='Recursos operativos' title='Conductores' description='Administra el equipo y controla su disponibilidad para nuevas rutas.' action={<Button onClick={() => setEditing('new')}><Plus size={17} />Nuevo conductor</Button>} />
    <Card><div className='flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row'><label className='relative flex-1'><span className='sr-only'>Buscar conductores</span><Search className='absolute left-3 top-3 text-slate-400' size={18} /><Input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} className='pl-10' placeholder='Buscar por nombre o licencia…' /></label><Select aria-label='Filtrar disponibilidad' value={availability} onChange={(event) => { setAvailability(event.target.value); setPage(1) }} className='sm:w-52'><option value=''>Toda disponibilidad</option><option value='true'>Disponibles</option><option value='false'>No disponibles</option></Select></div>
      {query.isPending ? <LoadingTable label='Cargando conductores' /> : query.isError ? <ErrorState title='No pudimos cargar los conductores' message={errorMessage(query.error)} onRetry={() => void query.refetch()} /> : !query.data.items.length ? <EmptyState title={search || availability ? 'No encontramos conductores' : 'Aún no hay conductores'} description={search || availability ? 'Prueba cambiando los filtros de búsqueda.' : 'Agrega el primer conductor para comenzar a asignar pedidos.'} action={!search && !availability && <Button onClick={() => setEditing('new')}><Plus size={16} />Nuevo conductor</Button>} /> : <><div className='hidden sm:block'><DataTable data={query.data.items} columns={columns} getRowLabel={(row) => `Conductor ${row.nombre}`} /></div><div className='divide-y divide-slate-100 sm:hidden'>{query.data.items.map((item) => <article key={item.id_conductor} className='p-4'><div className='flex items-start justify-between gap-3'><div><p className='font-semibold text-slate-900'>{item.nombre}</p><p className='mt-1 font-mono text-xs text-slate-500'>{item.licencia ?? 'Sin licencia'}</p></div><Badge value={item.disponible ? 'disponible' : 'no_disponible'} /></div><div className='mt-3 flex justify-end gap-1 border-t border-slate-100 pt-3'><Button variant='ghost' size='sm' onClick={() => setEditing(item)}><Edit3 size={16} />Editar</Button><Button variant='ghost' size='sm' className='text-rose-600 hover:bg-rose-50' onClick={() => setDeleting(item)}><Trash2 size={16} />Eliminar</Button></div></article>)}</div><Pagination page={query.data.page} totalPages={query.data.total_pages} total={query.data.total} onChange={setPage} /></>}
    </Card>
    <Modal open={Boolean(editing)} onOpenChange={(open) => !open && setEditing(null)} title={editing === 'new' ? 'Nuevo conductor' : 'Editar conductor'} description='La licencia debe ser única dentro de la operación.'>{editing && <ConductorForm conductor={editing === 'new' ? undefined : editing} close={() => setEditing(null)} />}</Modal>
    <ConfirmDialog open={Boolean(deleting)} onOpenChange={(open) => !open && setDeleting(null)} title='Eliminar conductor' description={`Se eliminará a ${deleting?.nombre ?? 'este conductor'}. Solo es posible si no participa en una asignación.`} onConfirm={() => deleting && remove.mutate(deleting.id_conductor)} busy={remove.isPending} />
  </div>
}
