import requests
from json import loads

def test_post_v1_account():
    login = 'd.gaponenko_test6'
    email = f'{login}@mail.ru'
    password = '123456789'

    # User registration
    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = requests.post('http://5.63.153.31:5051/v1/account', json=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201, f"Couldn't create user {response.json()}"

    # Get email from email server
    params = {
        'limit': '50',
    }

    response = requests.get('http://5.63.153.31:5025/api/v2/messages', params=params, verify=False)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't get emails {response.json}"

    # Get token from email
    token = None
    for i in response.json()['items']:
        user_data = (loads(i['Content']['Body']))
        user_login = user_data['Login']
        if user_login == login:
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
    assert token is not None, f"Couldn't get token for user {login}"

    # User activation
    headers = {
        'accept': 'text/plain',
    }

    response = requests.put(f'http://5.63.153.31:5051/v1/account/{token}', headers=headers)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't activate user {login}"

    # Sign in
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = requests.post('http://5.63.153.31:5051/v1/account/login', json=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, f"Couldn't sign in user {login}"
