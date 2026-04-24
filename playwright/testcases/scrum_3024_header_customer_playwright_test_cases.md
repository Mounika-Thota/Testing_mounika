# SCRUM-3024 Playwright Test Cases - Header Customer Display

## Execution

- `pnpm exec playwright test playwright/tests/header-customer.spec.ts`

## Scope

- Story: `SCRUM-3024`
- Requirement: show customer name in header after login; fallback to display name when missing.

## Preconditions

- UI application is reachable.
- Dashboard route is accessible for contributor role.
- Auth cookies can be set in browser context.

## TC-SCRUM-3024-PW-01 - Show customer name when available

Test data:
- User: `Jane Doe`
- Role: `contributor`
- `customer_name`: `Acme Corp`

Steps:
1. Seed auth cookies (`auth_user`, `access_token`) with customer_name present.
2. Open `/contributor/dashboard`.
3. Verify header renders `Acme Corp`.

Expected:
- `Acme Corp` is visible in the header logo section.

Automation:
- `playwright/tests/header-customer.spec.ts` → `shows customer_name in header when available`

## TC-SCRUM-3024-PW-02 - Fallback to display_name

Test data:
- User: `Jane Doe`
- Role: `contributor`
- `customer_name`: absent

Steps:
1. Seed auth cookies without `customer_name`.
2. Open `/contributor/dashboard`.
3. Verify header user identity shows `Jane Doe`.

Expected:
- User menu button label includes `Jane Doe`.

Automation:
- `playwright/tests/header-customer.spec.ts` → `falls back to display_name when customer_name is missing`
