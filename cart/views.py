from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from .forms import CartItemForm
from products.models import Product

COUPONS = {
    "111111": {"type": "percentage", "amount": 10},
    "222222": {"type": "fixed", "amount": 100},
}

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'price': product.price})
    if not created:
        cart_item.quantity += 1
        cart_item.price = product.price
        cart_item.save()
    return redirect('cart_list')

@login_required
def cart_list(request):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
    items = cart.items.all()
    return render(request, "cart/cart_list.html", {
        "cart": cart,
        "items": items,
    })

@login_required
def cart_add_item(request):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
    if request.method == "POST":
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.cart = cart
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect("cart_list")
    else:
        form = CartItemForm()
    return render(request, "cart/cart_add_items.html", {"cart": cart, "form": form, "items": cart.items.all()})

@login_required
def cart_update(request, pk):
    user = request.user
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=user)
    if request.method == "POST":
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect("cart_list")
    else:
        form = CartItemForm(instance=cart_item)
    return render(request, "cart/cart_form.html", {"form": form, "title": "Update Cart Item"})

@login_required
def cart_delete(request, pk):
    user = request.user
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=user)
    if request.method == "POST":
        cart_item.delete()
        return redirect("cart_list")
    return render(request, "cart/cart_confirm_delete.html", {"cart_item": cart_item})



@login_required
def checkout(request):
    user = request.user
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart or not cart.items.exists():
        return redirect("cart_list")

    coupon_code = request.session.get("applied_coupon")
    coupon_data = COUPONS.get(coupon_code) if coupon_code else None

    # Handle coupon application
    if request.method == "POST" and "coupon_code" in request.POST:
        code = request.POST["coupon_code"].strip()
        if code in COUPONS:
            request.session["applied_coupon"] = code
            coupon_data = COUPONS[code]
        else:
            request.session["applied_coupon"] = None
            coupon_data = None
        return redirect("checkout_page")  # reload page after applying coupon

    total = cart.grand_total()
    discounted_total = cart.grand_total(coupon_data) if coupon_data else total
    saved_amount = total - discounted_total

    return render(request, "cart/checkout.html", {
        "cart": cart,
        "items": cart.items.all(),
        "total": total,
        "discounted_total": discounted_total,
        "coupon_code": coupon_code,
        "coupon_data": coupon_data,
        "saved_amount": saved_amount,
    })


@login_required
def place_order(request):
    user = request.user
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart or not cart.items.exists():
        return redirect("cart_list")

    coupon_code = request.session.get("applied_coupon")
    coupon_data = COUPONS.get(coupon_code) if coupon_code else None

    total = cart.grand_total(coupon_data) if coupon_data else cart.grand_total()
    order = Order.objects.create(user=user, total_amount=total, status="PENDING")

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.final_price(coupon_data)
        )

    cart.is_active = False
    cart.save()
    request.session.pop("applied_coupon", None)

    return redirect("order_detail", pk=order.id)