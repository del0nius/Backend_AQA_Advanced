import requests

def test_post_v1_account():
    login = 'd.gaponenko_test'
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

    # Get email from email server
    params = {
        'limit': '50',
    }

    response = requests.get('http://5.63.153.31:5025/api/v2/messages', params=params, verify=False)
    print(response.status_code)
    print(response.text)

    # Get token from email
    ...

    # User activation
    headers = {
        'accept': 'text/plain',
    }

    response = requests.put('http://5.63.153.31:5051/v1/account/79a2f11c-d0b4-49bf-9ebc-694612b310a8', headers=headers)
    print(response.status_code)
    print(response.text)

    # Sign in
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = requests.post('http://5.63.153.31:5051/v1/account/login', json=json_data)
    print(response.status_code)
    print(response.text)
