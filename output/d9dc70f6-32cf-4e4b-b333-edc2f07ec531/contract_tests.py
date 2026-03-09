import pytest
import httpx
from pydantic import BaseModel, ValidationError

# Define the response schema using Pydantic
class GetTestResponse(BaseModel):
    type: str
    _truncated: bool

# Pytest fixture for the HTTP client
@pytest.fixture
def client():
    with httpx.Client(base_url="http://localhost:8000") as client:
        yield client

# Test for the GET /test endpoint status code
def test_get_test_status_code(client):
    response = client.get("/test")
    assert response.status_code == 200

# Test for the GET /test endpoint response shape
def test_get_test_response_shape(client):
    response = client.get("/test")
    try:
        GetTestResponse.parse_obj(response.json())
    except ValidationError as e:
        pytest.fail(f"Response validation failed: {e}")