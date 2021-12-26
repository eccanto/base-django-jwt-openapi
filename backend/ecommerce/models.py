import uuid
from typing import Any, Dict, Tuple

from django.db import models, transaction
from djmoney.models.fields import MoneyField


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='ARS')
    stock = models.PositiveIntegerField()


class Order(models.Model):
    date_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']

    def delete(self, using: Any = None, keep_parents: bool = False) -> Tuple[int, Dict[str, int]]:
        with transaction.atomic():
            for order_detail in self.orderdetail_set.all():
                order_detail.product.stock += order_detail.cuantity
                order_detail.product.save()

                order_detail.delete()

        return super().delete(using, keep_parents)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cuantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
