import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { join } from 'node:path'


const backendDir = fileURLToPath(new URL('../../backend/', import.meta.url))
const python = join(backendDir, '.venv', 'Scripts', 'python.exe')
const adminUrl = process.env.E2E_DATABASE_ADMIN_URL
  ?? process.env.TEST_DATABASE_ADMIN_URL
  ?? 'postgresql+psycopg://campo_logistica:change_me_for_local_development@127.0.0.1:55432/postgres'

export default function globalTeardown() {
  execFileSync(python, ['-m', 'tests.e2e_server', 'drop'], {
    cwd: backendDir,
    env: {
      ...process.env,
      E2E_DATABASE_ADMIN_URL: adminUrl,
    },
    stdio: 'inherit',
  })
}
