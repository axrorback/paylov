from django.contrib import admin

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'amount', 'status')