"""Tests that need no database."""

import asyncio
from datetime import datetime

import bcrypt
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models import Role, User
from app.schemas import AuthIn, CategoryOut, ProductIn, ProductQuery
from app.security import decode_token, sign_token, verify_password
from app.services.slug import to_slug

client = TestClient(app)


def test_to_slug():
    assert to_slug("  Red Wool  Coat! ") == "red-wool-coat"
    assert to_slug("A -- B") == "a-b"


def test_token_roundtrip_keeps_numeric_sub():
    user = User(id=7, email="a@b.co", role=Role.ADMIN)
    payload = decode_token(sign_token(user))
    assert (payload.sub, payload.email, payload.role) == (7, "a@b.co", Role.ADMIN)


def test_verifies_bcryptjs_style_hash_and_truncates_long_passwords():
    long_password = "x" * 100
    legacy_hash = bcrypt.hashpw(long_password[:72].encode(), bcrypt.gensalt(4)).decode()
    legacy_hash = legacy_hash.replace("$2b$", "$2a$", 1)  # bcryptjs < 3 emitted $2a$
    assert asyncio.run(verify_password(long_password, legacy_hash))
    assert not asyncio.run(verify_password("wrong-password", legacy_hash))


def test_product_input_accepts_camel_case_and_coerces_quantity():
    body = ProductIn.model_validate(
        {
            "name": "Coat",
            "description": "A long description",
            "aisle": "A-01",
            "quantity": "3",
            "categorySlug": "clothing",
            "eraSlug": "modern",
            "images": [{"url": "http://localhost:4000/uploads/x.png", "sortOrder": 1}],
        }
    )
    assert body.quantity == 3 and body.images[0].sort_order == 1


def test_query_limits_page_size():
    with pytest.raises(ValidationError):
        ProductQuery.model_validate({"pageSize": 49})


def test_email_validation():
    AuthIn(email="admin@wardrobe.house", password="password1")
    with pytest.raises(ValidationError):
        AuthIn(email="not-an-email", password="password1")


def test_datetimes_serialize_as_utc_iso():
    out = CategoryOut(
        id=1, name="C", slug="c", created_at=datetime(2026, 5, 1, 12, 0, 0, 123000), updated_at=datetime(2026, 5, 1)
    ).model_dump(by_alias=True, mode="json")
    assert out["createdAt"] == "2026-05-01T12:00:00.123Z"


def test_health():
    assert client.get("/api/health").json() == {"ok": True}


def test_admin_requires_token():
    response = client.get("/api/admin/products")
    assert response.status_code == 401
    assert response.json() == {"message": "Unauthorized"}


def test_admin_rejects_non_admin():
    token = sign_token(User(id=1, email="u@b.co", role=Role.USER))
    response = client.get("/api/admin/products", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_validation_errors_use_400_with_message():
    response = client.post("/api/auth/login", json={"email": "bad", "password": "x"})
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid body"
