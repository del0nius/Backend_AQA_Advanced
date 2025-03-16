import json
from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi


def test_put_v1_account_email():
    account_api = AccountApi(host='http://5.63.153.31:5051')
    login_api = LoginApi(host='http://5.63.153.31:5051')
    mailhog_api = MailhogApi(host='http://5.63.153.31:5025')
    login = 'd.gaponenko_test31'
    email = f'{login}@mail.ru'
    new_email = f'd{login}@mail.ru'
    password = '123456789'
    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    # User registration
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

    # Change an email of a registered user (adding additional 'd' to original email)
    json_data = {
        'login': login,
        'email': new_email,
        'password': password,
    }

    response = account_api.put_v1_account_email(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't change email of user {login}"

    # Sign in with inactive user (expect code 403)
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 403, f"Didn't get code 403"

    # Get new email from email server (after changing users email)
    response = mailhog_api.get_api_v2_messages()
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't get emails {response.json()}"

    # Get new token from new user's email
    new_token = get_activation_token_by_new_email(new_email, response)
    assert new_token is not None, f"Couldn't get token for user with email {new_email}"

    # User activation with new token
    response = account_api.put_v1_account_token(token=new_token)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't activate user {login}"

    # Sign in after user activation
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