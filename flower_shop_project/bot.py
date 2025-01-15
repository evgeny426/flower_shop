import sqlite3
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TOKEN, CHAT_ID

# Настройки бота
TELEGRAM_BOT_TOKEN = TOKEN
TELEGRAM_CHAT_ID = CHAT_ID  # ID чата, куда будут отправляться уведомления

# Путь к базе данных
DATABASE_PATH = 'db.sqlite3'

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_new_orders(conn):
    """Получает новые заказы из базы данных."""
    cursor = conn.cursor()

    # Получаем последний заказ
    cursor.execute('''
        SELECT id, user_id, total_price, address, phone, created_at
        FROM flower_shop_order
        ORDER BY created_at DESC
        LIMIT 1
    ''')
    latest_order = cursor.fetchone()

    return latest_order

def get_order_items(order_id, conn):
    """Получает товары из заказа."""
    cursor = conn.cursor()

    # Получаем товары для заказа
    cursor.execute('''
        SELECT flower_id, quantity
        FROM flower_shop_orderitem
        WHERE order_id = ?
    ''', (order_id,))
    items = cursor.fetchall()

    return items

def get_username(user_id, conn):
    """Получает имя пользователя по его ID."""
    cursor = conn.cursor()

    cursor.execute('''
        SELECT username
        FROM flower_shop_user
        WHERE id = ?
    ''', (user_id,))
    user = cursor.fetchone()

    return user[0] if user else "Неизвестный пользователь"

def get_flower_name(flower_id, conn):
    """Получает название товара по его ID."""
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name
        FROM flower_shop_flower
        WHERE id = ?
    ''', (flower_id,))
    flower = cursor.fetchone()

    return flower[0] if flower else "Неизвестный товар"

async def send_notification(order, items, conn):
    """Отправляет уведомление о новом заказе."""
    order_id, user_id, total_price, address, phone, created_at = order

    # Получаем имя пользователя
    username = get_username(user_id, conn)

    # Округляем секунды в дате заказа
    created_at_rounded = created_at.split('.')[0]  # Убираем миллисекунды

    # Формируем сообщение
    message = (
        f"🎉 Новый заказ!\n\n"
        f"🔔 ID заказа: {order_id}\n"
        f"👤 Покупатель: {username}\n"
        f"📦 Адрес доставки: {address}\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Сумма заказа: {total_price} руб.\n"
        f"🕒 Дата и время заказа: {created_at_rounded}\n\n"
        f"📦 Товары:\n"
    )

    # Добавляем информацию о товарах
    for flower_id, quantity in items:
        flower_name = get_flower_name(flower_id, conn)
        message += f"- {flower_name}, Количество: {quantity}\n"

    # Отправляем сообщение
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Уведомление отправлено!")
    except TelegramError as e:
        print(f"Ошибка при отправке уведомления: {e}")

async def monitor_orders():
    """Мониторит новые заказы."""
    last_order_id = None

    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect(DATABASE_PATH)

    while True:
        # Получаем последний заказ
        latest_order = get_new_orders(conn)

        if latest_order and latest_order[0] != last_order_id:
            # Если найден новый заказ
            last_order_id = latest_order[0]
            order_items = get_order_items(last_order_id, conn)

            # Отправляем уведомление
            await send_notification(latest_order, order_items, conn)

        # Пауза перед следующей проверкой
        await asyncio.sleep(10)

    # Закрываем соединение с базой данных
    conn.close()

if __name__ == '__main__':
    print("Бот запущен и мониторит новые заказы...")
    asyncio.run(monitor_orders())