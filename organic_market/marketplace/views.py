from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .models import Product, Category, CartItem, Order, OrderItem, Review, User, CustomerQuery
from .forms import UserRegistrationForm, ProductForm, CheckoutForm, UpdateStockForm, ReviewForm, CategoryForm
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm 
from .forms import CheckoutForm, PaymentForm
from .models import OrderItem, Payment
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from .forms import UserRegistrationForm, ProductForm, CheckoutForm, UpdateStockForm, ReviewForm, CategoryForm, CustomerQueryForm
from .forms import CustomerQueryForm






def home(request):
    products = Product.objects.filter(status='approved').order_by('-created_at')[:8]
    return render(request, 'marketplace/home.html', {'products': products})

def products_list(request):
    qs = Product.objects.filter(status='approved')  # ✅ FIX
    category_slug = request.GET.get('category')
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'marketplace/products_list.html', {
        'products': qs,
        'categories': categories
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status='approved')

    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'marketplace/register.html', {'form': form})


def login_view(request):
    
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'marketplace/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'farmer':
        return redirect('farmer_dashboard')
    else:
        return redirect('customer_dashboard')

# Admin
def admin_required(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(admin_required)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_farmers = User.objects.filter(role='farmer').count()
    recent_orders = Order.objects.order_by('-created_at')[:10]
    return render(request, 'marketplace/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_farmers': total_farmers,
        'recent_orders': recent_orders
    })

@user_passes_test(admin_required)
def manage_farmers(request):
    farmers = User.objects.filter(role='farmer')
    return render(request, 'marketplace/manage_farmers.html', {'farmers': farmers})

@user_passes_test(admin_required)
def manage_customers(request):
    customers = User.objects.filter(role='customer')
    return render(request, 'marketplace/manage_customers.html', {'customers': customers})

@user_passes_test(admin_required)
def approve_products(request):
    pending = Product.objects.filter(status='pending')
    if request.method == 'POST':
        pid = request.POST.get('product_id')
        action = request.POST.get('action')
        prod = get_object_or_404(Product, id=pid)
        if action == 'approve':
            prod.status = 'approved'
        elif action == 'reject':
            prod.status = 'rejected'
        prod.save()
        return redirect('approve_products')
    return render(request, 'marketplace/approve_products.html', {'pending': pending})

@user_passes_test(admin_required)
def categories_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    categories = Category.objects.all()
    return render(request, 'marketplace/categories.html', {'categories': categories, 'form': form})

@user_passes_test(admin_required)
def delete_category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    return redirect('categories')

# Farmer
def farmer_required(user):
    return user.is_authenticated and user.role == 'farmer'

@user_passes_test(farmer_required)
def farmer_dashboard(request):
    my_products = Product.objects.filter(farmer=request.user)
    return render(request, 'marketplace/farmer_dashboard.html', {'my_products': my_products})

@user_passes_test(farmer_required)

def list_products(request):
    products = Product.objects.filter(farmer=request.user)

    for product in products:
        product.avg_rating = product.reviews.aggregate(
            Avg('rating')
        )['rating__avg'] or 0

    return render(request, 'marketplace/farmer_products.html', {
        'products': products
    })

@user_passes_test(farmer_required)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.farmer = request.user
            prod.status = 'pending'
            prod.save()
            messages.success(request, "Product added and pending approval.")
            return redirect('list_products')
    else:
        form = ProductForm()
    return render(request, 'marketplace/add_product.html', {'form': form})

@user_passes_test(farmer_required)
def edit_product(request, pk):
    prod = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect('list_products')
    else:
        form = ProductForm(instance=prod)
    return render(request, 'marketplace/edit_product.html', {'form': form, 'product': prod})

@user_passes_test(farmer_required)
def delete_product(request, pk):
    prod = get_object_or_404(Product, pk=pk, farmer=request.user)
    prod.delete()
    messages.success(request, "Product deleted.")
    return redirect('list_products')

@user_passes_test(farmer_required)
def update_stock(request, pk):
    prod = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = UpdateStockForm(request.POST, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock/price updated.")
            return redirect('list_products')
    else:
        form = UpdateStockForm(instance=prod)
    return render(request, 'marketplace/update_stock.html', {'form': form, 'product': prod})

@user_passes_test(farmer_required)
def track_orders(request):
    order_items = OrderItem.objects.filter(product__farmer=request.user).select_related('order', 'product')
    return render(request, 'marketplace/track_orders.html', {'order_items': order_items})

@user_passes_test(farmer_required)
def customer_queries(request):
    queries = CustomerQuery.objects.filter(farmer=request.user).order_by('-created_at')
    return render(request, 'marketplace/customer_queries.html', {'queries': queries})

@user_passes_test(farmer_required)
def respond_query(request, pk):
    q = get_object_or_404(CustomerQuery, id=pk, farmer=request.user)
    if request.method == 'POST':
        q.response = request.POST.get('response')
        q.responded_at = timezone.now()
        q.save()
        messages.success(request, "Response saved.")
        return redirect('customer_queries')
    return render(request, 'marketplace/respond_query.html', {'q': q})

# Customer
# views.py
from django.shortcuts import render
from .models import Product

def customer_dashboard(request):
    products = Product.objects.filter(status='approved')  # ✅ FIX
    return render(request, 'marketplace/customer_dashboard.html', {
        'products': products
    })



# views.py
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        status='approved'   # ✅ FIX
    )

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        customer=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('customer_dashboard')







@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total': total
    })



@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, customer=request.user)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    return redirect('cart')

@login_required
def remove_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, customer=request.user)
    item.delete()
    return redirect('cart')



@login_required
def orders_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'marketplace/orders.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    return render(request, 'marketplace/order_detail.html', {'order': order})

@login_required
def rate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = product
            rev.customer = request.user
            rev.save()
            messages.success(request, "Thank you for rating!")
    return redirect('product_detail', pk=pk)
def reports(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_farmers = User.objects.filter(role='farmer').count()
    recent_orders = Order.objects.order_by('-created_at')[:10]

    return render(request, 'marketplace/reports.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_farmers': total_farmers,
        'recent_orders': recent_orders,
    })



def about_us(request):
    return render(request, 'marketplace/about_us.html')

def contact_us(request):
    if request.method == 'POST':
        # You can handle the form submission here
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Message from {name} ({email}): {message}")
        # Redirect to a thank you page or reload
        return HttpResponseRedirect(reverse('contact_us'))
    return render(request, 'marketplace/contactus.html')

@login_required
def rate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = product
            rev.customer = request.user
            rev.save()
            messages.success(request, "Thank you for rating!")
    return redirect('product_detail', pk=pk)

def cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your cart.")
        return redirect('login')

    cart_items = CartItem.objects.filter(customer=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'marketplace/cart.html', {'cart_items': cart_items, 'total': total})

# Checkout view
# views.py

@login_required
def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to checkout.")
        return redirect('login')

    cart_items = CartItem.objects.filter(customer=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if form.is_valid() and payment_form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.customer = request.user
            order.total = sum(item.product.price * item.quantity for item in cart_items)
            order.save()

            # Add cart items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Reduce stock
                item.product.stock -= item.quantity
                item.product.save()

            # Create payment
            payment = payment_form.save(commit=False)
            payment.order = order
            payment.success = True if payment.method == 'cod' else False  # assume COD is successful
            payment.save()

            cart_items.delete()
            messages.success(request, "Order placed successfully!")
            return redirect('order_success')

    else:
        form = CheckoutForm()
        payment_form = PaymentForm()

    return render(request, 'marketplace/checkout.html', {
        'form': form,
        'payment_form': payment_form,
        'cart_items': cart_items
    })
# Order success view
def order_success(request):
    return render(request, 'marketplace/order_success.html')
@user_passes_test(admin_required)
def admin_toggle_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('manage_farmers')


@user_passes_test(admin_required)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_farmers')


@user_passes_test(admin_required)
def admin_farmer_products(request, farmer_id):
    farmer = get_object_or_404(User, id=farmer_id, role='farmer')
    products = Product.objects.filter(farmer=farmer)
    return render(request, 'marketplace/admin_farmer_products.html', {
        'farmer': farmer,
        'products': products
    })
@user_passes_test(admin_required)
def admin_customer_orders(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, role='customer')
    orders = Order.objects.filter(customer=customer)
    return render(request, 'marketplace/admin_customer_orders.html', {
        'customer': customer,
        'orders': orders
    })
from django.db.models import Sum

@user_passes_test(admin_required)
def manage_customers(request):
    customers = User.objects.filter(role='customer').annotate(
        total_spent=Sum('orders__total')
    )
    return render(request, 'marketplace/manage_customers.html', {
        'customers': customers
    })


@user_passes_test(admin_required)
def admin_customer_orders(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, role='customer')
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'marketplace/admin_customer_orders.html', {
        'customer': customer,
        'orders': orders
    })


@user_passes_test(admin_required)
def admin_toggle_customer(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, role='customer')
    customer.is_active = not customer.is_active
    customer.save()
    return redirect('manage_customers')
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test

from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(admin_required)
def manage_customers(request):
    customers = User.objects.filter(role='customer').annotate(
        total_spent=Sum('orders__total_amount')
    )

    return render(request, 'marketplace/manage_customers.html', {
        'customers': customers
    })
def admin_farmer_products(request, farmer_id):
    farmer = get_object_or_404(User, id=farmer_id, role='farmer')
    products = Product.objects.filter(farmer=farmer)

    return render(request, 'marketplace/farmer_products.html', {
        'farmer': farmer,
        'products': products
    })
# views
def submit_query(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = CustomerQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.product = product   # ✅ correct
            query.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = CustomerQueryForm()

    return render(request, 'marketplace/submit_query.html', {
        'form': form,
        'product': product
    })


# views.py
@user_passes_test(lambda u: u.is_authenticated and u.is_farmer())
def respond_query(request, query_id):
    query = get_object_or_404(CustomerQuery, id=query_id, farmer=request.user)

    if request.method == 'POST':
        response = request.POST.get('response')
        if response:
            query.response = response
            query.responded_at = timezone.now()
            query.save()
            messages.success(request, "Response sent successfully.")
        return redirect('farmer_queries')

    return render(request, 'marketplace/respond_query.html', {'query': query})
# views.py
@user_passes_test(lambda u: u.is_authenticated and u.is_farmer())
def farmer_queries(request):
    queries = CustomerQuery.objects.filter(farmer=request.user).order_by('-created_at')
    return render(request, 'marketplace/farmer_queries.html', {'queries': queries})
from django.contrib.auth.decorators import login_required

@login_required
def customer_queries(request):
    queries = CustomerQuery.objects.filter(
        product__farmer=request.user   # 👈 THIS IS THE KEY FIX
    ).select_related('product')

    return render(request, 'marketplace/farmer_queries.html', {
        'queries': queries
    })
