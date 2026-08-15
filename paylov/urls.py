from django.urls import path

from .views import *

urlpatterns = [
    path('order/create/', OrderCreateAPIView.as_view()),
    path('webhook/', PaylovWebhookAPIView.as_view()),
]