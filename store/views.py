from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, is_created = Order.objects.get_or_create(customer=customer, complete=False)
        cart_items = order.get_total_cart_items
    else:
        order = {
            'get_total_cart_items': 0,
            'get_total_cart_price': 0,
            'is_shipping': False
        }
        cart_items = order['get_total_cart_items']

    products = Product.objects.all().order_by('id')
    context = {'products': products, 'cart_items': cart_items}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, is_created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.items.all()
        cart_items = order.get_total_cart_items
    else:
        items = []
        order = {
            'get_total_cart_items': 0,
            'get_total_cart_price': 0,
            'is_shipping': False
        }
        cart_items = order['get_total_cart_items']

    context = {
        'items': items,
        'order': order,
        'cart_items': cart_items
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, is_created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.items.all()
        cart_items = order.get_total_cart_items
    else:
        items = []
        order = {
            'get_total_cart_items': 0,
            'get_total_cart_price': 0,
            'is_shipping': False
        }
        cart_items = order['get_total_cart_items']

    context = {
        'items': items,
        'order': order,
        'cart_items': cart_items
    }
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print(f'product_id: {product_id}')
    print(f'action: {action}')

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, order_is_created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, orderitem_is_created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, order_is_created = Order.objects.get_or_create(customer=customer, complete=False)
        total_price = float(data['form']['total_price'])
        order.transaction_id = transaction_id

        print(total_price, order.get_total_cart_price)

        if total_price == float(order.get_total_cart_price):
            print('OK')
            order.complete = True
        order.save()

        if order.is_shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    return JsonResponse('Payment is completed!', safe=False)
