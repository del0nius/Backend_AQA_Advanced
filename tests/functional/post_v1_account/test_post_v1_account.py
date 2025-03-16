import json
from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi
from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
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

def test_post_v1_account():
    # User registration
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account_api = AccountApi(configuration=dm_api_configuration)
    login_api = LoginApi(configuration=dm_api_configuration)
    mailhog_api = MailhogApi(configuration=mailhog_configuration)

    login = 'd.gaponenko_test36'
    email = f'{login}@mail.ru'
    password = '123456789'
    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = account_api.post_v1_account(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201, f"Couldn't create user {response.json()}"

    # Get email from email server
    response = mailhog_api.get_api_v2_messages()
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't get emails {response.json()}"

    # Get token from email
    token = get_activation_token_by_login(login, response)
    assert token is not None, f"Couldn't get token for user {login}"

    # User activation
    response = account_api.put_v1_account_token(token=token)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't activate user {login}"

    # Sign in
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't sign in user {login}"


def get_activation_token_by_login(
        login,
        response
        ):
    token = None
    for i in response.json()['items']:
        try:
            user_data = json.loads(i['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        except (json.JSONDecodeError, KeyError):
            continue

    return token
