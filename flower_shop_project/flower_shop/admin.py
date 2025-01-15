from django.contrib import admin
from .models import User, Flower, Order, OrderItem, CartItem

admin.site.register(User)
admin.site.register(Flower)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)  # Добавь эту строку
