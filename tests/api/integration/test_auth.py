import pytest


@pytest.mark.asyncio
async def test_register(client):

    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "newuser"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_username(client):

    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "another@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "Username already exists."
    }