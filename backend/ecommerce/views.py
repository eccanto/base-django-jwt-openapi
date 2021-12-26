# pylint: disable=too-many-ancestors
import json
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

import requests
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ecommerce.models import Order, OrderDetail, Product
from ecommerce.schemes import ApiVersioningSchema, CustomOrderSchema
from ecommerce.serializers import (ApiProductsOrderSerializer, ApiTotalMoneySerializer,
                                   OrderDetailSerializer, OrderSerializer, ProductSerializer)
from service import settings
from service.views import ApiVersioning


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    versioning_class = ApiVersioning
    schema = ApiVersioningSchema(tags=['product'])


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    versioning_class = ApiVersioning
    schema = CustomOrderSchema(tags=['order'])

    @staticmethod
    @action(detail=False, methods=['post'])
    def register_order(request: Request, version: Optional[str] = None) -> Response:
        # pylint: disable=unused-argument
        """Register a order."""
        data_serializer = ApiProductsOrderSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)

        order_data = [tuple(item.values()) for item in data_serializer.validated_data['products']]
        product_ids = [item[1] for item in order_data]
        if len(product_ids) == len(set(product_ids)):  # no duplicate products
            with transaction.atomic():
                sid = transaction.savepoint()

                order = Order.objects.create()
                for cuantity, product_id in order_data:
                    product = get_object_or_404(Product, pk=product_id)
                    if product.stock >= cuantity:
                        product.stock -= cuantity
                        product.save()

                        OrderDetail.objects.create(
                            order=order,
                            cuantity=cuantity,
                            product=product,
                        )
                    else:
                        transaction.savepoint_rollback(sid)

                        response = Response(
                            {
                                'message': 'the product stock is not sufficient: '
                                           f'{product.stock} ({product_id})'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        break
                else:
                    response = Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            response = Response(
                {'message': f'duplicate products were detected: {product_ids}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response

    @action(detail=True, methods=['put'])
    def update_order(
        self, request: Request, pk: Any = None, version: Optional[str] = None
    ) -> Response:
        # pylint: disable=unused-argument
        """Update a order."""
        data_serializer = ApiProductsOrderSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)

        order_data = [tuple(item.values()) for item in data_serializer.validated_data['products']]
        product_ids = [item[1] for item in order_data]
        if len(product_ids) == len(set(product_ids)):  # no duplicate products
            with transaction.atomic():
                sid = transaction.savepoint()

                order = self.get_object()
                for cuantity, product_id in order_data:
                    order_detail = get_object_or_404(
                        OrderDetail, order=order, product__id=product_id
                    )

                    product = order_detail.product
                    current_stock = product.stock + order_detail.cuantity
                    if current_stock >= cuantity:
                        if cuantity > order_detail.cuantity:
                            product.stock -= (cuantity - order_detail.cuantity)
                        elif cuantity < order_detail.cuantity:
                            product.stock += (order_detail.cuantity - cuantity)

                        product.save()

                        order_detail.cuantity = cuantity
                        order_detail.save()
                    else:
                        transaction.savepoint_rollback(sid)

                        response = Response(
                            {
                                'message': 'the product stock is not sufficient: '
                                           f'{current_stock} ({product_id})'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        break
                else:
                    order.date_time = datetime.now()
                    order.save()

                    response = Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            response = Response(
                {'message': f'duplicate products were detected: {product_ids}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response

    @action(detail=True, methods=['get'])
    def order_details(
        self, request: Request, pk: Any = None, version: Optional[str] = None
    ) -> Response:
        # pylint: disable=unused-argument

        order = self.get_object()
        return Response(
            OrderDetailSerializer(order.orderdetail_set.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def get_total(
        self, request: Request, pk: Any = None, version: Optional[str] = None
    ) -> Response:
        # pylint: disable=unused-argument
        """Obtain invoice data."""
        order = self.get_object()
        return Response({'total': self._get_total(order)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def get_total_usd(
        self, request: Request, pk: Any = None, version: Optional[str] = None
    ) -> Response:
        # pylint: disable=unused-argument
        """Obtain invoice data USD BLUE."""
        order = self.get_object()
        try:
            resp_dolar = requests.get(settings.EXCHANGE_USD)
            resp_dolar.raise_for_status()

            data = resp_dolar.json()
            dolar_blue = next(
                (val['casa']['venta'] for val in data if val['casa']['nombre'] == 'Dolar Blue'),
                None
            )
            if dolar_blue:
                dolar_blue_float = dolar_blue.replace('.', '').replace(',', '.')
                response = Response(
                    ApiTotalMoneySerializer({
                        'total': self._get_total(order) / Decimal(dolar_blue_float),
                    }).data,
                    status=status.HTTP_200_OK
                )
            else:
                response = Response(
                    {'message': 'error generating the result'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            response = Response(
                {'message': 'error generating the result'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return response

    @staticmethod
    def _get_total(order: Order) -> Decimal:
        return Decimal(
            OrderDetail.objects.filter(order=order).aggregate(
                total=Sum(F('cuantity') * F('product__price'))
            )['total']
        )


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    versioning_class = ApiVersioning
    http_method_names: List[str] = []
