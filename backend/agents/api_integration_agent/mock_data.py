"""
mock_data.py
============
Hardcoded Petstore outputs for MOCK_MODE = True.
Lets the full pipeline run without any LLM calls.
"""

from agents.api_integration_agent.schemas import SpecAnalysis, EndpointSummary

# ── Mock raw OpenAPI spec ─────────────────────────────────────

MOCK_RAW_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Petstore", "version": "1.0.0"},
    "servers": [{"url": "https://petstore3.swagger.io/api/v3"}],
    "paths": {
        "/pets": {
            "get": {
                "operationId": "list_pets",
                "summary": "List all pets",
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {
                        "description": "A list of pets",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Pet"},
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "operationId": "create_pet",
                "summary": "Create a pet",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/NewPet"}
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/pets/{petId}": {
            "get": {
                "operationId": "get_pet_by_id",
                "summary": "Info for a specific pet",
                "parameters": [
                    {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "Pet info",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Pet"}
                            }
                        },
                    }
                },
            },
            "delete": {
                "operationId": "delete_pet",
                "summary": "Delete a pet",
                "parameters": [
                    {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"204": {"description": "Deleted"}},
            },
        },
    },
    "components": {
        "schemas": {
            "Pet": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["id", "name"],
            },
            "NewPet": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["name"],
            },
        }
    },
}


# ── Mock Chain 1 output ───────────────────────────────────────

MOCK_SPEC_ANALYSIS = SpecAnalysis(
    base_url="https://petstore3.swagger.io/api/v3",
    auth_type="bearer",
    auth_location="header",
    pagination_style="offset",
    endpoints=[
        EndpointSummary(
            path="/pets",
            method="get",
            operation_id="list_pets",
            summary="List all pets",
            path_params=[],
            query_params=["limit"],
            request_body_schema={},
            response_200_schema={
                "type": "array",
                "items": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
            },
        ),
        EndpointSummary(
            path="/pets",
            method="post",
            operation_id="create_pet",
            summary="Create a pet",
            path_params=[],
            query_params=[],
            request_body_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}, "tag": {"type": "string"}},
                "required": ["name"],
            },
            response_200_schema={},
        ),
        EndpointSummary(
            path="/pets/{petId}",
            method="get",
            operation_id="get_pet_by_id",
            summary="Info for a specific pet",
            path_params=["petId"],
            query_params=[],
            request_body_schema={},
            response_200_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                },
            },
        ),
        EndpointSummary(
            path="/pets/{petId}",
            method="delete",
            operation_id="delete_pet",
            summary="Delete a pet",
            path_params=["petId"],
            query_params=[],
            request_body_schema={},
            response_200_schema={},
        ),
    ],
    common_error_codes=[400, 401, 404, 500],
)


# ── Mock Chain 2 output ───────────────────────────────────────

MOCK_CLIENT_STUBS = '''"""
client_stubs.py
Generated by API Integration Agent (mock)
Base URL: https://petstore3.swagger.io/api/v3
Auth: Bearer token in Authorization header
"""

import httpx
from typing import Optional


BASE_URL = "https://petstore3.swagger.io/api/v3"


def get_client(token: str) -> httpx.Client:
    """Return an authenticated httpx client."""
    return httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    )


def list_pets(client: httpx.Client, limit: Optional[int] = None) -> list:
    """List all pets. Optionally limit the number of results."""
    params = {}
    if limit is not None:
        params["limit"] = limit
    response = client.get("/pets", params=params)
    response.raise_for_status()
    return response.json()


def create_pet(client: httpx.Client, body: dict) -> dict:
    """Create a new pet. Body must include 'name'."""
    response = client.post("/pets", json=body)
    response.raise_for_status()
    return response.json()


def get_pet_by_id(client: httpx.Client, petId: str) -> dict:
    """Get info for a specific pet by ID."""
    response = client.get(f"/pets/{petId}")
    response.raise_for_status()
    return response.json()


def delete_pet(client: httpx.Client, petId: str) -> None:
    """Delete a pet by ID."""
    response = client.delete(f"/pets/{petId}")
    response.raise_for_status()
'''


# ── Mock Chain 3 output ───────────────────────────────────────

MOCK_USAGE_EXAMPLES = '''"""
usage_examples.py
Generated by API Integration Agent (mock)
Shows how to use each function from client_stubs.py
"""

from client_stubs import get_client, list_pets, create_pet, get_pet_by_id, delete_pet

TOKEN = "your-bearer-token-here"
client = get_client(TOKEN)


# ── Example 1: List pets ──────────────────────────────────────
try:
    pets = list_pets(client, limit=10)
    print("Pets:", pets)
except Exception as e:
    print(f"Error listing pets: {e}")


# ── Example 2: Create a pet ───────────────────────────────────
try:
    new_pet = create_pet(client, {"name": "Fluffy", "tag": "cat"})
    print("Created pet:", new_pet)
except Exception as e:
    print(f"Error creating pet: {e}")


# ── Example 3: Get pet by ID ──────────────────────────────────
try:
    pet = get_pet_by_id(client, petId="1")
    print("Pet details:", pet)
except Exception as e:
    if hasattr(e, "response") and e.response.status_code == 404:
        print("Pet not found (404)")
    elif hasattr(e, "response") and e.response.status_code == 401:
        print("Unauthorized — check your token (401)")
    else:
        print(f"Error: {e}")


# ── Example 4: Delete a pet ───────────────────────────────────
try:
    delete_pet(client, petId="1")
    print("Pet deleted successfully")
except Exception as e:
    print(f"Error deleting pet: {e}")
'''


# ── Mock Chain 4 output ───────────────────────────────────────

MOCK_CONTRACT_TESTS = '''"""
contract_tests.py
Generated by API Integration Agent (mock)
Pytest contract tests — verify spec contract, not business logic
"""

import pytest
import httpx
from pydantic import BaseModel
from typing import Optional, List


BASE_URL = "https://petstore3.swagger.io/api/v3"
TEST_TOKEN = "test-token"


# ── Pydantic models for response validation ───────────────────

class Pet(BaseModel):
    id: int
    name: str
    tag: Optional[str] = None


class NewPet(BaseModel):
    name: str
    tag: Optional[str] = None


# ── Fixture ───────────────────────────────────────────────────

@pytest.fixture
def client():
    return httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        timeout=30.0,
    )


# ── Tests ─────────────────────────────────────────────────────

def test_list_pets_status(client):
    """GET /pets should return 200."""
    response = client.get("/pets")
    assert response.status_code == 200


def test_list_pets_schema(client):
    """GET /pets should return a list of Pet objects."""
    response = client.get("/pets", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        Pet.model_validate(item)


def test_create_pet_status(client):
    """POST /pets should return 201."""
    response = client.post("/pets", json={"name": "TestPet", "tag": "test"})
    assert response.status_code in (200, 201)


def test_get_pet_by_id_status(client):
    """GET /pets/{petId} should return 200 or 404."""
    response = client.get("/pets/1")
    assert response.status_code in (200, 404)


def test_get_pet_by_id_schema(client):
    """GET /pets/{petId} 200 response must match Pet schema."""
    response = client.get("/pets/1")
    if response.status_code == 200:
        Pet.model_validate(response.json())


def test_delete_pet_status(client):
    """DELETE /pets/{petId} should return 204 or 404."""
    response = client.delete("/pets/9999")
    assert response.status_code in (204, 404)
'''
