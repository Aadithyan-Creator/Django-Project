from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required


def get_categories():
    return Product.objects.values_list('category', flat=True).distinct()


def all_products(request):
    products = Product.objects.all()
    categories = get_categories()
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': 'All',
        'categories': categories
    })


def product_list(request, category):
    products = Product.objects.filter(category=category)
    categories = get_categories()
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category,
        'categories': categories
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = get_categories()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'categories': categories
    })


def product_navigate(request):
    categories = get_categories()
    return render(request, 'products/category_list.html', {'categories': categories})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Use user instead of account
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)

    # Add or update cart item
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
