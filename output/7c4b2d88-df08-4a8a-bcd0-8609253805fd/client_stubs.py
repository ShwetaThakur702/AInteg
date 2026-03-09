import httpx

BASE_URL = "/api/v3"

def get_client(token: str) -> httpx.Client:
    """
    Returns an authenticated httpx.Client with the provided OAuth token.

    Args:
        token (str): The OAuth token for authentication.

    Returns:
        httpx.Client: An authenticated HTTP client.
    """
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.Client(base_url=BASE_URL, headers=headers)

def updatePet(client: httpx.Client) -> dict:
    """
    Updates an existing pet.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.put("/pet")
    response.raise_for_status()
    return response.json()

def addPet(client: httpx.Client) -> dict:
    """
    Adds a new pet to the store.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post("/pet")
    response.raise_for_status()
    return response.json()

def findPetsByStatus(client: httpx.Client, status: str = None) -> dict:
    """
    Finds pets by their status.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        status (str, optional): Status of the pets to find. Defaults to None.

    Returns:
        dict: The response JSON from the API.
    """
    params = {"status": status} if status else {}
    response = client.get("/pet/findByStatus", params=params)
    response.raise_for_status()
    return response.json()

def findPetsByTags(client: httpx.Client, tags: str = None) -> dict:
    """
    Finds pets by their tags.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        tags (str, optional): Tags of the pets to find. Defaults to None.

    Returns:
        dict: The response JSON from the API.
    """
    params = {"tags": tags} if tags else {}
    response = client.get("/pet/findByTags", params=params)
    response.raise_for_status()
    return response.json()

def getPetById(client: httpx.Client, petId: int) -> dict:
    """
    Finds a pet by its ID.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        petId (int): The ID of the pet to find.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.get(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def updatePetWithForm(client: httpx.Client, petId: int) -> dict:
    """
    Updates a pet with form data.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        petId (int): The ID of the pet to update.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def deletePet(client: httpx.Client, petId: int) -> dict:
    """
    Deletes a pet by its ID.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        petId (int): The ID of the pet to delete.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.delete(f"/pet/{petId}")
    response.raise_for_status()
    return response.json()

def uploadFile(client: httpx.Client, petId: int) -> dict:
    """
    Uploads an image for a pet.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        petId (int): The ID of the pet to upload the image for.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post(f"/pet/{petId}/uploadImage")
    response.raise_for_status()
    return response.json()

def getInventory(client: httpx.Client) -> dict:
    """
    Gets the inventory of pets.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.get("/store/inventory")
    response.raise_for_status()
    return response.json()

def placeOrder(client: httpx.Client) -> dict:
    """
    Places an order for a pet.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post("/store/order")
    response.raise_for_status()
    return response.json()

def getOrderById(client: httpx.Client, orderId: int) -> dict:
    """
    Gets an order by its ID.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        orderId (int): The ID of the order to retrieve.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.get(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def deleteOrder(client: httpx.Client, orderId: int) -> dict:
    """
    Deletes an order by its ID.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        orderId (int): The ID of the order to delete.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.delete(f"/store/order/{orderId}")
    response.raise_for_status()
    return response.json()

def createUser(client: httpx.Client) -> dict:
    """
    Creates a new user.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post("/user")
    response.raise_for_status()
    return response.json()

def createUsersWithListInput(client: httpx.Client) -> dict:
    """
    Creates multiple users with a list input.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.post("/user/createWithList")
    response.raise_for_status()
    return response.json()

def loginUser(client: httpx.Client, username: str = None) -> dict:
    """
    Logs in a user.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        username (str, optional): The username of the user to log in. Defaults to None.

    Returns:
        dict: The response JSON from the API.
    """
    params = {"username": username} if username else {}
    response = client.get("/user/login", params=params)
    response.raise_for_status()
    return response.json()

def logoutUser(client: httpx.Client) -> dict:
    """
    Logs out the current logged-in user.

    Args:
        client (httpx.Client): The authenticated HTTP client.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.get("/user/logout")
    response.raise_for_status()
    return response.json()

def getUserByName(client: httpx.Client, username: str) -> dict:
    """
    Gets a user by their username.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        username (str): The username of the user to retrieve.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.get(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def updateUser(client: httpx.Client, username: str) -> dict:
    """
    Updates a user by their username.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        username (str): The username of the user to update.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.put(f"/user/{username}")
    response.raise_for_status()
    return response.json()

def deleteUser(client: httpx.Client, username: str) -> dict:
    """
    Deletes a user by their username.

    Args:
        client (httpx.Client): The authenticated HTTP client.
        username (str): The username of the user to delete.

    Returns:
        dict: The response JSON from the API.
    """
    response = client.delete(f"/user/{username}")
    response.raise_for_status()
    return response.json()