import httpx

def get_client(token: str) -> httpx.Client:
    """Returns an authenticated httpx.Client with the provided token."""
    return httpx.Client(base_url="https://api.stripe.com/", headers={"Authorization": f"Bearer {token}"})

def GetAccount(client: httpx.Client, expand: str = None) -> dict:
    """Retrieves the account information."""
    params = {"expand": expand} if expand else None
    response = client.get("/v1/account", params=params)
    response.raise_for_status()
    return response.json()

def PostAccountLinks(client: httpx.Client) -> dict:
    """Creates an account link."""
    response = client.post("/v1/account_links")
    response.raise_for_status()
    return response.json()

def PostAccountSessions(client: httpx.Client) -> dict:
    """Creates an account session."""
    response = client.post("/v1/account_sessions")
    response.raise_for_status()
    return response.json()

def GetAccounts(client: httpx.Client, created: str = None) -> dict:
    """Retrieves a list of accounts."""
    params = {"created": created} if created else None
    response = client.get("/v1/accounts", params=params)
    response.raise_for_status()
    return response.json()

def PostAccounts(client: httpx.Client) -> dict:
    """Creates a new account."""
    response = client.post("/v1/accounts")
    response.raise_for_status()
    return response.json()

def DeleteAccountsAccount(client: httpx.Client, account: str) -> dict:
    """Deletes an account."""
    response = client.delete(f"/v1/accounts/{account}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccount(client: httpx.Client, account: str) -> dict:
    """Retrieves an account by its ID."""
    response = client.get(f"/v1/accounts/{account}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccount(client: httpx.Client, account: str) -> dict:
    """Updates an account."""
    response = client.post(f"/v1/accounts/{account}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountBankAccounts(client: httpx.Client, account: str) -> dict:
    """Adds a bank account to an account."""
    response = client.post(f"/v1/accounts/{account}/bank_accounts")
    response.raise_for_status()
    return response.json()

def DeleteAccountsAccountBankAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Deletes a bank account from an account."""
    response = client.delete(f"/v1/accounts/{account}/bank_accounts/{id}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountBankAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Retrieves a bank account by its ID."""
    response = client.get(f"/v1/accounts/{account}/bank_accounts/{id}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountBankAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Updates a bank account."""
    response = client.post(f"/v1/accounts/{account}/bank_accounts/{id}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountCapabilities(client: httpx.Client, account: str) -> dict:
    """Retrieves the capabilities of an account."""
    response = client.get(f"/v1/accounts/{account}/capabilities")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountCapabilitiesCapability(client: httpx.Client, account: str, capability: str) -> dict:
    """Retrieves a specific capability of an account."""
    response = client.get(f"/v1/accounts/{account}/capabilities/{capability}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountCapabilitiesCapability(client: httpx.Client, account: str, capability: str) -> dict:
    """Updates a specific capability of an account."""
    response = client.post(f"/v1/accounts/{account}/capabilities/{capability}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountExternalAccounts(client: httpx.Client, account: str) -> dict:
    """Retrieves external accounts of an account."""
    response = client.get(f"/v1/accounts/{account}/external_accounts")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountExternalAccounts(client: httpx.Client, account: str) -> dict:
    """Adds an external account to an account."""
    response = client.post(f"/v1/accounts/{account}/external_accounts")
    response.raise_for_status()
    return response.json()

def DeleteAccountsAccountExternalAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Deletes an external account from an account."""
    response = client.delete(f"/v1/accounts/{account}/external_accounts/{id}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountExternalAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Retrieves an external account by its ID."""
    response = client.get(f"/v1/accounts/{account}/external_accounts/{id}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountExternalAccountsId(client: httpx.Client, account: str, id: str) -> dict:
    """Updates an external account."""
    response = client.post(f"/v1/accounts/{account}/external_accounts/{id}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountLoginLinks(client: httpx.Client, account: str) -> dict:
    """Creates a login link for an account."""
    response = client.post(f"/v1/accounts/{account}/login_links")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountPeople(client: httpx.Client, account: str) -> dict:
    """Retrieves people associated with an account."""
    response = client.get(f"/v1/accounts/{account}/people")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountPeople(client: httpx.Client, account: str) -> dict:
    """Adds a person to an account."""
    response = client.post(f"/v1/accounts/{account}/people")
    response.raise_for_status()
    return response.json()

def DeleteAccountsAccountPeoplePerson(client: httpx.Client, account: str, person: str) -> dict:
    """Deletes a person from an account."""
    response = client.delete(f"/v1/accounts/{account}/people/{person}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountPeoplePerson(client: httpx.Client, account: str, person: str) -> dict:
    """Retrieves a person by their ID."""
    response = client.get(f"/v1/accounts/{account}/people/{person}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountPeoplePerson(client: httpx.Client, account: str, person: str) -> dict:
    """Updates a person."""
    response = client.post(f"/v1/accounts/{account}/people/{person}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountPersons(client: httpx.Client, account: str) -> dict:
    """Retrieves persons associated with an account."""
    response = client.get(f"/v1/accounts/{account}/persons")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountPersons(client: httpx.Client, account: str) -> dict:
    """Adds a person to an account."""
    response = client.post(f"/v1/accounts/{account}/persons")
    response.raise_for_status()
    return response.json()

def DeleteAccountsAccountPersonsPerson(client: httpx.Client, account: str, person: str) -> dict:
    """Deletes a person from an account."""
    response = client.delete(f"/v1/accounts/{account}/persons/{person}")
    response.raise_for_status()
    return response.json()

def GetAccountsAccountPersonsPerson(client: httpx.Client, account: str, person: str) -> dict:
    """Retrieves a person by their ID."""
    response = client.get(f"/v1/accounts/{account}/persons/{person}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountPersonsPerson(client: httpx.Client, account: str, person: str) -> dict:
    """Updates a person."""
    response = client.post(f"/v1/accounts/{account}/persons/{person}")
    response.raise_for_status()
    return response.json()

def PostAccountsAccountReject(client: httpx.Client, account: str) -> dict:
    """Rejects an account."""
    response = client.post(f"/v1/accounts/{account}/reject")
    response.raise_for_status()
    return response.json()

def GetApplePayDomains(client: httpx.Client, domain_name: str = None) -> dict:
    """Retrieves a list of Apple Pay domains."""
    params = {"domain_name": domain_name} if domain_name else None
    response = client.get("/v1/apple_pay/domains", params=params)
    response.raise_for_status()
    return response.json()

def PostApplePayDomains(client: httpx.Client) -> dict:
    """Creates a new Apple Pay domain."""
    response = client.post("/v1/apple_pay/domains")
    response.raise_for_status()
    return response.json()

def DeleteApplePayDomainsDomain(client: httpx.Client, domain: str) -> dict:
    """Deletes an Apple Pay domain."""
    response = client.delete(f"/v1/apple_pay/domains/{domain}")
    response.raise_for_status()
    return response.json()

def GetApplePayDomainsDomain(client: httpx.Client, domain: str) -> dict:
    """Retrieves an Apple Pay domain by its ID."""
    response = client.get(f"/v1/apple_pay/domains/{domain}")
    response.raise_for_status()
    return response.json()

def GetApplicationFees(client: httpx.Client, charge: str = None) -> dict:
    """Retrieves a list of application fees."""
    params = {"charge": charge} if charge else None
    response = client.get("/v1/application_fees", params=params)
    response.raise_for_status()
    return response.json()

def GetApplicationFeesFeeRefundsId(client: httpx.Client, fee: str, id: str) -> dict:
    """Retrieves a refund for a specific application fee."""
    response = client.get(f"/v1/application_fees/{fee}/refunds/{id}")
    response.raise_for_status()
    return response.json()

def PostApplicationFeesFeeRefundsId(client: httpx.Client, fee: str, id: str) -> dict:
    """Creates a refund for a specific application fee."""
    response = client.post(f"/v1/application_fees/{fee}/refunds/{id}")
    response.raise_for_status()
    return response.json()

def GetApplicationFeesId(client: httpx.Client, id: str) -> dict:
    """Retrieves a specific application fee by its ID."""
    response = client.get(f"/v1/application_fees/{id}")
    response.raise_for_status()
    return response.json()

def PostApplicationFeesIdRefund(client: httpx.Client, id: str) -> dict:
    """Creates a refund for a specific application fee."""
    response = client.post(f"/v1/application_fees/{id}/refund")
    response.raise_for_status()
    return response.json()

def GetApplicationFeesIdRefunds(client: httpx.Client, id: str, ending_before: str = None) -> dict:
    """Retrieves a list of refunds for a specific application fee."""
    params = {"ending_before": ending_before} if ending_before else None
    response = client.get(f"/v1/application_fees/{id}/refunds", params=params)
    response.raise_for_status()
    return response.json()

def PostApplicationFeesIdRefunds(client: httpx.Client, id: str) -> dict:
    """Creates a refund for a specific application fee."""
    response = client.post(f"/v1/application_fees/{id}/refunds")
    response.raise_for_status()
    return response.json()

def GetAppsSecrets(client: httpx.Client, ending_before: str = None) -> dict:
    """Retrieves a list of app secrets."""
    params = {"ending_before": ending_before} if ending_before else None
    response = client.get("/v1/apps/secrets", params=params)
    response.raise_for_status()
    return response.json()

def PostAppsSecrets(client: httpx.Client) -> dict:
    """Creates a new app secret."""
    response = client.post("/v1/apps/secrets")
    response.raise_for_status()
    return response.json()