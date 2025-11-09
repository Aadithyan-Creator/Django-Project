from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from cart.models import Cart, CartItem
from account.models import Account

def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    account = Account.objects.first()
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(account=request.user)


    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': product.price, 'quantity': 1}
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('cart_list')
