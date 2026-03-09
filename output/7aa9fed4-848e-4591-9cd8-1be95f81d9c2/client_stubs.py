import httpx

BASE_URL = "/api/v3"

def get_client(token: str) -> httpx.Client:
    """Returns an authenticated httpx.Client with the provided OAuth token."""
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.Client(base_url=BASE_URL, headers=headers)

def updatePet(client: httpx.Client) -> dict:
    """Updates an existing pet."""
    response = client.put("/pet")
    response.raise_for_status()
    return response.json()

def addPet(client: httpx.Client) -> dict:
    """Adds a new pet to the store."""
    response = client.post("/pet")
    response.raise_for_status()
    return response.json()

def findPetsByStatus(client: httpx.Client, status: str = None) -> dict:
    """Finds pets by their status."""
    response = client.get("/pet/findByStatus", params={"status": status})
    response.raise_for_status()
    return response.json()

def findPetsByTags(client: httpx.Client, tags: str = None) -> dict:
    """Finds pets by their tags."""
    response = client.get("/pet/findByTags", params={"tags": tags})
    response.raise_for_status()
    return response.json()

def getPetById(client: httpx.Client, petId: int) -> dict:
    """Finds a pet by its ID."""
    response = client.get(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def updatePetWithForm(client: httpx.Client, petId: int) -> dict:
    """Updates a pet with form data."""
    response = client.post(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def deletePet(client: httpx.Client, petId: int) -> dict:
    """Deletes a pet by its ID."""
    response = client.delete(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def uploadFile(client: httpx.Client, petId: int) -> dict:
    """Uploads an image for a pet."""
    response = client.post(f"/pet/{petId}/uploadImage")
    response.raise_for_status()
    return response.json()

def getInventory(client: httpx.Client) -> dict:
    """Gets the inventory of pets."""
    response = client.get("/store/inventory")
    response.raise_for_status()
    return response.json()

def placeOrder(client: httpx.Client) -> dict:
    """Places a new order."""
    response = client.post("/store/order")
    response.raise_for_status()
    return response.json()

def getOrderById(client: httpx.Client, orderId: int) -> dict:
    """Finds an order by its ID."""
    response = client.get(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def deleteOrder(client: httpx.Client, orderId: int) -> dict:
    """Deletes an order by its ID."""
    response = client.delete(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def createUser(client: httpx.Client) -> dict:
    """Creates a new user."""
    response = client.post("/user")
    response.raise_for_status()
    return response.json()

def createUsersWithListInput(client: httpx.Client) -> dict:
    """Creates multiple users with a list input."""
    response = client.post("/user/createWithList")
    response.raise_for_status()
    return response.json()

def loginUser(client: httpx.Client, username: str = None) -> dict:
    """Logs in a user."""
    response = client.get("/user/login", params={"username": username})
    response.raise_for_status()
    return response.json()

def logoutUser(client: httpx.Client) -> dict:
    """Logs out the current user."""
    response = client.get("/user/logout")
    response.raise_for_status()
    return response.json()

def getUserByName(client: httpx.Client, username: str) -> dict:
    """Finds a user by their username."""
    response = client.get(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def updateUser(client: httpx.Client, username: str) -> dict:
    """Updates a user by their username."""
    response = client.put(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def deleteUser(client: httpx.Client, username: str) -> dict:
    """Deletes a user by their username."""
    response = client.delete(f"/user/{username}")
    response.raise_for_status()
    return response.json()