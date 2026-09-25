import { expect, test } from '@playwright/test'

async function login(page: import('@playwright/test').Page, email: string) {
  await page.goto('/login')
  await page.getByLabel('Correo').fill(email)
  await page.getByLabel('Contraseña').fill('Demo1234!')
  await page.getByRole('button', { name: /iniciar sesión/i }).click()
}

async function noOverflow(page: import('@playwright/test').Page) {
  const result = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
  expect(result).toBeTruthy()
}

test('admin control tower con datos y mapa', async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 768 })
  await login(page, 'admin.demo@campologistica.bo')
  await expect(page).toHaveURL(/\/app/)
  await expect(page.getByRole('heading', { name: /resumen operacional/i })).toBeVisible()
  await expect(page.getByText(/operaciones$/).first()).not.toContainText(/^0 operaciones$/)
  await expect(page.locator('.leaflet-interactive').first()).toBeVisible()
  await noOverflow(page)
  await page.screenshot({ path: 'test-results/visual/admin-control-tower-desktop.png', fullPage: true })
  await page.goto('/app/pedidos/nuevo')
  await expect.poll(async()=>page.getByLabel('Seleccionar cliente').locator('option').count()).toBeGreaterThan(1)
  await page.getByLabel('Seleccionar cliente').selectOption({index:1})
  await page.getByRole('button',{name:/continuar/i}).click()
  await page.getByRole('button',{name:/seleccionar ubicación en mapa/i}).click()
  await page.screenshot({ path: 'test-results/visual/admin-new-order-map.png', fullPage: true })
})

test('portales conductor y cliente en móvil', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await login(page, 'conductor1.demo@campologistica.bo')
  await expect(page).toHaveURL(/\/driver/)
  await expect(page.getByText(/entrega actual/i)).toBeVisible()
  await noOverflow(page)
  await page.screenshot({ path: 'test-results/visual/driver-home-mobile.png', fullPage: true })
  await page.getByRole('button', { name: /cerrar sesión/i }).click()
  await login(page, 'cliente1.demo@campologistica.bo')
  await expect(page).toHaveURL(/\/client/)
  await expect(page.getByText(/dónde está mi entrega/i)).toBeVisible()
  await noOverflow(page)
  await page.screenshot({ path: 'test-results/visual/client-home-mobile.png', fullPage: true })
})
