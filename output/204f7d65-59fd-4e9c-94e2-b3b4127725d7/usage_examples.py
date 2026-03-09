import httpx
from client_stubs import get_client, GetAccount, PostAccountLinks, GetAccounts, PostAccounts, DeleteAccountsAccount

TOKEN = "your_api_token_here"

def main():
    client = get_client(TOKEN)

    # Example call to GetAccount
    try:
        account_info = GetAccount(client)
        print("Account Info:", account_info)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error: Account not found.")
        elif e.response.status_code == 401:
            print("Error: Unauthorized access.")
        else:
            print("An error occurred:", e)

    # Example call to PostAccountLinks
    try:
        account_link = PostAccountLinks(client)
        print("Account Link:", account_link)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error: Account link not found.")
        elif e.response.status_code == 401:
            print("Error: Unauthorized access.")
        else:
            print("An error occurred:", e)

    # Example call to GetAccounts
    try:
        accounts = GetAccounts(client)
        print("Accounts:", accounts)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error: Accounts not found.")
        elif e.response.status_code == 401:
            print("Error: Unauthorized access.")
        else:
            print("An error occurred:", e)

    # Example call to PostAccounts
    try:
        new_account = PostAccounts(client)
        print("New Account:", new_account)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error: Unable to create account.")
        elif e.response.status_code == 401:
            print("Error: Unauthorized access.")
        else:
            print("An error occurred:", e)

    # Example call to DeleteAccountsAccount
    account_id = "acct_123456789"
    try:
        deleted_account = DeleteAccountsAccount(client, account_id)
        print("Deleted Account:", deleted_account)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Error: Account not found for deletion.")
        elif e.response.status_code == 401:
            print("Error: Unauthorized access.")
        else:
            print("An error occurred:", e)

if __name__ == "__main__":
    main()