from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem

@login_required
def create_order(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart or not cart.items.exists():
        return redirect("cart_list")

    total = sum(item.quantity * item.price for item in cart.items.all())

    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        status="PENDING"
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.price
        )

    cart.is_active = False
    cart.save()

    return redirect("order_detail", pk=order.id)


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = order.items.all()

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items
    })
    
    
def order_delete(request, pk):
    user = request.user
    order = get_object_or_404(Order, pk=pk, user=user)

    if request.method == "POST":
        order.delete()
        return redirect("order_list")

    return render(request, "order/order_confirm_delete.html", {"order": order})


