from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'year', 'month', 'amount', 'paid_amount', 'status', 'payment_date']
    list_filter = ['status', 'year', 'month', 'payment_method']
    search_fields = ['student__name']
    raw_id_fields = ['student']
