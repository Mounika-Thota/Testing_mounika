# Execute: source .venv/bin/activate && pytest --no-cov tests/unit/test_scrum_3024_header_customer.py -v
"""SCRUM-3024 — Header customer display backend tests.

These tests validate the backend contract used by the UI header:
1) auth/session payload includes `customer_name` + `customer_id`
2) fallback behavior is stable when customer context is absent
3) customer resolution logic chooses the expected source

Test case coverage in this script:
- TC-SCRUM-3024-01
- TC-SCRUM-3024-02
- TC-SCRUM-3024-03
- TC-SCRUM-3024-04
- TC-SCRUM-3024-05
- TC-SCRUM-3024-06
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from src.db.users import get_primary_customer_for_user
from src.utils.auth import serialize_user


def _build_user_mock() -> MagicMock:
    """Create a reusable user double for auth payload tests."""
    user = MagicMock()
    user.id = "user-1"
    user.username = "jdoe"
    user.email = "jdoe@example.com"
    user.primary_role = "CONTRIBUTOR"
    user.display_name = "Jane Doe"
    user.avatar_url = None
    user.is_oauth_user = False
    user.oauth_providers = {}
    return user


def test_tc_scrum_3024_01_serialize_user_exposes_customer_fields_when_available():
    """TC-SCRUM-3024-01.

    Steps:
    1. Arrange a valid authenticated user object.
    2. Attach resolved customer context (id + name).
    3. Serialize user payload.
    4. Verify customer fields are present and accurate.
    """
    user = _build_user_mock()

    payload = serialize_user(user, customer={"id": "cust-1", "name": "Acme Corp"})

    assert payload["customer_id"] == "cust-1"
    assert payload["customer_name"] == "Acme Corp"


def test_tc_scrum_3024_02_serialize_user_preserves_existing_identity_fields():
    """TC-SCRUM-3024-02.

    Steps:
    1. Arrange a valid authenticated user object.
    2. Serialize with customer context.
    3. Verify existing identity fields remain unchanged.
    """
    user = _build_user_mock()

    payload = serialize_user(user, customer={"id": "cust-1", "name": "Acme Corp"})

    assert payload["display_name"] == "Jane Doe"
    assert payload["username"] == "jdoe"
    assert payload["email"] == "jdoe@example.com"


def test_tc_scrum_3024_03_serialize_user_has_stable_fallback_without_customer_context():
    """TC-SCRUM-3024-03.

    Steps:
    1. Arrange a valid authenticated user object.
    2. Serialize without customer context.
    3. Verify customer fields are explicitly None.
    """
    user = _build_user_mock()

    payload = serialize_user(user)

    assert payload["customer_id"] is None
    assert payload["customer_name"] is None


def test_tc_scrum_3024_04_resolver_prefers_membership_customer() -> None:
    """TC-SCRUM-3024-04.

    Steps:
    1. Arrange DB chain where membership-derived customer exists.
    2. Call customer resolver for a non-admin user.
    3. Verify resolver returns membership customer context.
    """
    membership_query = MagicMock()
    membership_query.join.return_value = membership_query
    membership_query.filter.return_value = membership_query
    membership_query.order_by.return_value = membership_query
    membership_query.first.return_value = SimpleNamespace(id="cust-1", company_name="Acme Corp")

    db = MagicMock()
    db.query.return_value = membership_query

    result = get_primary_customer_for_user(db=db, user_id="user-1", primary_role="CONTRIBUTOR")

    assert result == {"id": "cust-1", "name": "Acme Corp"}


def test_tc_scrum_3024_05_resolver_uses_owned_project_customer_for_admin_fallback() -> None:
    """TC-SCRUM-3024-05.

    Steps:
    1. Arrange DB chain with no membership customer.
    2. Arrange DB chain with owned-project customer for admin.
    3. Call customer resolver as ADMIN.
    4. Verify fallback returns owned-project customer context.
    """
    membership_query = MagicMock()
    membership_query.join.return_value = membership_query
    membership_query.filter.return_value = membership_query
    membership_query.order_by.return_value = membership_query
    membership_query.first.return_value = None

    owned_query = MagicMock()
    owned_query.join.return_value = owned_query
    owned_query.filter.return_value = owned_query
    owned_query.order_by.return_value = owned_query
    owned_query.first.return_value = SimpleNamespace(
        id="cust-admin", company_name="Admin Customer"
    )

    db = MagicMock()
    db.query.side_effect = [membership_query, owned_query]

    result = get_primary_customer_for_user(db=db, user_id="admin-1", primary_role="ADMIN")

    assert result == {"id": "cust-admin", "name": "Admin Customer"}
    assert db.query.call_count == 2


def test_tc_scrum_3024_06_resolver_returns_none_when_no_customer_context_found() -> None:
    """TC-SCRUM-3024-06.

    Steps:
    1. Arrange DB chain with no membership customer.
    2. Call customer resolver as non-admin user.
    3. Verify resolver returns None and does not use admin fallback path.
    """
    membership_query = MagicMock()
    membership_query.join.return_value = membership_query
    membership_query.filter.return_value = membership_query
    membership_query.order_by.return_value = membership_query
    membership_query.first.return_value = None

    db = MagicMock()
    db.query.return_value = membership_query

    result = get_primary_customer_for_user(
        db=db, user_id="contributor-1", primary_role="CONTRIBUTOR"
    )

    assert result is None
    assert db.query.call_count == 1
