import json
import time

from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
from retrying import retry


def retry_if_result_none(
        result
        ):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retryer(
        func
):
    def wrapper(
            *args,
            **kwargs
    ):
        token = None
        count = 0
        while token is None:
            print(f"Attempt №{count} to obtain an activation token")
            token = func(*args, **kwargs)
            count += 1
            if count == 5:
                raise AssertionError("Exceeded number of attempts to obtain an activation token")
            if token:
                return token
            time.sleep(1)

    return wrapper


class AccountHelper:
    def __init__(
            self,
            dm_account_api: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def auth_client(
            self,
            login: str,
            password: str
    ):
        response = self.dm_account_api.login_api.post_v1_account_login(
            json_data={"login": login, "password": password}
        )
        token = {
            "x-dm-auth-token": response.headers["x-dm-auth-token"]
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Couldn't create user {response.json()}"
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f"Couldn't get token for user {login}"
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, f"Couldn't activate user {login}"
        return response

    def user_login(
            self,
            login: str,
            password: str,
            expected_status_code: int = 200,
            remember_me: bool = True
    ):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me,
        }

        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == expected_status_code, f"Expected {expected_status_code}, but got {response.status_code} for user {login}"
        return response

    # option with retrying lib
    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none, wait_fixed=1000)
    def find_activation_token_from_mail(
            self,
            new_email: str
    ):

        # Get emails from the mail server
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, f"Couldn't get emails {response.json()}"

        # Find the activation token from the response
        activation_token = self.get_activation_token_by_new_email(new_email, response)
        assert activation_token is not None, f"Couldn't get token for email {new_email}"

        return activation_token

    # option with self-created decorator
    @retryer
    def get_activation_token_by_login(
            self,
            login,
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for i in response.json()['items']:
            try:
                user_data = json.loads(i['Content']['Body'])
                user_login = user_data['Login']
                if user_login == login:
                    token = user_data['ConfirmationLinkUrl'].split('/')[-1]
            except (json.JSONDecodeError, KeyError):
                continue
        return token

    @staticmethod
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
