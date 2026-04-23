# SCRUM-3024 Test Cases - Header Customer Display

Execution command for automated script:
- `source .venv/bin/activate && pytest --no-cov tests/unit/test_scrum_3024_header_customer.py -v`

## Scope

- Story: `SCRUM-3024`
- Requirement: After login, header must show customer name (user-related customer), not user name.
- Layers: backend auth payload + UI header rendering contract.

## Preconditions

- User exists and can authenticate.
- User has at least one active project/customer relationship for positive scenarios.
- Auth endpoints return the `user` payload consumed by UI.

## TC-SCRUM-3024-01 - Serialize payload includes customer fields

Test data:
- User: `id=user-1`, `username=jdoe`, `display_name=Jane Doe`
- Customer: `id=cust-1`, `name=Acme Corp`

Steps:
1. Create authenticated user payload in backend.
2. Attach customer context (`customer_id`, `customer_name`).
3. Serialize response user object.
4. Validate `customer_id` and `customer_name` are present and accurate.

Expected:
- `customer_id` equals resolved customer id.
- `customer_name` equals resolved company name.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_01_serialize_user_exposes_customer_fields_when_available`

## TC-SCRUM-3024-02 - Identity fields remain unchanged

Test data:
- Same as TC-01

Steps:
1. Serialize response with customer context.
2. Validate original user fields are unchanged (`username`, `email`, `display_name`).

Expected:
- Existing identity fields are preserved exactly.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_02_serialize_user_preserves_existing_identity_fields`

## TC-SCRUM-3024-03 - Fallback when customer context is missing

Test data:
- User payload with no customer context provided

Steps:
1. Serialize response without customer context.
2. Validate fallback values.

Expected:
- `customer_id` is `None`.
- `customer_name` is `None`.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_03_serialize_user_has_stable_fallback_without_customer_context`

## TC-SCRUM-3024-04 - Resolver uses membership customer (primary path)

Test data:
- Membership query returns: `("cust-1", "Acme Corp")`
- Role: `CONTRIBUTOR`

Steps:
1. Set resolver query to return membership-derived customer.
2. Execute resolver for non-admin user.

Expected:
- Resolver returns membership customer immediately.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_04_resolver_prefers_membership_customer`

## TC-SCRUM-3024-05 - Admin fallback uses owned-project customer

Test data:
- Membership query result: `None`
- Owned-project query returns: `("cust-admin", "Admin Customer")`
- Role: `ADMIN`

Steps:
1. Set membership resolver result to empty.
2. Set admin-owned-project query result to customer.
3. Execute resolver for `ADMIN`.

Expected:
- Resolver returns owned-project customer context.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_05_resolver_uses_owned_project_customer_for_admin_fallback`

## TC-SCRUM-3024-06 - Resolver returns none when no customer is found

Test data:
- Membership query result: `None`
- Role: `CONTRIBUTOR`

Steps:
1. Set membership resolver result to empty.
2. Execute resolver for non-admin role.

Expected:
- Resolver returns `None`.
- Admin fallback path is not executed.

Automation:
- `tests/unit/test_scrum_3024_header_customer.py::test_tc_scrum_3024_06_resolver_returns_none_when_no_customer_context_found`
