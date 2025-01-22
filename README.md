# Flower Shop Project

Это веб-приложение для цветочного магазина, разработанное с использованием Django. Проект включает в себя функциональность для просмотра ассортимента, добавления товаров в корзину, оформления заказов, управления пользователями и просмотра истории заказов.

## Основные функции

- **Просмотр ассортимента**: Пользователи могут просматривать доступные цветы с их описанием и ценой.
- **Корзина**: Пользователи могут добавлять товары в корзину, изменять количество и удалять товары.
- **Оформление заказа**: Пользователи могут оформлять заказы, указывая адрес доставки и контактный телефон.
- **История заказов**: Пользователи могут просматривать историю своих заказов, включая детали каждого заказа (товары, статус, сумму и дату).
- **Регистрация и вход**: Пользователи могут регистрироваться и входить в систему для управления своими заказами.
- **Уведомления**: Администратор получает уведомления в Telegram о новых заказах и изменениях их статуса.

## Установка и запуск

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/ваш-username/flower_shop.git
   cd flower_shop/flower_shop_project
   ```

2. **Создайте и активируйте виртуальное окружение**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Для Linux/MacOS
   .venv\Scripts\activate     # Для Windows
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте базу данных:**:
   ```bash
   python manage.py makemigrations flower_shop
   python manage.py migrate
   ```

5. **Создайте суперпользователя**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Запустите сервер**:
   ```bash
   python manage.py runserver
   ```

7. **Откройте браузер и перейдите по адресу**:
   ```
   http://127.0.0.1:8000/
   ```

## Настройка Telegram бота

Для получения уведомлений о новых заказах необходимо настроить Telegram бота:

1. **Создайте бота** через [BotFather](https://core.telegram.org/bots#botfather) и получите токен.
2. **Создайте файл `config.py`** в корне проекта и добавьте туда токен и ID чата:
   ```python
   TOKEN = 'ваш-токен'
   CHAT_ID = 'ваш-чат-id'
   ```
3. **Запустите бота**:
   ```bash
   cd flower_shop/flower_shop_project
   python bot.py
   ```

## Структура проекта

```
flower_shop_project/
    flower_shop/
        migrations/
        templates/
        __init__.py
        admin.py
        apps.py
        forms.py
        models.py
        tests.py
        urls.py
        views.py
    flower_shop_project/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    media/
    static/
    __init__.py
    bot.py
    config.py
    db.sqlite3
    manage.py
    requirements.txt
```

## Тестирование

Для запуска тестов выполните команду:
```bash
python -m unittest flower_shop/tests.py
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).

## Автор

[Бардыгин Евгений](https://github.com/evgeny426)
```

