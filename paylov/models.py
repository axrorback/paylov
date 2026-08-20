# models.py

import uuid

from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    amount = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING
    )

    transaction_id = models.UUIDField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    account_id = models.CharField(max_length=255 , null=True, blank=True)
    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.id)