from typing import Any, Dict

import jwt
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from service import settings


class LoginTestCase(TestCase):
    def setUp(self) -> None:
        self.username = 'testing_login_usernamme'
        self.password = 'testing_login_password'

        user = User(
            email='test@test.com',
            first_name='Testing',
            last_name='Testing',
            username=self.username
        )
        user.set_password(self.password)
        user.save()

        self.user = user

    def _api_login(self, username: str, password: str, expected_code: int) -> Dict[str, Any]:
        client = APIClient()
        response = client.post(
            '/api/token/',
            {'username': username, 'password': password},
            format='json'
        )

        self.assertEqual(response.status_code, expected_code)
        return response.json()

    def test_get_jwt_token_ok(self) -> None:
        data = self._api_login(self.username, self.password, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertIn('refresh', data)
        self.assertIn('access', data)

        token = data['access']
        header_data = jwt.get_unverified_header(token)

        jwt_decoded = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[header_data['alg']])
        self.assertEqual(jwt_decoded['token_type'], 'access')
        self.assertEqual(jwt_decoded['user_id'], self.user.id)

    def test_get_jwt_token_invalid_username(self) -> None:
        invalid_username = self.username + '_invalid'

        data = self._api_login(invalid_username, self.username, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(data), 1)
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'No active account found with the given credentials')

    def test_get_jwt_token_invalid_password(self) -> None:
        invalid_password = self.password + '_invalid'

        data = self._api_login(self.username, invalid_password, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(data), 1)
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'No active account found with the given credentials')
