from pydantic import BaseModel
import httpx
import pytest

class GetAccount(BaseModel):
    pass

class PostAccountLinks(BaseModel):
    pass

class PostAccountSessions(BaseModel):
    pass

class GetAccounts(BaseModel):
    pass

class PostAccounts(BaseModel):
    pass

class DeleteAccountsAccount(BaseModel):
    pass

class GetAccountsAccount(BaseModel):
    pass

class PostAccountsAccount(BaseModel):
    pass

class PostAccountsAccountBankAccounts(BaseModel):
    pass

class DeleteAccountsAccountBankAccountsId(BaseModel):
    pass

class GetAccountsAccountBankAccountsId(BaseModel):
    pass

class PostAccountsAccountBankAccountsId(BaseModel):
    pass

class GetAccountsAccountCapabilities(BaseModel):
    pass

class GetAccountsAccountCapabilitiesCapability(BaseModel):
    pass

class PostAccountsAccountCapabilitiesCapability(BaseModel):
    pass

class GetAccountsAccountExternalAccounts(BaseModel):
    pass

class PostAccountsAccountExternalAccounts(BaseModel):
    pass

class DeleteAccountsAccountExternalAccountsId(BaseModel):
    pass

class GetAccountsAccountExternalAccountsId(BaseModel):
    pass

class PostAccountsAccountExternalAccountsId(BaseModel):
    pass

class PostAccountsAccountLoginLinks(BaseModel):
    pass

class GetAccountsAccountPeople(BaseModel):
    pass

class PostAccountsAccountPeople(BaseModel):
    pass

class DeleteAccountsAccountPeoplePerson(BaseModel):
    pass

class GetAccountsAccountPeoplePerson(BaseModel):
    pass

class PostAccountsAccountPeoplePerson(BaseModel):
    pass

class GetAccountsAccountPersons(BaseModel):
    pass

class PostAccountsAccountPersons(BaseModel):
    pass

class DeleteAccountsAccountPersonsPerson(BaseModel):
    pass

class GetAccountsAccountPersonsPerson(BaseModel):
    pass

class PostAccountsAccountPersonsPerson(BaseModel):
    pass

class PostAccountsAccountReject(BaseModel):
    pass

class GetApplePayDomains(BaseModel):
    pass

class PostApplePayDomains(BaseModel):
    pass

class DeleteApplePayDomainsDomain(BaseModel):
    pass

class GetApplePayDomainsDomain(BaseModel):
    pass

class GetApplicationFees(BaseModel):
    pass

class GetApplicationFeesFeeRefundsId(BaseModel):
    pass

class PostApplicationFeesFeeRefundsId(BaseModel):
    pass

class GetApplicationFeesId(BaseModel):
    pass

class PostApplicationFeesIdRefund(BaseModel):
    pass

class GetApplicationFeesIdRefunds(BaseModel):
    pass

class PostApplicationFeesIdRefunds(BaseModel):
    pass

class GetAppsSecrets(BaseModel):
    pass

class PostAppsSecrets(BaseModel):
    pass

@pytest.fixture
def client():
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"
    }
    with httpx.Client(base_url="https://api.stripe.com/", headers=headers) as client:
        yield client

def test_get_account_status(client):
    response = client.get("/v1/account")
    assert response.status_code == 200

def test_get_account_shape(client):
    response = client.get("/v1/account")
    GetAccount.parse_obj(response.json())

def test_post_account_links_status(client):
    response = client.post("/v1/account_links")
    assert response.status_code == 200

def test_post_account_links_shape(client):
    response = client.post("/v1/account_links")
    PostAccountLinks.parse_obj(response.json())

def test_post_account_sessions_status(client):
    response = client.post("/v1/account_sessions")
    assert response.status_code == 200

def test_post_account_sessions_shape(client):
    response = client.post("/v1/account_sessions")
    PostAccountSessions.parse_obj(response.json())

def test_get_accounts_status(client):
    response = client.get("/v1/accounts")
    assert response.status_code == 200

def test_get_accounts_shape(client):
    response = client.get("/v1/accounts")
    GetAccounts.parse_obj(response.json())

def test_post_accounts_status(client):
    response = client.post("/v1/accounts")
    assert response.status_code == 200

def test_post_accounts_shape(client):
    response = client.post("/v1/accounts")
    PostAccounts.parse_obj(response.json())

def test_delete_accounts_account_status(client):
    account_id = "acct_test_id"
    response = client.delete(f"/v1/accounts/{account_id}")
    assert response.status_code == 200

def test_get_accounts_account_status(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}")
    assert response.status_code == 200

def test_get_accounts_account_shape(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}")
    GetAccountsAccount.parse_obj(response.json())

def test_post_accounts_account_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}")
    assert response.status_code == 200

def test_post_accounts_account_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}")
    PostAccountsAccount.parse_obj(response.json())

def test_post_accounts_account_bank_accounts_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/bank_accounts")
    assert response.status_code == 200

def test_post_accounts_account_bank_accounts_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/bank_accounts")
    PostAccountsAccountBankAccounts.parse_obj(response.json())

def test_delete_accounts_account_bank_accounts_id_status(client):
    account_id = "acct_test_id"
    bank_account_id = "ba_test_id"
    response = client.delete(f"/v1/accounts/{account_id}/bank_accounts/{bank_account_id}")
    assert response.status_code == 200

def test_get_accounts_account_bank_accounts_id_status(client):
    account_id = "acct_test_id"
    bank_account_id = "ba_test_id"
    response = client.get(f"/v1/accounts/{account_id}/bank_accounts/{bank_account_id}")
    assert response.status_code == 200

def test_get_accounts_account_bank_accounts_id_shape(client):
    account_id = "acct_test_id"
    bank_account_id = "ba_test_id"
    response = client.get(f"/v1/accounts/{account_id}/bank_accounts/{bank_account_id}")
    GetAccountsAccountBankAccountsId.parse_obj(response.json())

def test_post_accounts_account_bank_accounts_id_status(client):
    account_id = "acct_test_id"
    bank_account_id = "ba_test_id"
    response = client.post(f"/v1/accounts/{account_id}/bank_accounts/{bank_account_id}")
    assert response.status_code == 200

def test_post_accounts_account_bank_accounts_id_shape(client):
    account_id = "acct_test_id"
    bank_account_id = "ba_test_id"
    response = client.post(f"/v1/accounts/{account_id}/bank_accounts/{bank_account_id}")
    PostAccountsAccountBankAccountsId.parse_obj(response.json())

def test_get_accounts_account_capabilities_status(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/capabilities")
    assert response.status_code == 200

def test_get_accounts_account_capabilities_shape(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/capabilities")
    GetAccountsAccountCapabilities.parse_obj(response.json())

def test_get_accounts_account_capabilities_capability_status(client):
    account_id = "acct_test_id"
    capability = "capability_test"
    response = client.get(f"/v1/accounts/{account_id}/capabilities/{capability}")
    assert response.status_code == 200

def test_get_accounts_account_capabilities_capability_shape(client):
    account_id = "acct_test_id"
    capability = "capability_test"
    response = client.get(f"/v1/accounts/{account_id}/capabilities/{capability}")
    GetAccountsAccountCapabilitiesCapability.parse_obj(response.json())

def test_post_accounts_account_capabilities_capability_status(client):
    account_id = "acct_test_id"
    capability = "capability_test"
    response = client.post(f"/v1/accounts/{account_id}/capabilities/{capability}")
    assert response.status_code == 200

def test_post_accounts_account_capabilities_capability_shape(client):
    account_id = "acct_test_id"
    capability = "capability_test"
    response = client.post(f"/v1/accounts/{account_id}/capabilities/{capability}")
    PostAccountsAccountCapabilitiesCapability.parse_obj(response.json())

def test_get_accounts_account_external_accounts_status(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/external_accounts")
    assert response.status_code == 200

def test_get_accounts_account_external_accounts_shape(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/external_accounts")
    GetAccountsAccountExternalAccounts.parse_obj(response.json())

def test_post_accounts_account_external_accounts_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/external_accounts")
    assert response.status_code == 200

def test_post_accounts_account_external_accounts_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/external_accounts")
    PostAccountsAccountExternalAccounts.parse_obj(response.json())

def test_delete_accounts_account_external_accounts_id_status(client):
    account_id = "acct_test_id"
    external_account_id = "ext_test_id"
    response = client.delete(f"/v1/accounts/{account_id}/external_accounts/{external_account_id}")
    assert response.status_code == 200

def test_get_accounts_account_external_accounts_id_status(client):
    account_id = "acct_test_id"
    external_account_id = "ext_test_id"
    response = client.get(f"/v1/accounts/{account_id}/external_accounts/{external_account_id}")
    assert response.status_code == 200

def test_get_accounts_account_external_accounts_id_shape(client):
    account_id = "acct_test_id"
    external_account_id = "ext_test_id"
    response = client.get(f"/v1/accounts/{account_id}/external_accounts/{external_account_id}")
    GetAccountsAccountExternalAccountsId.parse_obj(response.json())

def test_post_accounts_account_external_accounts_id_status(client):
    account_id = "acct_test_id"
    external_account_id = "ext_test_id"
    response = client.post(f"/v1/accounts/{account_id}/external_accounts/{external_account_id}")
    assert response.status_code == 200

def test_post_accounts_account_external_accounts_id_shape(client):
    account_id = "acct_test_id"
    external_account_id = "ext_test_id"
    response = client.post(f"/v1/accounts/{account_id}/external_accounts/{external_account_id}")
    PostAccountsAccountExternalAccountsId.parse_obj(response.json())

def test_post_accounts_account_login_links_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/login_links")
    assert response.status_code == 200

def test_post_accounts_account_login_links_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/login_links")
    PostAccountsAccountLoginLinks.parse_obj(response.json())

def test_get_accounts_account_people_status(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/people")
    assert response.status_code == 200

def test_get_accounts_account_people_shape(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/people")
    GetAccountsAccountPeople.parse_obj(response.json())

def test_post_accounts_account_people_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/people")
    assert response.status_code == 200

def test_post_accounts_account_people_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/people")
    PostAccountsAccountPeople.parse_obj(response.json())

def test_delete_accounts_account_people_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.delete(f"/v1/accounts/{account_id}/people/{person_id}")
    assert response.status_code == 200

def test_get_accounts_account_people_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.get(f"/v1/accounts/{account_id}/people/{person_id}")
    assert response.status_code == 200

def test_get_accounts_account_people_person_shape(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.get(f"/v1/accounts/{account_id}/people/{person_id}")
    GetAccountsAccountPeoplePerson.parse_obj(response.json())

def test_post_accounts_account_people_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.post(f"/v1/accounts/{account_id}/people/{person_id}")
    assert response.status_code == 200

def test_post_accounts_account_people_person_shape(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.post(f"/v1/accounts/{account_id}/people/{person_id}")
    PostAccountsAccountPeoplePerson.parse_obj(response.json())

def test_get_accounts_account_persons_status(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/persons")
    assert response.status_code == 200

def test_get_accounts_account_persons_shape(client):
    account_id = "acct_test_id"
    response = client.get(f"/v1/accounts/{account_id}/persons")
    GetAccountsAccountPersons.parse_obj(response.json())

def test_post_accounts_account_persons_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/persons")
    assert response.status_code == 200

def test_post_accounts_account_persons_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/persons")
    PostAccountsAccountPersons.parse_obj(response.json())

def test_delete_accounts_account_persons_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.delete(f"/v1/accounts/{account_id}/persons/{person_id}")
    assert response.status_code == 200

def test_get_accounts_account_persons_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.get(f"/v1/accounts/{account_id}/persons/{person_id}")
    assert response.status_code == 200

def test_get_accounts_account_persons_person_shape(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.get(f"/v1/accounts/{account_id}/persons/{person_id}")
    GetAccountsAccountPersonsPerson.parse_obj(response.json())

def test_post_accounts_account_persons_person_status(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.post(f"/v1/accounts/{account_id}/persons/{person_id}")
    assert response.status_code == 200

def test_post_accounts_account_persons_person_shape(client):
    account_id = "acct_test_id"
    person_id = "person_test_id"
    response = client.post(f"/v1/accounts/{account_id}/persons/{person_id}")
    PostAccountsAccountPersonsPerson.parse_obj(response.json())

def test_post_accounts_account_reject_status(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/reject")
    assert response.status_code == 200

def test_post_accounts_account_reject_shape(client):
    account_id = "acct_test_id"
    response = client.post(f"/v1/accounts/{account_id}/reject")
    PostAccountsAccountReject.parse_obj(response.json())

def test_get_apple_pay_domains_status(client):
    response = client.get("/v1/apple_pay/domains")
    assert response.status_code == 200

def test_get_apple_pay_domains_shape(client):
    response = client.get("/v1/apple_pay/domains")
    GetApplePayDomains.parse_obj(response.json())

def test_post_apple_pay_domains_status(client):
    response = client.post("/v1/apple_pay/domains")
    assert response.status_code == 200

def test_post_apple_pay_domains_shape(client):
    response = client.post("/v1/apple_pay/domains")
    PostApplePayDomains.parse_obj(response.json())

def test_delete_apple_pay_domains_domain_status(client):
    domain = "example.com"
    response = client.delete(f"/v1/apple_pay/domains/{domain}")
    assert response.status_code == 200

def test_get_apple_pay_domains_domain_status(client):
    domain = "example.com"
    response = client.get(f"/v1/apple_pay/domains/{domain}")
    assert response.status_code == 200

def test_get_apple_pay_domains_domain_shape(client):
    domain = "example.com"
    response = client.get(f"/v1/apple_pay/domains/{domain}")
    GetApplePayDomainsDomain.parse_obj(response.json())

def test_get_application_fees_status(client):
    response = client.get("/v1/application_fees")
    assert response.status_code == 200

def test_get_application_fees_shape(client):
    response = client.get("/v1/application_fees")
    GetApplicationFees.parse_obj(response.json())

def test_get_application_fees_fee_refunds_id_status(client):
    fee_id = "fee_test_id"
    refund_id = "refund_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}/refunds/{refund_id}")
    assert response.status_code == 200

def test_get_application_fees_fee_refunds_id_shape(client):
    fee_id = "fee_test_id"
    refund_id = "refund_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}/refunds/{refund_id}")
    GetApplicationFeesFeeRefundsId.parse_obj(response.json())

def test_post_application_fees_fee_refunds_id_status(client):
    fee_id = "fee_test_id"
    refund_id = "refund_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refunds/{refund_id}")
    assert response.status_code == 200

def test_post_application_fees_fee_refunds_id_shape(client):
    fee_id = "fee_test_id"
    refund_id = "refund_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refunds/{refund_id}")
    PostApplicationFeesFeeRefundsId.parse_obj(response.json())

def test_get_application_fees_id_status(client):
    fee_id = "fee_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}")
    assert response.status_code == 200

def test_get_application_fees_id_shape(client):
    fee_id = "fee_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}")
    GetApplicationFeesId.parse_obj(response.json())

def test_post_application_fees_id_refund_status(client):
    fee_id = "fee_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refund")
    assert response.status_code == 200

def test_post_application_fees_id_refund_shape(client):
    fee_id = "fee_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refund")
    PostApplicationFeesIdRefund.parse_obj(response.json())

def test_get_application_fees_id_refunds_status(client):
    fee_id = "fee_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}/refunds")
    assert response.status_code == 200

def test_get_application_fees_id_refunds_shape(client):
    fee_id = "fee_test_id"
    response = client.get(f"/v1/application_fees/{fee_id}/refunds")
    GetApplicationFeesIdRefunds.parse_obj(response.json())

def test_post_application_fees_id_refunds_status(client):
    fee_id = "fee_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refunds")
    assert response.status_code == 200

def test_post_application_fees_id_refunds_shape(client):
    fee_id = "fee_test_id"
    response = client.post(f"/v1/application_fees/{fee_id}/refunds")
    PostApplicationFeesIdRefunds.parse_obj(response.json())

def test_get_apps_secrets_status(client):
    response = client.get("/v1/apps/secrets")
    assert response.status_code == 200

def test_get_apps_secrets_shape(client):
    response = client.get("/v1/apps/secrets")
    GetAppsSecrets.parse_obj(response.json())

def test_post_apps_secrets_status(client):
    response = client.post("/v1/apps/secrets")
    assert response.status_code == 200

def test_post_apps_secrets_shape(client):
    response = client.post("/v1/apps/secrets")
    PostAppsSecrets.parse_obj(response.json())