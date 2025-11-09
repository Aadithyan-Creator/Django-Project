from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from .forms import CartItemForm
from account.models import Account
from django.utils import timezone

def cart_list(request):
    account = Account.objects.first()
    carts = CartItem.objects.filter(cart__account=account)
    for cart in carts:
        cart.total_price = cart.subtotal()
    return render(request, 'cart/cart_list.html', {'carts': carts})

from django.utils import timezone

def cart_create(request):
    account = Account.objects.first()  # temporary for testing
    cart, created = Cart.objects.get_or_create(
        account=account,
        is_active=True,
        defaults={'created_at': timezone.now()}
    )




    
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            product = cart_item.product
            quantity = cart_item.quantity
            
            cart_item.price = product.price          
            cart_item.discount_percent = 0 

            # call directly
            if product.reduce_stock(quantity):
                cart_item.save()
                return redirect('cart_list')
            else:
                form.add_error('quantity', 'Not enough stock available')
    else:
        form = CartItemForm()

    return render(request, 'cart/cart_form.html', {'form': form})

def cart_add_items(request):
    cart = Cart.objects.filter(account=request.user, is_active=True).first()
    if not cart:
        return redirect('cart_create')

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.cart = cart
            cart_item.save()
            return redirect('cart_add_items')  # Stay on same page to add more
    else:
        form = CartItemForm()

    items = cart.items.all()
    return render(request, 'cart/cart_add_items.html', {'cart': cart, 'form': form, 'items': items})

def cart_checkout(request):
    cart = Cart.objects.filter(account=request.user, is_active=True).first()
    if cart:
        cart.is_active = False
        cart.save()
    return render(request, 'cart/checkout.html', {'cart': cart})


def cart_update(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            return redirect('cart_list')
    else:
        form = CartItemForm(instance=cart_item)
    return render(request, 'cart/cart_form.html', {'form': form, 'title': 'Create Cart Item'})


def cart_delete(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    if request.method == 'POST':
        cart_item.delete()
        return redirect('cart_list')
    return render(request, 'cart/cart_confirm_delete.html', {'cart': cart_item})
