from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from ecommerce.models import Product, Order, OrderDetail


class OrderTestCase(TestCase):
    def setUp(self):
        self.username = 'testing_order_usernamme'
        self.password = 'testing_order_password'
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

        # create producs
        self.products = [
            {
                'name': 'product 1',
                'price': '200',
                'stock': 51
            },
            {
                'name': 'product 2',
                'price': '202',
                'stock': 52
            },
            {
                'name': 'product 3',
                'price': '203',
                'stock': 53
            }
        ]
        for product_data in self.products:
            product_id = self._create_product(**product_data)['id']
            product_data['id'] = product_id

        # new order
        self.new_order = [
            {
                'cuantity': 5,
                'product': self.products[0]['id']
            },
            {
                'cuantity': 7,
                'product': self.products[1]['id']
            }
        ]

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

    def _create_order(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.post(
            f'/api/{self.api_version}/order/register_order/',
            {'products': self.new_order},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()

    def test_register_order(self):
        # check request
        resp_data = self._create_order()
        self.assertEqual(len(resp_data), 2)
        self.assertIn('id', resp_data)
        self.assertIn('date_time', resp_data)

        # check db
        order_id = resp_data['id']
        order = Order.objects.get(id=order_id)
        products = Product.objects.filter(orderdetail__in=order.orderdetail_set.all())

        self.assertListEqual(
            [str(p.id) for p in products],
            [self.products[0]['id'], self.products[1]['id']]
        )

        for product in products:
            product_order = next(
                (p for p in self.new_order if p['product'] == str(product.id)),
                None
            )
            product_test = next((p for p in self.products if p['id'] == str(product.id)), None)

            self.assertEqual(product.stock, product_test['stock'] - product_order['cuantity'])

    def test_edit_order(self):
        order_update = [
            {
                'cuantity': 2,
                'product': self.products[0]['id']
            }
        ]

        # check request
        resp_data = self._create_order()
        order_id = resp_data['id']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.put(
            f'/api/{self.api_version}/order/{order_id}/update_order/',
            {'products': order_update},
            format='json'
        )

        # check request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()
        self.assertEqual(len(resp_data), 2)
        self.assertIn('id', resp_data)
        self.assertIn('date_time', resp_data)

        # check db
        order = Order.objects.get(id=order_id)
        products = Product.objects.filter(orderdetail__in=order.orderdetail_set.all())

        self.assertListEqual(
            [str(p.id) for p in products],
            [self.products[0]['id'], self.products[1]['id']]
        )

        for product in products:
            product_order = next((p for p in order_update if p['product'] == str(product.id)), None)
            if product_order:
                product_test = next((p for p in self.products if p['id'] == str(product.id)), None)

                self.assertEqual(product.stock, product_test['stock'] - product_order['cuantity'])

    def test_delete_order(self):
        # send order
        resp_data = self._create_order()
        order_id = resp_data['id']

        order_obj = Order.objects.get(id=order_id)
        order_details = list(order_obj.orderdetail_set.all())
        products = list(Product.objects.filter(orderdetail__in=order_details))

        # send request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.delete(f'/api/{self.api_version}/order/{order_id}/')

        # check request
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

        # check db
        order_obj = Order.objects.filter(id=order_id).first()
        self.assertIsNone(order_obj)

        for product in products:
            product_updated = Product.objects.get(id=product.id)
            product_order = next((p for p in self.products if p['id'] == str(product.id)), None)

            self.assertEqual(product_updated.stock, product_order['stock'])

        for order_detail in order_details:
            order_detail_obj = OrderDetail.objects.filter(id=order_detail.id).first()
            self.assertIsNone(order_detail_obj)

    def test_get_order_details(self):
        # send order
        resp_data = self._create_order()
        order_id = resp_data['id']

        # send request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.get(f'/api/{self.api_version}/order/{order_id}/order_details/')

        # check request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()
        self.assertEqual(len(resp_data), len(self.new_order))
        self.assertTrue(all(detail['order'] == order_id for detail in resp_data))

        # check db
        order = Order.objects.get(id=order_id)
        order_details = order.orderdetail_set.all()
        products = Product.objects.filter(orderdetail__in=order_details)

        self.assertEqual(len(resp_data), len(order_details))
        self.assertEqual(len(resp_data), len(products))
        self.assertListEqual([str(p.id) for p in products], [p['product'] for p in resp_data])

        for detail in resp_data:
            order_detail = OrderDetail.objects.filter(id=detail['id']).first()
            self.assertIsNotNone(order_detail)
            self.assertEqual(detail['cuantity'], order_detail.cuantity)

    def test_list_orders(self):
        # send orders
        orders_number = 5
        orders = [self._create_order()['id'] for _ in range(orders_number)]

        # send request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = client.get('/api/v1/order/')

        # check request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_data = response.json()
        self.assertEqual(len(resp_data), orders_number)

        self.assertListEqual(orders, [o['id'] for o in resp_data])
