from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BikeProduct(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text='Stock Keeping Unit')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text='Purchase cost')
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    
    # Specifications
    frame_size = models.CharField(max_length=50, blank=True)
    wheel_size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Auto-update status based on stock quantity
        if self.stock_quantity == 0:
            self.status = 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            self.status = 'low_stock'
        else:
            self.status = 'in_stock'
        super().save(*args, **kwargs)
    
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('gcash', 'GCash'),
        ('bank', 'Bank Transfer'),
    ]
    
    sale_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales')
    product = models.ForeignKey(BikeProduct, on_delete=models.PROTECT, related_name='sales')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_created')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sale_id} - {self.customer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Generate sale ID
        if not self.sale_id:
            date_str = timezone.now().strftime('%Y%m%d')
            count = Sale.objects.filter(sale_id__startswith=f'SALE-{date_str}').count() + 1
            self.sale_id = f'SALE-{date_str}-{count:04d}'
        
        # Calculate amounts
        self.unit_price = self.product.price
        self.total_amount = self.unit_price * self.quantity
        self.final_amount = self.total_amount - self.discount
        
        # Update product stock if completed
        is_new = self.pk is None
        old_status = None if is_new else Sale.objects.get(pk=self.pk).status
        
        if self.status == 'completed' and (is_new or old_status != 'completed'):
            # Deduct stock
            self.product.stock_quantity -= self.quantity
            self.product.save()
        elif old_status == 'completed' and self.status == 'cancelled':
            # Return stock
            self.product.stock_quantity += self.quantity
            self.product.save()
        
        super().save(*args, **kwargs)


class StockHistory(models.Model):
    ACTION_CHOICES = [
        ('add', 'Stock Added'),
        ('remove', 'Stock Removed'),
        ('adjust', 'Stock Adjusted'),
        ('sale', 'Sale'),
    ]
    
    product = models.ForeignKey(BikeProduct, on_delete=models.CASCADE, related_name='stock_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_change = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stock Histories"
    
    def __str__(self):
        return f"{self.product.sku} - {self.action} - {self.quantity_change}"
