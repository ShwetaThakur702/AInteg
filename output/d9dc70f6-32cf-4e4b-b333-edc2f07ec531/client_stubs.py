import httpx

BASE_URL = "http://example.com"  # Replace with the actual base URL

def get_client() -> httpx.Client:
    """Create and return an HTTP client."""
    return httpx.Client(base_url=BASE_URL)

def getTest() -> dict:
    """Retrieve test data from the API.

    Returns:
        dict: The JSON response from the API.
    """
    with get_client() as client:
        response = client.get("/test")
        response.raise_for_status()
        return response.json()