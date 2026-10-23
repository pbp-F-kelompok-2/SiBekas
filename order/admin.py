from django.contrib import admin, messages

from .models import Order, OrderEvent, OrderItem
from .services import OrderError, change_status


class ReadOnlyInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderItemInline(ReadOnlyInline):
    model = OrderItem


class OrderEventInline(ReadOnlyInline):
    model = OrderEvent


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["number", "buyer", "recipient_name", "status", "payment_status", "total", "created_at"]
    list_filter = ["status", "payment_status", "delivery_method", "created_at"]
    search_fields = ["recipient_name", "buyer__username", "tracking_number"]
    readonly_fields = [field.name for field in Order._meta.fields]
    inlines = [OrderItemInline, OrderEventInline]
    actions = ["cancel_orders"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Batalkan pesanan dan kembalikan stok")
    def cancel_orders(self, request, queryset):
        for order in queryset:
            try:
                change_status(order.pk, request.user, "cancel")
            except OrderError as exc:
                self.message_user(request, f"{order.number}: {exc}", messages.WARNING)
            else:
                self.message_user(request, f"{order.number} dibatalkan.", messages.SUCCESS)
