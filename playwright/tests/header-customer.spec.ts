import { test, expect } from '@playwright/test';

const AUTH_USER_COOKIE = 'auth_user';
const ACCESS_TOKEN_COOKIE = 'access_token';

async function setAuthenticatedUserCookie(
  page: Parameters<typeof test>[0]['page'],
  payload: Record<string, unknown>
): Promise<void> {
  await page.context().addCookies([
    {
      name: AUTH_USER_COOKIE,
      value: encodeURIComponent(JSON.stringify(payload)),
      domain: '127.0.0.1',
      path: '/',
      httpOnly: false,
      secure: false,
      sameSite: 'Lax',
    },
    {
      name: ACCESS_TOKEN_COOKIE,
      value: encodeURIComponent(JSON.stringify('dummy-access-token')),
      domain: '127.0.0.1',
      path: '/',
      httpOnly: false,
      secure: false,
      sameSite: 'Lax',
    },
  ]);
}

test.describe('SCRUM-3024 header customer display', () => {
  test.describe.configure({ mode: 'parallel' });

  test('shows customer_name in header when available', async ({ page }) => {
    await setAuthenticatedUserCookie(page, {
      id: 'user-1',
      name: 'Jane Doe',
      display_name: 'Jane Doe',
      email: 'jane@example.com',
      customer_name: 'Acme Corp',
      role: 'contributor',
    });

    await page.goto('/contributor/dashboard');

    await expect(page.getByText('Acme Corp')).toBeVisible();
  });

  test('falls back to display_name when customer_name is missing', async ({ page }) => {
    await setAuthenticatedUserCookie(page, {
      id: 'user-1',
      name: 'Jane Doe',
      display_name: 'Jane Doe',
      email: 'jane@example.com',
      role: 'contributor',
    });

    await page.goto('/contributor/dashboard');

    await expect(
      page.getByRole('button', { name: /User menu for Jane Doe/i })
    ).toBeVisible();
  });
});
