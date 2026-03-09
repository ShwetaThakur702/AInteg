import httpx

BASE_URL = "/api/v3"

def get_client(token: str) -> httpx.Client:
    """Create an authenticated HTTP client."""
    return httpx.Client(base_url=BASE_URL, headers={"Authorization": f"Bearer {token}"})

def updatePet(client: httpx.Client) -> dict:
    """Update an existing pet."""
    response = client.put("/pet")
    response.raise_for_status()
    return response.json()

def addPet(client: httpx.Client) -> dict:
    """Add a new pet."""
    response = client.post("/pet")
    response.raise_for_status()
    return response.json()

def findPetsByStatus(client: httpx.Client, status: str = None) -> dict:
    """Finds Pets by status."""
    params = {"status": status} if status else {}
    response = client.get("/pet/findByStatus", params=params)
    response.raise_for_status()
    return response.json()

def findPetsByTags(client: httpx.Client, tags: str = None) -> dict:
    """Finds Pets by tags."""
    params = {"tags": tags} if tags else {}
    response = client.get("/pet/findByTags", params=params)
    response.raise_for_status()
    return response.json()

def getPetById(client: httpx.Client, petId: int) -> dict:
    """Find pet by ID."""
    response = client.get(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def updatePetWithForm(client: httpx.Client, petId: int) -> dict:
    """Updates a pet in the store with form data."""
    response = client.post(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def deletePet(client: httpx.Client, petId: int) -> dict:
    """Deletes a pet."""
    response = client.delete(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def uploadFile(client: httpx.Client, petId: int) -> dict:
    """Uploads an image."""
    response = client.post(f"/pet/{petId}/uploadImage")
    response.raise_for_status()
    return response.json()

def getInventory(client: httpx.Client) -> dict:
    """Returns pet inventories by status."""
    response = client.get("/store/inventory")
    response.raise_for_status()
    return response.json()

def placeOrder(client: httpx.Client) -> dict:
    """Place an order for a pet."""
    response = client.post("/store/order")
    response.raise_for_status()
    return response.json()

def getOrderById(client: httpx.Client, orderId: int) -> dict:
    """Find purchase order by ID."""
    response = client.get(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def deleteOrder(client: httpx.Client, orderId: int) -> dict:
    """Delete purchase order by ID."""
    response = client.delete(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def createUser(client: httpx.Client) -> dict:
    """Create user."""
    response = client.post("/user")
    response.raise_for_status()
    return response.json()

def createUsersWithListInput(client: httpx.Client) -> dict:
    """Creates list of users with given input array."""
    response = client.post("/user/createWithList")
    response.raise_for_status()
    return response.json()

def loginUser(client: httpx.Client, username: str = None) -> dict:
    """Logs user into the system."""
    params = {"username": username} if username else {}
    response = client.get("/user/login", params=params)
    response.raise_for_status()
    return response.json()

def logoutUser(client: httpx.Client) -> dict:
    """Logs out current logged in user session."""
    response = client.get("/user/logout")
    response.raise_for_status()
    return response.json()

def getUserByName(client: httpx.Client, username: str) -> dict:
    """Find user by username."""
    response = client.get(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def updateUser(client: httpx.Client, username: str) -> dict:
    """Update user."""
    response = client.put(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def deleteUser(client: httpx.Client, username: str) -> dict:
    """Delete user."""
    response = client.delete(f"/user/{username}")
    response.raise_for_status()
    return response.json()