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
            "payment_url",
        )

        read_only_fields = (
            "id",
            "payment_url",
        )

    def get_payment_url(self, obj):
        return generate_payment_link(obj)





class AccountSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()


class TransactionParamsSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField(required=False)

    account = AccountSerializer()

    amount = serializers.IntegerField()

    amount_tiyin = serializers.IntegerField()

    currency = serializers.IntegerField()


class PaylovWebhookSerializer(serializers.Serializer):
    jsonrpc = serializers.CharField()

    id = serializers.IntegerField()

    method = serializers.ChoiceField(
        choices=[
            "transaction.check",
            "transaction.perform",
        ]
    )

    params = TransactionParamsSerializer()