from datetime import timedelta
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib import messages
from .models import CustomUser as User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
import stripe
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    category = Category.objects.all().order_by('category_name')[:5]
    context = {
        'category': category
    
    }
    return render(request, "index.html", context)

def products(request):
    products = Product.objects.all().order_by('product_name')
    
    page_numbers = request.GET.get('page', 1)
    paginator = Paginator(products, 6)
    
    try:
        paginated_products = paginator.page(page_numbers)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    context = {
        'products':paginated_products
    }
        
    return render(request, 'products.html', context)


def contact_us(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        contact_obj = Contact.objects.create(
            username = username,
            email = email,
            phone = phone,
            message = message
        )
        messages.success(request, "Your message has been recorded")
        return redirect('contact-us')
    
    return render(request, 'contact-us.html')

def about_us(request):
    return render(request, 'about-us.html')

def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')
    
    return render(request, 'login.html')

def signup(request):
    
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Account already exists')
            return redirect('signup')
        
        user_obj = User.objects.create_user(
            username=email,  # Or you can choose any username you want
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, 'Account created successfully')
        return redirect('login')
    
    return render(request, 'signup.html')

@login_required(login_url='login')
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    images = FeatureProductImages.objects.filter(product=product)
    context = {
        'product': product,
        'images': images
    }
    return render(request, 'product-detail.html',context)

def calculate_delivery_date(order_date):
    days_to_add = 5  # Number of days for delivery
    current_date = order_date
    while days_to_add > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() not in (5, 6): 
            days_to_add -= 1
    return current_date

@login_required(login_url='login')
def checkout_cart(request):
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
    delivery_date = calculate_delivery_date(timezone.now())
    total_price = sum(item.product.discounted_price * item.quantity for item in cart_items)

    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item_id = request.POST.get('cart_item_id')

        if cart_item_id:
            try:
                cart_item_id = int(cart_item_id)
                cart_item = Cart.objects.get(id=cart_item_id, user=request.user, is_ordered=False)

                if action == 'increase':
                    cart_item.quantity += 1
                elif action == 'decrease':
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                cart_item.save()

                # Recalculate total price after cart item quantity change
                cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
                total_price = sum(item.product.discounted_price * item.quantity for item in cart_items)
            except (ValueError, Cart.DoesNotExist):
                pass

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'delivery_date': delivery_date
    }
    return render(request, 'checkout-cart.html', context)

@login_required(login_url='login')
def create_checkout_session(request):
    try:
        # Collect necessary data
        email = request.user.email
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)

        # Initialize Stripe with your secret key
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create line items for each product in the cart
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(float(item.product.discounted_price) * 100),
                    'product_data': {
                        'name': item.product.product_name,  # Name of the product
                    },
                },
                'quantity': item.quantity,  # Quantity of the product
            })

        # Create a Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,  # Provide the line items data here
            mode='payment',
            success_url='http://127.0.0.1:390/checkout_complete',
            cancel_url='http://127.0.0.1:390/payment-failed',
        )

        # Redirect to the Stripe Checkout session URL
        return redirect(session.url)

    except Exception as e:
        print("Error:", e)
        messages.error(request, 'An error occurred while processing the payment. Please try again.')

    # If an error occurs or session creation fails, redirect back to the checkout page
    return redirect('payment-failed')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Retrieve the user email from the session
        user_email = session['customer_details']['email']
        cart_items = Cart.objects.filter(user__email=user_email, is_ordered=False)

        # Mark items as ordered and delete them
        for item in cart_items:
            item.mark_as_ordered_or_deleted()
            item.delete()

    return JsonResponse({'status': 'success'}, status=200)

@login_required(login_url='login')
def shipping_address(request):
    
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        shipping_obj = ShippingAddress.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            address = address
        )
        shipping_obj.save()
        return redirect('create_checkout_session')
    
    return render(request, 'shipping-address.html')

@login_required(login_url='login')
def add_to_cart(request, slug):
    user = request.user
    product = Product.objects.get(slug = slug)

    cart_item, created = Cart.objects.get_or_create(product=product, user=user, is_ordered=False)
    if created:
        cart_item.quantity = 1
        cart_item.save()
    else:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Item added to cart")
    return redirect('product-detail', slug=slug)

@login_required(login_url='login')
def checkout_cart_remove(request, slug):
    user = request.user
    product = Product.objects.get(slug = slug)
    cart_item = Cart.objects.get(product=product, user=user, is_ordered=False)
    cart_item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('checkout-cart')
    
@login_required(login_url='login')
def product_by_category(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category_name=category)
        
    context = {
        'category': category,
        'products': products
    }
    
    return render(request, 'products.html', context)

def checkout_complete(request):  
    return render(request, 'checkout_complete.html')

def payment_failed(request):
    return render(request, 'payment-failed.html')

def logout_page(request):
    logout(request)
    return redirect('/')