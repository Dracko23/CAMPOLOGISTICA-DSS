import * as AlertDialog from '@radix-ui/react-alert-dialog'
import * as Dialog from '@radix-ui/react-dialog'
import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from '@tanstack/react-table'
import { AlertTriangle, ChevronLeft, ChevronRight, Inbox, LoaderCircle, X } from 'lucide-react'
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react'

import { cn } from '@/lib/utils'

export function Button({ className, variant = 'primary', size = 'md', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'icon'
}) {
  return <button className={cn(
    'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
    variant === 'primary' && 'bg-emerald-500 text-slate-950 shadow-sm hover:bg-emerald-400',
    variant === 'secondary' && 'border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50',
    variant === 'ghost' && 'text-slate-600 hover:bg-slate-100 hover:text-slate-950',
    variant === 'danger' && 'bg-rose-600 text-white hover:bg-rose-500',
    size === 'sm' && 'h-9 px-3 text-sm', size === 'md' && 'h-11 px-4 text-sm', size === 'icon' && 'h-10 w-10',
    className,
  )} {...props} />
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn('w-full max-w-full min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-200/40', className)}>{children}</section>
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn('h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 disabled:bg-slate-100', className)} {...props} />
}

export function Select({ className, children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn('h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 disabled:bg-slate-100', className)} {...props}>{children}</select>
}

export function Textarea({ className, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn('min-h-24 w-full resize-y rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10', className)} {...props} />
}

export function Field({ label, error, hint, required, children }: { label: string; error?: string; hint?: string; required?: boolean; children: ReactNode }) {
  return <div className='w-full space-y-1.5'>
    <label className='block w-full space-y-1.5'>
      <span className='block text-sm font-medium text-slate-700'>{label}{required && <span className='ml-1 text-rose-600' aria-hidden='true'>*</span>}</span>
      {children}
    </label>
    {hint && !error && <p className='text-xs text-slate-500'>{hint}</p>}
    {error && <p className='text-xs font-medium text-rose-600' role='alert'>{error}</p>}
  </div>
}

const badgeStyles: Record<string, string> = {
  pendiente: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  asignado: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  asignada: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  en_camino: 'bg-violet-50 text-violet-700 ring-violet-600/20',
  entregado: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  entregada: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  cancelado: 'bg-rose-50 text-rose-700 ring-rose-600/20',
  cancelada: 'bg-rose-50 text-rose-700 ring-rose-600/20',
  disponible: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  no_disponible: 'bg-slate-100 text-slate-600 ring-slate-500/20',
}

export function Badge({ value }: { value: string }) {
  const label = value === 'no_disponible' ? 'No disponible' : value.replace('_', ' ').replace(/^./, (letter) => letter.toUpperCase())
  return <span className={cn('inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset', badgeStyles[value] ?? badgeStyles.no_disponible)}>{label}</span>
}

export function Skeleton({ className }: { className?: string }) {
  return <span className={cn('block animate-pulse rounded-lg bg-slate-200', className)} />
}

export function LoadingTable({ label = 'Cargando información' }: { label?: string }) {
  return <div className='space-y-3 p-5' aria-label={label} role='status'>
    <span className='sr-only'>{label}</span>
    {[1, 2, 3, 4].map((item) => <Skeleton key={item} className='h-14 w-full' />)}
  </div>
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <div className='flex min-h-72 flex-col items-center justify-center px-6 py-12 text-center'>
    <span className='mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-500'><Inbox aria-hidden='true' size={23} /></span>
    <h2 className='font-semibold text-slate-900'>{title}</h2>
    <p className='mt-1 max-w-sm text-sm leading-6 text-slate-500'>{description}</p>
    {action && <div className='mt-5'>{action}</div>}
  </div>
}

export function ErrorState({ title = 'No pudimos cargar la información', message, onRetry }: { title?: string; message?: string; onRetry: () => void }) {
  return <div className='flex min-h-72 flex-col items-center justify-center px-6 py-12 text-center' role='alert'>
    <span className='mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-rose-50 text-rose-600'><AlertTriangle aria-hidden='true' size={23} /></span>
    <h2 className='font-semibold text-slate-900'>{title}</h2>
    {message && <p className='mt-1 max-w-sm text-sm text-slate-500'>{message}</p>}
    <Button className='mt-5' variant='secondary' onClick={onRetry}>Reintentar</Button>
  </div>
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return <header className='flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between'>
    <div>
      {eyebrow && <p className='mb-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-700'>{eyebrow}</p>}
      <h1 className='text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl'>{title}</h1>
      {description && <p className='mt-1.5 max-w-2xl text-sm leading-6 text-slate-500'>{description}</p>}
    </div>
    {action && <div className='shrink-0'>{action}</div>}
  </header>
}

export function Modal({ open, onOpenChange, title, description, children, className }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; description?: string; children: ReactNode; className?: string }) {
  return <Dialog.Root open={open} onOpenChange={onOpenChange}>
    <Dialog.Portal>
      <Dialog.Overlay className='fixed inset-0 z-50 bg-slate-950/50 backdrop-blur-sm data-[state=open]:animate-in' />
      <Dialog.Content className={cn('fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl outline-none', className)}>
        <div className='pr-10'>
          <Dialog.Title className='text-xl font-bold text-slate-950'>{title}</Dialog.Title>
          {description && <Dialog.Description className='mt-1 text-sm leading-6 text-slate-500'>{description}</Dialog.Description>}
        </div>
        <Dialog.Close asChild><Button type='button' variant='ghost' size='icon' className='absolute right-4 top-4' aria-label='Cerrar'><X size={18} /></Button></Dialog.Close>
        <div className='mt-6'>{children}</div>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
}

export function ConfirmDialog({ open, onOpenChange, title, description, confirmLabel = 'Eliminar', onConfirm, busy }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; description: string; confirmLabel?: string; onConfirm: () => void; busy?: boolean }) {
  return <AlertDialog.Root open={open} onOpenChange={onOpenChange}>
    <AlertDialog.Portal>
      <AlertDialog.Overlay className='fixed inset-0 z-50 bg-slate-950/50 backdrop-blur-sm' />
      <AlertDialog.Content className='fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-6 shadow-2xl outline-none'>
        <AlertDialog.Title className='text-lg font-bold text-slate-950'>{title}</AlertDialog.Title>
        <AlertDialog.Description className='mt-2 text-sm leading-6 text-slate-500'>{description}</AlertDialog.Description>
        <div className='mt-6 flex justify-end gap-3'>
          <AlertDialog.Cancel asChild><Button variant='secondary'>Volver</Button></AlertDialog.Cancel>
          <AlertDialog.Action asChild><Button variant='danger' onClick={onConfirm} disabled={busy}>{busy && <LoaderCircle className='animate-spin' size={16} />}{confirmLabel}</Button></AlertDialog.Action>
        </div>
      </AlertDialog.Content>
    </AlertDialog.Portal>
  </AlertDialog.Root>
}

export function DataTable<T>({ data, columns, getRowLabel }: { data: T[]; columns: ColumnDef<T, unknown>[]; getRowLabel?: (row: T) => string }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })
  return <div className='w-full max-w-full min-w-0 overflow-x-auto'>
    <table className='w-full min-w-[720px] border-collapse text-left text-sm'>
      <thead className='border-b border-slate-200 bg-slate-50/80'>
        {table.getHeaderGroups().map((group) => <tr key={group.id}>{group.headers.map((header) => <th key={header.id} scope='col' className='px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500'>{header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}</th>)}</tr>)}
      </thead>
      <tbody className='divide-y divide-slate-100'>
        {table.getRowModel().rows.map((row) => <tr key={row.id} aria-label={getRowLabel?.(row.original)} className='transition hover:bg-slate-50/70'>{row.getVisibleCells().map((cell) => <td key={cell.id} className='px-5 py-4 align-middle text-slate-600'>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>)}
      </tbody>
    </table>
  </div>
}

export function Pagination({ page, totalPages, total, onChange }: { page: number; totalPages: number; total: number; onChange: (page: number) => void }) {
  if (totalPages <= 1) return <div className='border-t border-slate-100 px-5 py-3 text-xs text-slate-500'>{total} registro{total === 1 ? '' : 's'}</div>
  return <div className='flex items-center justify-between gap-4 border-t border-slate-100 px-5 py-3'>
    <span className='text-xs text-slate-500'>Página {page} de {totalPages} · {total} registros</span>
    <div className='flex gap-2'>
      <Button variant='secondary' size='icon' aria-label='Página anterior' disabled={page <= 1} onClick={() => onChange(page - 1)}><ChevronLeft size={17} /></Button>
      <Button variant='secondary' size='icon' aria-label='Página siguiente' disabled={page >= totalPages} onClick={() => onChange(page + 1)}><ChevronRight size={17} /></Button>
    </div>
  </div>
}
