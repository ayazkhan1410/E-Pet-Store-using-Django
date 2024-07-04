from django.db import models
from .helper import *
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class CustomUser(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100)
    address = models.TextField()
    user_profile = models.ImageField(upload_to='user_profile/', default='user_profile/default.webp')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = Manager()     
    

    
    def __str__(self) -> str:
        return self.email   

    def get_cart_count(self):
        total_items = 0
        cart_items = Cart.objects.filter(user=self, is_ordered=False)
        for item in cart_items:
            total_items += item.quantity
        return total_items
    

class Category(models.Model):
    category_name = models.CharField(max_length=100, null=True, blank=True)
    category_image = models.ImageField(upload_to='images/', null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.category_name

class Product(models.Model):
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=100, null=True, blank=True)
    product_description = models.TextField()
    original_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    product_image = models.ImageField(upload_to='product_images/')
    is_stock = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    created_at = models.DateField(auto_now_add=True)
    
    @property
    def discounted_price(self):
        discount_amount = (self.discount_percentage / 100) * self.original_price
        discounted_price = self.original_price - discount_amount
        return round(discounted_price, 2)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.product_name


class Contact(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(null=True, blank = True, max_length = 100)
    message = models.TextField()
    
    def __str__(self) -> str:
        return self.email    
    
class FeatureProductImages(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    image = models.ImageField(upload_to='feature_images/')
    
    def __str__(self) -> str:
        return self.product.product_name

class Cart(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart')
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_ordered_or_deleted(self):
        if not self.is_ordered:
            self.is_ordered = True
            self.save()
    
    def __str__(self) -> str:
        return self.product.product_name

class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)