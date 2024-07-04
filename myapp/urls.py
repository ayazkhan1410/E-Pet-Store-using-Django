from django.urls import path
from myapp import views

urlpatterns = [
    path("", views.index, name='index'),
    path('about-us', views.about_us, name='about-us'),
    path('contact-us', views.contact_us, name='contact-us'),
    path('product-detail/<str:slug>', views.product_detail, name='product-detail'),
    path('login', views.login_page, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout_page, name='logout'),
    path('products', views.products, name='products'),
    
    # cart items 
    path('checkout-cart', views.checkout_cart, name='checkout-cart'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('add-to-cart/<str:slug>', views.add_to_cart, name='add-to-cart'),
    path('checkout_cart_remove/<str:slug>', views.checkout_cart_remove, name='checkout_cart_remove'),
    path('product_by_category/<int:category_id>', views.product_by_category, name='product_by_category'),
    path('shipping-address', views.shipping_address, name='shipping-address'),
    path('create_checkout_session', views.create_checkout_session, name='create_checkout_session'),
    path('checkout_complete', views.checkout_complete, name='checkout_complete'),
    path('payment-failed', views.payment_failed, name='payment-failed'),
    # path('remove_cart/<str:slug>', views.remove_cart, name='remove_cart'),

]
