import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from azure.identity import ClientSecretCredential
from pydantic import SecretStr

load_dotenv()

def llm_initialization() -> AzureChatOpenAI:
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    token = credential.get_token(os.environ["AZURE_TOKEN_SCOPE"])

    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        api_key=SecretStr(token.token),
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        temperature=0.2,
    )

if __name__ == "__main__":
    llm = llm_initialization()
    print(llm.invoke("How's your day?").content)
