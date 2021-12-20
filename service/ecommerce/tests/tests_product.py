from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ecommerce.models import Product


class ProductTestCase(TestCase):
    def setUp(self):
        self.username = 'testing_product_usernamme'
        self.password = 'testing_product_password'
        self.api_version = 'v1'

        user = User(
            email='test@test.com',
            first_name='Testing',
            last_name='Testing',
            username=self.username
        )
        user.set_password(self.password)
        user.save()

        self.user = user

        client = APIClient()
        response = client.post(
            '/api/token/',
            {'username': self.username, 'password': self.password},
            format='json'
        )

        self.access_token = response.json()['access']

    def _create_product(self, **kwargs):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.post(
            f'/api/{self.api_version}/product/',
            kwargs,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()

    def test_create_product(self):
        resp_data = self._create_product(name='test 1', price='599', stock=60)

        # check response
        self.assertEqual(len(resp_data), 5)
        self.assertIn('id', resp_data)
        self.assertIn('name', resp_data)
        self.assertIn('price_currency', resp_data)
        self.assertIn('price', resp_data)
        self.assertIn('stock', resp_data)

        # check db
        product_obj = Product.objects.get(id=resp_data['id'])

        self.assertEqual(resp_data['id'], str(product_obj.id))
        self.assertEqual(resp_data['name'], product_obj.name)
        self.assertEqual(resp_data['price_currency'], 'ARS')
        self.assertEqual(Decimal(resp_data['price']), product_obj.price.amount)
        self.assertEqual(resp_data['stock'], product_obj.stock)

    def test_update_product_put(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        product_id = self._create_product(name='test 2', price='599', stock=60)['id']

        # request
        update_data = {
            'name': 'test 2 - update',
            'price': '200',
            'stock': 20
        }

        response = client.put(
            f'/api/{self.api_version}/product/{product_id}/',
            update_data,
            format='json'
        )

        # check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()

        self.assertEqual(len(resp_data), 5)
        self.assertIn('id', resp_data)
        self.assertIn('name', resp_data)
        self.assertIn('price_currency', resp_data)
        self.assertIn('price', resp_data)
        self.assertIn('stock', resp_data)

        # check db
        product_obj = Product.objects.get(id=product_id)

        self.assertEqual(resp_data['id'], str(product_obj.id))
        self.assertEqual(resp_data['name'], product_obj.name)
        self.assertEqual(resp_data['price_currency'], 'ARS')
        self.assertEqual(Decimal(resp_data['price']), product_obj.price.amount)
        self.assertEqual(resp_data['stock'], product_obj.stock)

        self.assertEqual(update_data['name'], product_obj.name)
        self.assertEqual(Decimal(update_data['price']), product_obj.price.amount)
        self.assertEqual(update_data['stock'], product_obj.stock)

    def test_update_product_patch(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        product_id = self._create_product(name='test 3', price='599', stock=60)['id']

        # request
        update_data = {
            'stock': 100,
        }

        response = client.patch(
            f'/api/{self.api_version}/product/{product_id}/',
            update_data,
            format='json'
        )

        # check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()

        self.assertEqual(len(resp_data), 5)
        self.assertIn('id', resp_data)
        self.assertIn('name', resp_data)
        self.assertIn('price_currency', resp_data)
        self.assertIn('price', resp_data)
        self.assertIn('stock', resp_data)

        # check product
        product_obj = Product.objects.get(id=product_id)

        self.assertEqual(resp_data['id'], str(product_obj.id))
        self.assertEqual(resp_data['name'], product_obj.name)
        self.assertEqual(resp_data['price_currency'], 'ARS')
        self.assertEqual(Decimal(resp_data['price']), product_obj.price.amount)
        self.assertEqual(resp_data['stock'], product_obj.stock)

        self.assertEqual(update_data['stock'], product_obj.stock)

    def test_delete_product(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        product_id = self._create_product(name='test 4', price='701', stock=22)['id']

        # request
        response = client.delete(f'/api/{self.api_version}/product/{product_id}/')

        # check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

        # check db
        product_obj = Product.objects.filter(id=product_id).first()
        self.assertIsNone(product_obj)

    def test_get_product(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        product_data = {
            'name': 'test 4',
            'price': '701',
            'stock': 22
        }
        product_id = self._create_product(**product_data)['id']

        # request
        response = client.get(f'/api/{self.api_version}/product/{product_id}/')

        # check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()

        self.assertEqual(len(resp_data), 5)
        self.assertIn('id', resp_data)
        self.assertIn('name', resp_data)
        self.assertIn('price_currency', resp_data)
        self.assertIn('price', resp_data)
        self.assertIn('stock', resp_data)

        self.assertEqual(resp_data['name'], product_data['name'])
        self.assertEqual(Decimal(resp_data['price']), Decimal(product_data['price']))
        self.assertEqual(resp_data['stock'], product_data['stock'])

    def test_get_products(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        products = [
            {
                'name': 'test 5',
                'price': '705',
                'stock': 25
            },
            {
                'name': 'test 6',
                'price': '706',
                'stock': 26
            },
            {
                'name': 'test 7',
                'price': '707',
                'stock': 27
            }
        ]

        products_id = []
        for product_data in products:
            products_id.append(self._create_product(**product_data)['id'])

        # request
        response = client.get(f'/api/{self.api_version}/product/')

        # check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()

        self.assertIsInstance(resp_data, list)
        self.assertEqual(len(products), len(resp_data))

        for resp_product in resp_data:
            self.assertEqual(len(resp_product), 5)
            self.assertIn('id', resp_product)
            self.assertIn('name', resp_product)
            self.assertIn('price_currency', resp_product)
            self.assertIn('price', resp_product)
            self.assertIn('stock', resp_product)
