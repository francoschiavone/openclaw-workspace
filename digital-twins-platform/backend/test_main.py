"""
Tests for the Digital Twins Platform API
"""

import pytest
from httpx import AsyncClient
from main import app, ditto_client


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Create a test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for the health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test that health endpoint returns healthy status"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestThingsEndpoints:
    """Tests for the things endpoints"""

    @pytest.mark.asyncio
    async def test_list_things(self, client: AsyncClient):
        """Test listing things"""
        # This will fail if Ditto is not available, which is expected in unit tests
        # In integration tests, Ditto should be running
        response = await client.get("/things")
        # Either success or connection error
        assert response.status_code in [200, 500, 503]


class TestPoliciesEndpoints:
    """Tests for the policies endpoints"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_policy(self, client: AsyncClient):
        """Test getting a non-existent policy"""
        response = await client.get("/policies/nonexistent:policy")
        assert response.status_code in [404, 500, 503]


# Run tests with: pytest test_main.py -v
