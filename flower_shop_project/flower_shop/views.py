from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CartItem, Order, OrderItem, Flower


class LoginView(auth_views.LoginView):
    template_name = 'flower_shop/login.html'  # Указываем шаблон для страницы входа

    def form_valid(self, form):
        # Перенос корзины из сессии в базу данных при успешной аутентификации
        user = form.get_user()
        auth_login(self.request, user)

        cart = self.request.session.get('cart', {})
        for flower_id, item in cart.items():
            flower = Flower.objects.get(id=int(flower_id))
            cart_item, created = CartItem.objects.get_or_create(user=user, flower=flower)
            cart_item.quantity += item['quantity']
            cart_item.save()

        # Очистка корзины в сессии
        if 'cart' in self.request.session:
            del self.request.session['cart']

        return super().form_valid(form)

class LogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        print("Пользователь вышел из системы")  # Отладочный вывод
        return super().dispatch(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан!')
            return redirect('home')
        else:
            print("Форма невалидна:", form.errors)  # Отладочный вывод
    else:
        form = RegisterForm()
    return render(request, 'flower_shop/register.html', {'form': form})

def home(request):
    return render(request, 'flower_shop/index.html')

def products(request):
    flowers = Flower.objects.all()  # Получаем все товары из базы данных
    return render(request, 'flower_shop/products.html', {'flowers': flowers})

@csrf_exempt
def add_to_cart(request, flower_id):
    if request.method == 'POST':
        flower = get_object_or_404(Flower, id=flower_id)

        if request.user.is_authenticated:
            # Для зарегистрированных пользователей
            cart_item, created = CartItem.objects.get_or_create(user=request.user, flower=flower)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            # Для анонимных пользователей
            cart = request.session.get('cart', {})
            cart_item = cart.get(str(flower_id), {'quantity': 0})
            cart_item['quantity'] += 1
            cart[str(flower_id)] = cart_item
            request.session['cart'] = cart

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def cart(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        # Для зарегистрированных пользователей
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.total_price for item in cart_items)
    else:
        # Для анонимных пользователей
        cart = request.session.get('cart', {})
        for flower_id, item in cart.items():
            flower = Flower.objects.get(id=int(flower_id))
            quantity = item['quantity']
            total_price += flower.price * quantity
            cart_items.append({
                'flower': flower,
                'quantity': quantity,
                'total_price': flower.price * quantity,
            })

    return render(request, 'flower_shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@csrf_exempt
def update_cart(request, item_id, action):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Для зарегистрированных пользователей
            item = CartItem.objects.get(id=item_id)
            if action == 'increase':
                item.quantity += 1
            elif action == 'decrease' and item.quantity > 1:
                item.quantity -= 1
            item.save()
        else:
            # Для анонимных пользователей
            cart = request.session.get('cart', {})
            item = cart.get(str(item_id), {'quantity': 1})
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1:
                item['quantity'] -= 1
            cart[str(item_id)] = item
            request.session['cart'] = cart

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            item_id = int(item_id)  # Преобразуем item_id в число
        except ValueError:
            return JsonResponse({'status': 'error'}, status=400)

        if request.user.is_authenticated:
            item = CartItem.objects.get(id=item_id)
            item.delete()
        else:
            cart = request.session.get('cart', {})
            if str(item_id) in cart:
                del cart[str(item_id)]
                request.session['cart'] = cart

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Для оформления заказа необходимо войти в систему.')
        return redirect('login')

    # Получаем товары из корзины
    if request.user.is_authenticated:
        # Для авторизованных пользователей
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        # Для анонимных пользователей
        cart = request.session.get('cart', {})
        cart_items = []
        for flower_id, item in cart.items():
            flower = Flower.objects.get(id=int(flower_id))
            cart_items.append({
                'flower': flower,
                'quantity': item['quantity'],
                'total_price': flower.price * item['quantity'],
            })

    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('cart')

    if request.method == 'POST':
        # Получаем данные из формы
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Создаем заказ
        total_price = sum(item.total_price for item in cart_items)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_price=total_price,
            address=address,
            phone=phone,
        )

        # Добавляем товары в заказ
        for cart_item in cart_items:
            if request.user.is_authenticated:
                # Для авторизованных пользователей
                OrderItem.objects.create(
                    order=order,
                    flower=cart_item.flower,
                    quantity=cart_item.quantity,
                )
            else:
                # Для анонимных пользователей
                OrderItem.objects.create(
                    order=order,
                    flower=cart_item['flower'],
                    quantity=cart_item['quantity'],
                )

        # Очищаем корзину
        if request.user.is_authenticated:
            cart_items.delete()  # Удаляем товары из корзины для авторизованных пользователей
        else:
            request.session['cart'] = {}  # Очищаем корзину в сессии для анонимных пользователей

        messages.success(request, 'Ваш заказ успешно оформлен!')
        return redirect('home')

    return render(request, 'flower_shop/checkout.html', {'cart_items': cart_items})


