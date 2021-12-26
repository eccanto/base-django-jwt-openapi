from abc import ABC
from typing import Any, Dict, Union

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class BaseApiTestCase(ABC, TestCase):
    _DEFAULT_API_CREDS = 'testing_api'
    _DEFAULT_API_EMAIL = 'test@test.com'
    _DEFAULT_API_FIRST_NAME = 'Testing'
    _DEFAULT_API_LAST_NAME = 'Testing'

    def setUp(self) -> None:
        self.api_version = 'v1'

        user = User(
            email=self._DEFAULT_API_EMAIL,
            first_name=self._DEFAULT_API_FIRST_NAME,
            last_name=self._DEFAULT_API_LAST_NAME,
            username=self._DEFAULT_API_CREDS
        )
        user.set_password(self._DEFAULT_API_CREDS)
        user.save()

        self.user = user

        client = APIClient()
        response = client.post(
            '/api/token/',
            {'username': self._DEFAULT_API_CREDS, 'password': self._DEFAULT_API_CREDS},
            format='json'
        )

        self.access_token = response.json()['access']

    def _create_product(self, **kwargs: Union[str, int]) -> Dict[str, Any]:
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.post(
            f'/api/{self.api_version}/product/',
            kwargs,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()
