from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Cart, CartItem, CartCoupon
from .forms import CartItemForm
from account.models import Account


def cart_list(request):
    account = Account.objects.first()
    cart, _ = Cart.objects.get_or_create(account=account, is_active=True, defaults={'created_at': timezone.now()})

    coupon = None
    discount_applied = False
    invalid_coupon = False

    items = cart.items.all()
    total = cart.total_price()
    discounted_total = cart.final_amount()

    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip()
        coupon = CartCoupon.objects.filter(coupon_code=code, discount_active=True).first()

        if coupon:
            discounted_total = coupon.coupon_discount(cart)
            discount_applied = True
            request.session['applied_coupon'] = code
        else:
            invalid_coupon = True

    return render(request, 'cart/cart_list.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'discounted_total': discounted_total,
        'coupon': coupon,
        'discount_applied': discount_applied,
        'invalid_coupon': invalid_coupon,
    })


def cart_create(request):
    account = Account.objects.first()
    cart, _ = Cart.objects.get_or_create(account=account, is_active=True, defaults={'created_at': timezone.now()})

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            product = cart_item.product
            quantity = cart_item.quantity
            cart_item.cart = cart
            cart_item.price = product.price
            cart_item.discount_percent = 0

            if hasattr(product, 'reduce_stock') and product.reduce_stock(quantity):
                cart_item.save()
                return redirect('cart_list')
            else:
                form.add_error('quantity', 'Not enough stock available')
    else:
        form = CartItemForm()

    return render(request, 'cart/cart_form.html', {'form': form})


def cart_add_items(request):
    account = Account.objects.first()
    cart, _ = Cart.objects.get_or_create(account=account, is_active=True)

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.cart = cart
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect('cart_add_items')
    else:
        form = CartItemForm()

    items = cart.items.all()
    return render(request, 'cart/cart_add_items.html', {
        'cart': cart,
        'form': form,
        'items': items,
    })


def cart_checkout(request):
    account = Account.objects.first()
    cart = Cart.objects.filter(account=account, is_active=True).first()
    if not cart:
        return redirect('cart_list')

    coupon_code = request.session.get('applied_coupon')
    coupon = CartCoupon.objects.filter(coupon_code=coupon_code, discount_active=True).first() if coupon_code else None

    final_total = coupon.coupon_discount(cart) if coupon else cart.final_amount()

    cart.is_active = False
    cart.save()
    request.session.pop('applied_coupon', None)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'final_total': final_total,
        'coupon': coupon,
    })


def cart_update(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            return redirect('cart_list')
    else:
        form = CartItemForm(instance=cart_item)
    return render(request, 'cart/cart_form.html', {'form': form, 'title': 'Update Cart Item'})


def cart_delete(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    if request.method == 'POST':
        cart_item.delete()
        return redirect('cart_list')
    return render(request, 'cart/cart_confirm_delete.html', {'cart_item': cart_item})
