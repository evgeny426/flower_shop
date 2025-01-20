from django.contrib import admin
from .models import User, Flower, Order, OrderItem, CartItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_editable = ('status',)  # Позволяет редактировать статус прямо в списке заказов
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')

admin.site.register(User)
admin.site.register(Flower)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CartItem)
