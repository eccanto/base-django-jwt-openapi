from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from ecommerce.models import Order, OrderDetail, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'


class ApiOrderSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    cuantity = serializers.IntegerField(required=True, min_value=0)
    product = serializers.CharField(required=True, max_length=36)


class ApiProductsOrderSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    products = ApiOrderSerializer(many=True, required=True)


class ApiTotalMoneySerializer(serializers.Serializer):  # pylint: disable=abstract-method
    total = MoneyField(max_digits=14, decimal_places=2)
