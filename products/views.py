from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from cart.models import Cart, CartItem
from account.models import Account
from django.contrib.auth.decorators import login_required

# Utility function to get categories for buttons
def get_categories():
    return Product.objects.values_list('category', flat=True).distinct()


# All products page
def all_products(request):
    products = Product.objects.all()
    categories = get_categories()
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': 'All',
        'categories': categories
    })


# Products filtered by category
def product_list(request, category):
    products = Product.objects.filter(category=category)
    categories = get_categories()
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category,
        'categories': categories
    })


# Product detail page
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = get_categories()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'categories': categories
    })


# Category navigation page (optional if you have a separate page)
def product_navigate(request):
    categories = get_categories()
    return render(request, 'products/category_list.html', {'categories': categories})


# Add product to cart
@login_required
def add_to_cart(request, product_id):
    account = Account.objects.first()

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(account=account, is_active=True)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': product.price, 'quantity': 1}
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        # else: optional: show "stock limit reached" message

    return redirect('cart_list')  # make sure cart_list URL exists
