from carts.models import CartItem, Cart
from django.contrib import admin

class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "date_added")

class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "cart", "user" ,"quantity", "is_active")

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)