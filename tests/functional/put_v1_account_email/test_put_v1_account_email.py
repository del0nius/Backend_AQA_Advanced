import json
import time
from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi
from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
from helpers.account_helper import AccountHelper
from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
import structlog

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(
            indent=4,
            ensure_ascii=True,
            # sort_keys=True
        )
    ]
)

def test_put_v1_account_email():
    # Sign in after changing an email of a registered user
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account = DMApiAccount(configuration=dm_api_configuration)
    mailhog = MailHogApi(configuration=mailhog_configuration)
    account_helper = AccountHelper(dm_account_api=account, mailhog=mailhog)

    account_api = AccountApi(configuration=dm_api_configuration)
    login_api = LoginApi(configuration=dm_api_configuration)
    mailhog_api = MailhogApi(configuration=mailhog_configuration)

    login = 'd.gaponenko_test58'
    email = f'{login}@mail.ru'
    new_email = f'd{login}@mail.ru'
    password = '123456789'
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)

    # Change an email of a registered user (adding additional 'd' to original email)
    json_data = {
        'login': login,
        'email': new_email,
        'password': password,
    }

    response = account_api.put_v1_account_email(json_data=json_data)
    assert response.status_code == 200, f"Couldn't change email of user {login}"

    # Sign in with inactive user (expect code 403)
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 403, f"Didn't get code 403"

    # Get new email from email server (after changing users email), wait 3 seconds before execution to ensure that email is received
    time.sleep(3)
    response = mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, f"Couldn't get emails {response.json()}"

    # Get new token from new user's email
    new_token = get_activation_token_by_new_email(new_email, response)
    assert new_token is not None, f"Couldn't get token for user with email {new_email}"

    # User activation with new token
    response = account_api.put_v1_account_token(token=new_token)
    assert response.status_code == 200, f"Couldn't activate user {login}"

    # Sign in after user activation
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, f"Couldn't sign in user {login}"

def get_activation_token_by_new_email(
        new_email,
        response
        ):
    new_token = None
    for i in response.json()['items']:
        try:
            user_data = json.loads(i['Content']['Body'])
            user_email = i['Content']['Headers']['To'][0]
            if user_email == new_email:
                new_token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        except (json.JSONDecodeError, KeyError):
            continue
    return new_token