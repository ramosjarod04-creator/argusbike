from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.contrib.auth.models import User
from .models import Category, Brand, BikeProduct, Customer, Sale, StockHistory
from .forms import RegisterForm, CategoryForm, BrandForm, BikeProductForm, CustomerForm, SaleForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .models import BikeProduct, Customer, Sale

from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin) # This strictly blocks customers
def product_update_view(request, pk):
    product = get_object_or_404(BikeProduct, pk=pk)

def is_admin(user):
    return user.is_authenticated and user.is_staff

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    if request.user.is_staff:
        context = {
            'is_admin': True,
            'total_revenue': Sale.objects.filter(status='completed').aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            'low_stock_count': BikeProduct.objects.filter(status='low_stock', is_active=True).count(),
            'total_customers': Customer.objects.count(),
            'recent_sales': Sale.objects.all().order_by('-created_at')[:5],
            'shortcuts': [
                {'name': 'Add Bike', 'url': 'product_create', 'icon': 'fas fa-plus-circle'},
                {'name': 'Sales', 'url': 'sale_list', 'icon': 'fas fa-file-invoice-dollar'},
                {'name': 'Customers', 'url': 'customer_list', 'icon': 'fas fa-users-cog'},
                {'name': 'Settings', 'url': 'category_create', 'icon': 'fas fa-sliders-h'},
            ]
        }
    else:
        context = {
            'is_admin': False,
            'featured_products': BikeProduct.objects.filter(is_featured=True, is_active=True)[:6],
            'shortcuts': [
                {'name': 'Browse Store', 'url': 'product_list', 'icon': 'fas fa-bicycle'},
                # FIXED: This now points to sale_list instead of dashboard
                {'name': 'My Order Basket', 'url': 'sale_list', 'icon': 'fas fa-shopping-basket'},
            ]
        }
    return render(request, 'shop/dashboard.html', context)
        
# ============================================
# PRODUCT VIEWS
# ============================================

@login_required
def product_list_view(request):
    products = BikeProduct.objects.filter(is_active=True)
    
    # Search and filter
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    status = request.GET.get('status', '')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(description__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    if status:
        products = products.filter(status=status)
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'search': search,
        'selected_category': category_id,
        'selected_brand': brand_id,
        'selected_status': status,
    }
    
    return render(request, 'shop/product_list.html', context)


@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(BikeProduct, pk=pk)
    stock_history = product.stock_history.all()[:10]
    
    context = {
        'product': product,
        'stock_history': stock_history,
    }
    
    return render(request, 'shop/product_detail.html', context)


@login_required
def product_create_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add products.')
        return redirect('product_list')
    
    if request.method == 'POST':
        form = BikeProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            
            # Log stock addition
            StockHistory.objects.create(
                product=product,
                action='add',
                quantity_change=product.stock_quantity,
                previous_quantity=0,
                new_quantity=product.stock_quantity,
                notes='Initial stock',
                created_by=request.user
            )
            
            messages.success(request, 'Product created successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = BikeProductForm()
    
    return render(request, 'shop/product_form.html', {'form': form, 'action': 'Create'})


@login_required
def product_update_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can edit products.')
        return redirect('product_list')
    
    product = get_object_or_404(BikeProduct, pk=pk)
    old_quantity = product.stock_quantity
    
    if request.method == 'POST':
        form = BikeProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Log stock change
            if product.stock_quantity != old_quantity:
                change = product.stock_quantity - old_quantity
                action = 'add' if change > 0 else 'remove'
                
                StockHistory.objects.create(
                    product=product,
                    action=action,
                    quantity_change=abs(change),
                    previous_quantity=old_quantity,
                    new_quantity=product.stock_quantity,
                    notes='Stock updated',
                    created_by=request.user
                )
            
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = BikeProductForm(instance=product)
    
    return render(request, 'shop/product_form.html', {'form': form, 'action': 'Update'})


@login_required
def product_delete_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can delete products.')
        return redirect('product_list')
    
    product = get_object_or_404(BikeProduct, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, 'Product deactivated successfully!')
        return redirect('product_list')
    
    return render(request, 'shop/product_confirm_delete.html', {'product': product})


# ============================================
# CUSTOMER VIEWS
# ============================================

@login_required
def customer_list_view(request):
    customers = Customer.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'customers': customers,
        'search': search,
    }
    
    return render(request, 'shop/customer_list.html', context)


@login_required
def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'shop/customer_form.html', {'form': form, 'action': 'Create'})


@login_required
def customer_update_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'shop/customer_form.html', {'form': form, 'action': 'Update'})


@login_required
def customer_delete_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    
    return render(request, 'shop/customer_confirm_delete.html', {'customer': customer})


# ============================================
# SALE VIEWS
# ============================================

@login_required
def sale_list_view(request):
    # If the user is staff/admin, show all orders
    if request.user.is_staff:
        # Changed '-date' to '-created_at'
        sales = Sale.objects.all().order_by('-created_at')
    else:
        # If the user is a customer, only show their own orders
        # Changed '-date' to '-created_at'
        sales = Sale.objects.filter(created_by=request.user).order_by('-created_at')
    
    return render(request, 'shop/sale_list.html', {'sales': sales})

@login_required
def sale_create_view(request):
    product_id = request.GET.get('product')
    product = get_object_or_404(BikeProduct, id=product_id) if product_id else None

    # This automatically finds or creates your customer profile
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'last_name': request.user.last_name or "Customer",
            'email': request.user.email,
        }
    )

    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.customer = customer
            sale.product = product
            sale.unit_price = product.price
            sale.created_by = request.user  # Crucial for the filter to work
            sale.status = 'pending'
            sale.total_amount = product.price * sale.quantity
            sale.final_amount = sale.total_amount
            sale.save()
            messages.success(request, 'Order submitted! Wait for admin review.')
            return redirect('sale_list') # Redirect straight to the basket
    else:
        form = SaleForm(initial={'quantity': 1})
    
    return render(request, 'shop/sale_form.html', {
        'form': form, 
        'product': product,
        'customer': customer
    })


@login_required
def sale_update_view(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully!')
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
    
    return render(request, 'shop/sale_form.html', {'form': form, 'action': 'Update'})


@login_required
def sale_delete_view(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        sale.status = 'cancelled'
        sale.save()
        messages.success(request, 'Sale cancelled successfully!')
        return redirect('sale_list')
    
    return render(request, 'shop/sale_confirm_delete.html', {'sale': sale})
@login_required
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            # Redirect to product creation so you can use the new category immediately
            return redirect('product_create') 
    else:
        form = CategoryForm()
    return render(request, 'shop/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def brand_create_view(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added successfully!')
            return redirect('product_create')
    else:
        form = BrandForm()
    return render(request, 'shop/brand_form.html', {'form': form, 'title': 'Add Brand'})

@login_required
def manage_sale_status(request, pk, action):
    # Only staff/admins can perform these actions
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    sale = get_object_or_404(Sale, pk=pk)

    if action == 'approve':
        sale.status = 'completed'
        sale.save()
        messages.success(request, f"Order #{sale.sale_id} has been Approved.")
    elif action == 'deny':
        sale.status = 'cancelled'
        sale.save()
        messages.warning(request, f"Order #{sale.sale_id} has been Denied.")
    elif action == 'delete':
        sale_id = sale.sale_id
        sale.delete()
        messages.error(request, f"Order #{sale_id} has been Deleted.")
    
    return redirect('dashboard') # Or 'sale_list' if you prefer