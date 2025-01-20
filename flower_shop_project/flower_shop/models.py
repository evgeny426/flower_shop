from django.db import models
from django.contrib.auth.models import AbstractUser


# Модель пользователя
class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

# Модель цветов
class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Заказ может быть анонимным
    flowers = models.ManyToManyField(Flower, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()  # Адрес доставки
    phone = models.CharField(max_length=15)  # Телефон для связи
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Anonymous'}"

# Модель для связи заказа и товаров
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.flower.name} in Order {self.order.id}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey('Flower', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.flower.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.flower.name} (User: {self.user.username})"
