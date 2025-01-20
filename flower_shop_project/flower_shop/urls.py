from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('register/', views.register, name='register'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('add-to-cart/<int:flower_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),  # Маршрут для обновления корзины
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Маршрут для удаления из корзины
    path('order-history/', views.order_history, name='order_history'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
]