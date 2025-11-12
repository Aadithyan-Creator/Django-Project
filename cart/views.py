from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from .forms import CartItemForm
from account.models import Account
from decimal import Decimal

COUPONS = {
    "111111": {"type": "percentage", "amount": 10},
    "222222": {"type": "fixed", "amount": 100},
}

def cart_list(request):
    account = Account.objects.first()
    cart, _ = Cart.objects.get_or_create(account=account, is_active=True)
    items = cart.items.all()

    coupon_code = request.session.get('applied_coupon')
    coupon_data = COUPONS.get(coupon_code) if coupon_code else None

    total = cart.grand_total()
    discounted_total = cart.grand_total(coupon_data) if coupon_data else total

    return render(request, 'cart/cart_list.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'discounted_total': discounted_total,
        'coupon_code': coupon_code,
        'coupon_data': coupon_data,
    })


def cart_add_item(request):
    account = Account.objects.first()
    cart, _ = Cart.objects.get_or_create(account=account, is_active=True)

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.cart = cart
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect('cart_list')
    else:
        form = CartItemForm()

    items = cart.items.all()
    return render(request, 'cart/cart_add_items.html', {
        'cart': cart,
        'form': form,
        'items': items,
    })


def cart_update(request, pk):
    account = Account.objects.first()
    cart_item = get_object_or_404(CartItem, pk=pk, cart__account=account)

    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect('cart_list')
    else:
        form = CartItemForm(instance=cart_item)

    return render(request, 'cart/cart_form.html', {
        'form': form,
        'title': 'Update Cart Item'
    })


def cart_delete(request, pk):
    account = Account.objects.first()
    cart_item = get_object_or_404(CartItem, pk=pk, cart__account=account)
    if request.method == 'POST':
        cart_item.delete()
        return redirect('cart_list')
    return render(request, 'cart/cart_confirm_delete.html', {'cart_item': cart_item})


def cart_checkout(request):
    account = Account.objects.first()
    cart = Cart.objects.filter(account=account, is_active=True).first()
    if not cart or not cart.items.exists():
        return redirect('cart_list')

    coupon_data = None
    discount_applied = False
    invalid_coupon = False

    if request.method == 'POST' and 'coupon_code' in request.POST:
        coupon_code = request.POST.get('coupon_code')
        coupon_data = COUPONS.get(coupon_code)
        if coupon_data:
            request.session['applied_coupon'] = coupon_code
            discount_applied = True
        else:
            request.session.pop('applied_coupon', None)
            invalid_coupon = True
    elif request.session.get('applied_coupon'):
        coupon_code = request.session.get('applied_coupon')
        coupon_data = COUPONS.get(coupon_code)
        if coupon_data:
            discount_applied = True

    total = cart.grand_total()
    discounted_total = cart.grand_total(coupon_data) if coupon_data else total
    saved_amount = total - discounted_total

    for item in cart.items.all():
        item.final_price_amount = item.final_price(coupon_data)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'items': cart.items.all(),
        'total': total,
        'discounted_total': discounted_total,
        'coupon_data': coupon_data,
        'discount_applied': discount_applied,
        'invalid_coupon': invalid_coupon,
        'saved_amount': saved_amount,
    })
