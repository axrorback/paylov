import base64
import urllib.parse

from django.conf import settings


def generate_payment_link(order):
    base_url = "https://my.paylov.uz/checkout/create/"

    query_params = {
        "merchant_id": settings.PAYLOV_MERCHANT_ID,
        "amount": order.amount,
        "return_url": settings.PAYLOV_RETURN_URL,
        "currency_id":840
    }

    account_params = {
        "order_id": str(order.id),
        "amount": order.amount,
        "purpose": "Django & DevOps Darslari uchun to'lov",
        "account_id":order.account_id
    }

    for key, value in account_params.items():
        query_params[f"account.{key}"] = value

    query_string = urllib.parse.urlencode(query_params)

    encoded_query = base64.b64encode(
        query_string.encode()
    ).decode()

    return f"{base_url}{encoded_query}"