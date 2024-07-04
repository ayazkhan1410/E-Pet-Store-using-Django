from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'address',
        'user_profile',
    ]
    list_per_page = 10
    search_fields = ['email']

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['category_name', 'category_image', 'is_active']
    list_per_page = 10
    search_fields = ['category_name']
    list_filter = ['is_active']
    
@admin.register(Contact)
class AdminContactUs(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'message']
    list_per_page = 10
    search_fields = ['email']

@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ['category_name', 'product_name', 'product_description', 'discount_percentage', 'discounted_price', 'product_image', 'is_stock', 'slug', 'created_at', ]
    list_per_page = 10
    search_fields = ['product_name']
    
@admin.register(FeatureProductImages)
class AdminFeatureProductImages(admin.ModelAdmin):
    list_display = ['product', 'image']
    list_per_page = 10
    search_fields = ['product']

@admin.register(Cart)
class AdminCart(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'price','is_ordered']
    list_per_page = 10
    search_fields = ['user']

@admin.register(ShippingAddress)
class AdminShippingAddress(admin.ModelAdmin):
   list_display = ('first_name', 'last_name', 'email', 'phone_number', 'address', )
   list_per_page = 10
   search_fields = ['email']