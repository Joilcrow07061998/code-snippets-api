from uuid import uuid4

import pytest


async def create_account(client, email):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert response.status_code == 201
    login = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "strong-pass-123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register_and_login(client):
    headers = await create_account(client, "dev@example.com")
    assert headers["Authorization"].startswith("Bearer ")


@pytest.mark.asyncio
async def test_snippet_requires_auth(client):
    response = await client.post(
        "/api/v1/snippets",
        json={"title": "hello", "code": "print('hello')", "language": "python"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shared_snippet_is_public(client):
    headers = await create_account(client, "owner@example.com")
    created = await client.post(
        "/api/v1/snippets",
        headers=headers,
        json={"title": "hello", "code": "print('hello')", "language": "python"},
    )
    assert created.status_code == 201
    share_id = created.json()["share_id"]

    response = await client.get(f"/api/v1/snippets/shared/{share_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "print('hello')"


@pytest.mark.asyncio
async def test_other_user_cannot_edit_snippet(client):
    owner_headers = await create_account(client, "owner@example.com")
    other_headers = await create_account(client, "other@example.com")
    created = await client.post(
        "/api/v1/snippets",
        headers=owner_headers,
        json={"title": "hello", "code": "print('hello')", "language": "python"},
    )

    response = await client.patch(
        f"/api/v1/snippets/{created.json()['id']}",
        headers=other_headers,
        json={"title": "changed"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unknown_shared_snippet_returns_404(client):
    response = await client.get(f"/api/v1/snippets/shared/{uuid4()}")
    assert response.status_code == 404
