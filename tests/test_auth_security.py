from app.models import User
from app.routes.auth import _safe_next_url


def test_public_registration_cannot_assign_admin_role(client, app):
    # First account bootstraps the initial administrator.
    first = client.post(
        "/register",
        data={"username": "first-admin", "password": "example-password", "role": "user"},
        follow_redirects=False,
    )
    assert first.status_code == 302

    # Subsequent public registrations must not be able to request admin privileges.
    second = client.post(
        "/register",
        data={"username": "regular-user", "password": "example-password", "role": "admin"},
        follow_redirects=False,
    )
    assert second.status_code == 302

    with app.app_context():
        regular_user = User.query.filter_by(username="regular-user").one()
        assert regular_user.role == "user"


def test_safe_next_url_accepts_local_paths():
    assert _safe_next_url("/dashboard") == "/dashboard"
    assert _safe_next_url("/dashboard?page=2") == "/dashboard?page=2"


def test_safe_next_url_rejects_external_and_malformed_targets():
    assert _safe_next_url("https://example.com") is None
    assert _safe_next_url("//example.com/path") is None
    assert _safe_next_url("/\\\\example.com") is None
    assert _safe_next_url(None) is None
