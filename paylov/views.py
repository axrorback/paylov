from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer , PaylovWebhookSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from kafka_sender import send_payment_event
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


class OrderCreateAPIView(CreateAPIView):

    queryset = Order.objects.all()

    serializer_class = OrderSerializer


@method_decorator(csrf_exempt, name='dispatch')
class PaylovWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    serializer_class = PaylovWebhookSerializer

    def post(self, request):

        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        if data["method"] == "transaction.check":
            return self.transaction_check(data)

        if data["method"] == "transaction.perform":
            return self.transaction_perform(data)
        return Response(
            {"detail": "Invalid method"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def transaction_check(self, data):

        params = data["params"]

        order_id = params["account"]["order_id"]
        amount = params["amount"]

        try:
            order = Order.objects.get(id=order_id)

        except Order.DoesNotExist:

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": data["id"],
                    "result": {
                        "status": "303",
                        "statusText": "Order not found"
                    }
                }
            )

        if order.amount != amount:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": data["id"],
                    "result": {
                        "status": "5",
                        "statusText": "Invalid amount"
                    }
                }
            )

        return Response(
            {
                "jsonrpc": "2.0",
                "id": data["id"],
                "result": {
                    "status": "0",
                    "statusText": "OK"
                }
            }
        )

    def transaction_perform(self, data):
        params = data["params"]

        order_id = params["account"]["order_id"]
        transaction_id = params["transaction_id"]
        amount = params["amount"]

        try:
            with transaction.atomic():
                order = (
                    Order.objects
                    .select_for_update()
                    .get(id=order_id)
                )

                if order.amount != amount:
                    return Response({
                        "jsonrpc": "2.0",
                        "id": data["id"],
                        "result": {
                            "status": "5",
                            "statusText": "Invalid amount",
                        },
                    })


                if order.status != Order.Status.PAID:
                    order.status = Order.Status.PAID
                    order.transaction_id = transaction_id
                    order.paid_at = timezone.now()
                    order.save(
                        update_fields=[
                            "status",
                            "transaction_id",
                            "paid_at",
                        ]
                    )

                    event = {
                        "event": "payment.paid",
                        "provider": "paylov",
                        "order_id": order.id,
                        "transaction_id": transaction_id,
                        "amount": order.amount,
                        "status": "paid",
                        "paid_at": order.paid_at.isoformat(),
                    }

                    def publish_after_commit():
                        try:
                            send_payment_event(event)
                        except Exception:
                            logger.exception(
                                "Failed to publish Paylov event: "
                                "order_id=%s transaction_id=%s",
                                order.id,
                                transaction_id,
                            )

                    transaction.on_commit(publish_after_commit)

        except Order.DoesNotExist:
            return Response({
                "jsonrpc": "2.0",
                "id": data["id"],
                "result": {
                    "status": "303",
                    "statusText": "Order not found",
                },
            })

        return Response({
            "jsonrpc": "2.0",
            "id": data["id"],
            "result": {
                "status": "0",
                "statusText": "OK",
            },
        })