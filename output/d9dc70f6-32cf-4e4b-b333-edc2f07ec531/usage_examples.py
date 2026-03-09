import httpx

BASE_URL = "http://example.com"  # Replace with the actual base URL

def get_client(token: str) -> httpx.Client:
    """Create and return an HTTP client with authorization."""
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.Client(base_url=BASE_URL, headers=headers)

def getTest() -> dict:
    """Retrieve test data from the API.

    Returns:
        dict: The JSON response from the API.
    """
    with get_client("your_token_here") as client:
        response = client.get("/test")
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    try:
        test_data = getTest()
        print("Test Data:", test_data)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error 404: Resource not found.")
        elif e.response.status_code == 401:
            print("Error 401: Unauthorized access.")
        else:
            print(f"HTTP error occurred: {e}")