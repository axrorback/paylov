from rest_framework import serializers

from .models import Order
from .utils import generate_payment_link


def get_payment_url(obj):
    return generate_payment_link(obj)


class OrderSerializer(serializers.ModelSerializer):

    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = (
            "id",
            "amount",
            "account_id",
            "payment_url",
        )

        read_only_fields = (
            "id",
            "payment_url",
        )

    def get_payment_url(self, obj):
        return generate_payment_link(obj)





class AccountSerializer(serializers.Serializer):
    order_id = serializers.CharField()


class TransactionParamsSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    account = AccountSerializer()

    amount = serializers.IntegerField()

    amount_tiyin = serializers.IntegerField(required=False, allow_null=True)

    currency = serializers.IntegerField(required=False, allow_null=True)


class PaylovWebhookSerializer(serializers.Serializer):
    jsonrpc = serializers.CharField(required=False, allow_null=True)

    id = serializers.JSONField()

    method = serializers.ChoiceField(
        choices=[
            "transaction.check",
            "transaction.perform",
        ]
    )

    params = TransactionParamsSerializer()