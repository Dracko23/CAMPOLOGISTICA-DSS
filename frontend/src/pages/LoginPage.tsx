import { useState, type FormEvent } from 'react'
import { Boxes, LockKeyhole, LogIn, Mail } from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/auth'
import { errorMessage } from '@/lib/api'

export function LoginPage() {
  const { user, login } = useAuth(); const navigate = useNavigate()
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  if (user) return <Navigate to={user.rol === 'admin' ? '/app' : user.rol === 'conductor' ? '/driver' : '/client'} replace />
  async function submit(event: FormEvent) { event.preventDefault(); setBusy(true); setError(''); try { const current = await login(email, password); navigate(current.rol === 'admin' ? '/app' : current.rol === 'conductor' ? '/driver' : '/client', { replace: true }) } catch (reason) { setError(errorMessage(reason)) } finally { setBusy(false) } }
  return <main className='grid min-h-screen place-items-center bg-slate-950 px-4 py-10'>
    <div className='absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,.18),transparent_38%)]' />
    <section className='relative w-full max-w-md rounded-3xl border border-white/10 bg-white p-7 shadow-2xl sm:p-9'>
      <div className='flex items-center gap-3'><span className='grid h-12 w-12 place-items-center rounded-2xl bg-emerald-400 text-slate-950'><Boxes /></span><div><p className='font-extrabold tracking-[.2em]'>CAMPO</p><p className='text-xs font-bold uppercase tracking-[.15em] text-emerald-700'>Logística DSS</p></div></div>
      <h1 className='mt-8 text-2xl font-bold text-slate-950'>Bienvenido a operaciones</h1><p className='mt-2 text-sm text-slate-500'>Accede a tu espacio de trabajo logístico.</p>
      <form onSubmit={submit} className='mt-7 space-y-5'>
        <label className='block text-sm font-semibold text-slate-700'>Correo<div className='relative mt-2'><Mail className='absolute left-3 top-3 text-slate-400' size={18}/><input aria-label='Correo' type='email' required value={email} onChange={e => setEmail(e.target.value)} className='h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 outline-none focus:ring-2 focus:ring-emerald-400'/></div></label>
        <label className='block text-sm font-semibold text-slate-700'>Contraseña<div className='relative mt-2'><LockKeyhole className='absolute left-3 top-3 text-slate-400' size={18}/><input aria-label='Contraseña' type='password' required value={password} onChange={e => setPassword(e.target.value)} className='h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 outline-none focus:ring-2 focus:ring-emerald-400'/></div></label>
        {error && <p role='alert' className='rounded-xl bg-red-50 p-3 text-sm text-red-700'>{error}</p>}
        <button disabled={busy} className='flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 font-bold text-slate-950 hover:bg-emerald-400 disabled:opacity-60'><LogIn size={18}/>{busy ? 'Ingresando…' : 'Iniciar sesión'}</button>
      </form>
    </section>
  </main>
}
