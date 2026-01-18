from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem
from apps.products.models import Product

def get_cart(request):
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return render(request, 'partials/_cart_items.html', {'cart': cart})



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from apps.products.models import Product

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()

    response = render(request, 'partials/_cart_items.html', {'cart': cart})
    # Send product name in custom HX header
    response['HX-Trigger-After'] = product.name
    return response


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Cart, CartItem

def cart_view(request):
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return render(request, 'orders/cart.html', {'cart': cart})

def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
        item.save()

    cart = item.cart
    return render(request, 'partials/_cart_items.html', {'cart': cart})

def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = item.cart
    item.delete()
    return render(request, 'partials/_cart_items.html', {'cart': cart})




from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cart #, Order
from django.views.decorators.csrf import csrf_exempt

def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return render(request, 'orders/checkout.html', {'cart': cart})

@csrf_exempt
def checkout_process(request):
    if request.method == 'POST':
        # Basic HTMX validation
        required_fields = ['first_name', 'last_name', 'email', 'address', 'city', 'state', 'postal_code', 'phone', 'payment_method']
        errors = []
        for field in required_fields:
            if not request.POST.get(field):
                errors.append(f"{field.replace('_',' ').title()} is required.")

        if errors:
            return HttpResponse("<br>".join(errors), status=400)

        # Create Order
        cart = Cart.objects.aget(session_key=request.session.session_key)
        order = Order.objects.acreate(
            cart=cart,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            postal_code=request.POST['postal_code'],
            phone=request.POST['phone'],
            payment_method=request.POST['payment_method'],
            total=cart.total
        )

        # Redirect to payment page (Paystack / Stripe integration placeholder)
        return HttpResponse(f"Order #{order.id} created! Proceed to payment.", status=200)



from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cart #, Order
from django.views.decorators.csrf import csrf_exempt

def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return render(request, 'orders/checkout.html', {'cart': cart})

@csrf_exempt
def checkout_process(request):
    if request.method == 'POST':
        # Basic HTMX validation
        required_fields = ['first_name', 'last_name', 'email', 'address', 'city', 'state', 'postal_code', 'phone', 'payment_method']
        errors = []
        for field in required_fields:
            if not request.POST.get(field):
                errors.append(f"{field.replace('_',' ').title()} is required.")

        if errors:
            return HttpResponse("<br>".join(errors), status=400)

        # Create Order
        cart = Cart.objects.get(session_key=request.session.session_key)
        order = Order.objects.create(
            cart=cart,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            postal_code=request.POST['postal_code'],
            phone=request.POST['phone'],
            payment_method=request.POST['payment_method'],
            total=cart.total
        )

        # Redirect to payment page (Paystack / Stripe integration placeholder)
        return HttpResponse(f"Order #{order.id} created! Proceed to payment.", status=200)




def cart_partial(request):
    cart = Cart(request)

    return render(
        request,
        "partials/_cart_items.html",
        {
            "cart": cart,
        },
    )
