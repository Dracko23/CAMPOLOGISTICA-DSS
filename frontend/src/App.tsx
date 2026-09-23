import { CheckCircle2, PackageCheck } from "lucide-react"
export default function App() {
  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-slate-50"><section className="w-full max-w-xl rounded-3xl border border-white/10 bg-slate-900/70 p-10 shadow-2xl shadow-emerald-950/30 backdrop-blur"><div className="mb-8 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-400 text-slate-950"><PackageCheck aria-hidden="true" size={25} strokeWidth={2.2} /></div><p className="mb-3 text-sm font-semibold uppercase tracking-[0.24em] text-emerald-400">Tarija DSS</p><h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">CAMPO LOGÍSTICA</h1><div className="mt-9 flex items-center gap-3 border-t border-white/10 pt-6 text-slate-300"><CheckCircle2 className="text-emerald-400" aria-hidden="true" size={20} /><span>Entorno inicial operativo</span></div></section></main>
}

