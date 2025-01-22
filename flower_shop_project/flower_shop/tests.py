import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop_project.settings")
django.setup()

import json
import unittest
import sqlite3
from unittest.mock import patch, AsyncMock, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from .views import add_to_cart, update_cart, remove_from_cart
from .models import Flower, User, CartItem, Order, OrderItem
from bot import get_new_orders, get_order_items, get_username, get_flower_name, send_notification

class Test(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        """Настройка тестовой базы данных."""
        cls.conn = sqlite3.connect(':memory:')  # Используем базу данных в памяти
        cls.cursor = cls.conn.cursor()

        # Создаем таблицы для тестов
        cls.cursor.execute('''
            CREATE TABLE flower_shop_user (
                id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        cls.cursor.execute('''
            CREATE TABLE flower_shop_flower (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        cls.cursor.execute('''
            CREATE TABLE flower_shop_order (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                total_price REAL,
                address TEXT,
                phone TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')
        cls.cursor.execute('''
            CREATE TABLE flower_shop_orderitem (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                flower_id INTEGER,
                quantity INTEGER
            )
        ''')

        # Добавляем тестовые данные
        cls.cursor.execute('INSERT INTO flower_shop_user (id, username) VALUES (1, "test_user")')
        cls.cursor.execute('INSERT INTO flower_shop_flower (id, name) VALUES (1, "Роза")')
        cls.cursor.execute('''
            INSERT INTO flower_shop_order (id, user_id, total_price, address, phone, status, created_at)
            VALUES (1, 1, 1000, "ул. Ленина, д. 10", "+79123456789", "pending", "2023-10-10 14:30:00")
        ''')
        cls.cursor.execute('INSERT INTO flower_shop_orderitem (order_id, flower_id, quantity) VALUES (1, 1, 2)')
        cls.conn.commit()

        # Настройка для тестов корзины
        cls.factory = RequestFactory()
        cls.flower = Flower(id=1, name="Роза", price=100.0)  # Создаем тестовый товар

    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов."""
        cls.conn.close()

    def setUp(self):
        """Создание уникального пользователя для каждого теста."""
        self.user = User.objects.create_user(username=f'testuser_{self.id()}', password='testpass')

    def tearDown(self):
        """Очистка после каждого теста."""
        User.objects.filter(username__startswith='testuser_').delete()

    def test_get_new_orders(self):
        """Тест для функции get_new_orders."""
        latest_order = get_new_orders(self.conn)
        self.assertIsNotNone(latest_order)
        self.assertEqual(latest_order[0], 1)

    def test_get_order_items(self):
        """Тест для функции get_order_items."""
        items = get_order_items(1, self.conn)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], (1, 2))

    def test_get_username(self):
        """Тест для функции get_username."""
        username = get_username(1, self.conn)
        self.assertEqual(username, "test_user")

    def test_get_flower_name(self):
        """Тест для функции get_flower_name."""
        flower_name = get_flower_name(1, self.conn)
        self.assertEqual(flower_name, "Роза")

    @patch('bot.Bot.send_message', new_callable=AsyncMock)
    async def test_send_notification(self, mock_send_message):
        """Тест для функции send_notification."""
        mock_send_message.return_value = None
        order = (1, 1, 1000, "ул. Ленина, д. 10", "+79123456789", "pending", "2023-10-10 14:30:00")  # Добавлен status
        items = [(1, 2)]
        await send_notification(order, items, self.conn)
        mock_send_message.assert_called_once()

    def test_add_to_cart_anonymous_user(self):
        """Тест добавления товара в корзину для неавторизованного пользователя."""
        request = self.factory.post('/add-to-cart/1/')
        request.user = AnonymousUser()
        request.session = {}
        with patch('flower_shop.views.get_object_or_404', return_value=self.flower):
            response = add_to_cart(request, flower_id=1)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(request.session['cart'], {'1': {'quantity': 1}})

    def test_update_cart_anonymous_user_increase(self):
        """Тест увеличения количества товара в корзине для неавторизованного пользователя."""
        request = self.factory.post('/update-cart/1/increase/')
        request.user = AnonymousUser()
        request.session = {'cart': {'1': {'quantity': 1}}}
        response = update_cart(request, item_id=1, action='increase')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(request.session['cart'], {'1': {'quantity': 2}})

    def test_update_cart_anonymous_user_decrease(self):
        """Тест уменьшения количества товара в корзине для неавторизованного пользователя."""
        request = self.factory.post('/update-cart/1/decrease/')
        request.user = AnonymousUser()
        request.session = {'cart': {'1': {'quantity': 2}}}
        response = update_cart(request, item_id=1, action='decrease')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(request.session['cart'], {'1': {'quantity': 1}})

    def test_update_cart_anonymous_user_quantity_zero(self):
        """Тест уменьшения количества товара до нуля для неавторизованного пользователя."""
        request = self.factory.post('/update-cart/1/decrease/')
        request.user = AnonymousUser()
        request.session = {'cart': {'1': {'quantity': 1}}}
        response = update_cart(request, item_id=1, action='decrease')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(request.session['cart'], {'1': {'quantity': 1}})

    def test_remove_from_cart_anonymous_user(self):
        """Тест удаления товара из корзины для неавторизованного пользователя."""
        request = self.factory.post('/remove-from-cart/1/')
        request.user = AnonymousUser()
        request.session = {'cart': {'1': {'quantity': 1}}}
        response = remove_from_cart(request, item_id=1)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertNotIn('1', request.session['cart'])

    def test_add_to_cart_authenticated_user(self):
        """Тест добавления товара в корзину для авторизованного пользователя."""
        request = self.factory.post('/add-to-cart/1/')
        request.user = self.user
        request.session = {}
        with patch('flower_shop.views.get_object_or_404', return_value=self.flower):
            response = add_to_cart(request, flower_id=1)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(CartItem.objects.filter(user=self.user, flower=self.flower).count(), 1)

    def test_update_cart_authenticated_user_increase(self):
        """Тест увеличения количества товара в корзине для авторизованного пользователя."""
        cart_item = CartItem.objects.create(user=self.user, flower=self.flower, quantity=1)
        request = self.factory.post('/update-cart/1/increase/')
        request.user = self.user
        response = update_cart(request, item_id=cart_item.id, action='increase')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_authenticated_user_decrease(self):
        """Тест уменьшения количества товара в корзине для авторизованного пользователя."""
        cart_item = CartItem.objects.create(user=self.user, flower=self.flower, quantity=2)
        request = self.factory.post('/update-cart/1/decrease/')
        request.user = self.user
        response = update_cart(request, item_id=cart_item.id, action='decrease')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_from_cart_authenticated_user(self):
        """Тест удаления товара из корзины для авторизованного пользователя."""
        cart_item = CartItem.objects.create(user=self.user, flower=self.flower, quantity=1)
        request = self.factory.post('/remove-from-cart/1/')
        request.user = self.user
        response = remove_from_cart(request, item_id=cart_item.id)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'status': 'success'})
        self.assertEqual(CartItem.objects.filter(user=self.user, flower=self.flower).count(), 0)

if __name__ == '__main__':
    unittest.main()