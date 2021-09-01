from django.contrib import admin
from .models import Payment, Order, Order_Product

class OrderProductInline(admin.TabularInline):
    model = Order_Product
    extra = 0
    readonly_fields = ("payment", "user", "product", "variation", "quantity", "product_price")

class OrderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "state", "city", "address_line1", "order_total", "status", "is_ordered")
    list_filter = ("status", "is_ordered")
    search_fields = ("order_number", "first_name", "last_name", "phone", "email")
    list_per_page = 20
    inlines = (OrderProductInline,)

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Order_Product)