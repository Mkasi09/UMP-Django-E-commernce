from multiprocessing import context
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Avg, F, ExpressionWrapper, DecimalField
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.urls import reverse
from core.models import Payment, Product, Category, Vendor, CartOrder, CartOrderItems, \
ProductImages, ProductReview, Wishlist, Address, ContactUs
from core.forms import ProductReviewFrom
from taggit.models import Tag
from django.views.decorators.csrf import csrf_exempt
from .models import Order, CartOrderItems  # Ensure your models are imported
import uuid
from django.conf import settings
from django.contrib import messages

def index(request):
    products = Product.objects.filter(product_status='published', featured=True)

    # Dynamically determine the user type based on the logged-in user
    if request.user.is_authenticated:
        user_type = request.user.user_type  # Assuming user_type is stored in your User model
    else:
        user_type = None

    special_offers = Product.objects.filter(product_status='published').annotate(
        discount_percentage=ExpressionWrapper(
            (F('old_price') - F('student_price' if user_type == 'student' else 'staff_price')) / F('old_price') * 100,
            output_field=DecimalField()
        )
    ).order_by('-discount_percentage')[:9]

    oldest_products = Product.objects.filter(product_status='published').order_by('date')

    context = {
        "products": products,
        "special_offers": special_offers,
        "oldest_products": oldest_products,
        "user_type": user_type,  # Pass the user_type to the template
    }
    return render(request, 'core/index.html', context)


def products_list_view(request):
	products = Product.objects.filter(product_status='published')
	user_type = request.user.user_type if request.user.is_authenticated else None
	context = {
		"products": products,
		"user_type": user_type,
	}
	return render(request, 'core/product-list.html', context)

def category_list_view(request):
	categories = Category.objects.all()
	context = {
		"categories": categories,
	}
	return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
	category = Category.objects.get(cid=cid)
	products = Product.objects.filter(product_status='published', category=category)
	context = {
		"category": category,
		"products": products,
	}
	return render(request, 'core/category-products-list.html', context)

def vendor_list_view(request):
	vendors = Vendor.objects.all()
	context = {
		'vendors': vendors,
	}
	return render(request, 'core/vendor-list.html', context)

def vendor_detail_view(request, vid):
	vendor = Vendor.objects.get(vid=vid)
	products = Product.objects.filter(product_status='published', vendor=vendor)
	context = {
		'vendor': vendor,
		'products': products,
	}
	return render(request, 'core/vendor-detail.html', context)

def product_detail_view(request, pid):
	product = Product.objects.get(pid=pid)
	# product = get_object_or_404(Product, pid=pid)
	products = Product.objects.filter(category=product.category).exclude(pid=pid)
	p_image = product.p_images.all()

	reviews = ProductReview.objects.filter(product=product).order_by('-date')
	average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
	review_form = ProductReviewFrom()

	make_review = True
	if request.user.is_authenticated:
		user_review_count = ProductReview.objects.filter(user=request.user, product=product).count() 

		if user_review_count > 0:
			make_review = False

	context = {
		'product': product,
		'p_image': p_image,
		'products': products,
		'reviews': reviews,
		'average_rating': average_rating,
		'review_form': review_form,
		'make_review': make_review,
	}
	return render(request, 'core/product-detail.html', context)

def tags_list(request, tag_slug=None):
	products = Product.objects.filter(product_status='published').order_by('-id')

	tag = None
	if tag_slug:
		tag = Tag.objects.get(slug=tag_slug)
		# tag = get_object_or_404(Tag, slug=tag_slug)
		products = products.filter(tags__in=[tag])

	context = {
		'products': products,
		'tag': tag,
	}

	return render(request, 'core/tag.html', context)

def ajax_add_review(request, pid):
	product = Product.objects.get(pk=pid)
	user = request.user
	image = user.image.url

	review = ProductReview.objects.create(
		user=user,
		product=product,
		review=request.POST['review'],
		rating=request.POST['rating'],
	)
	
	context = {
		'user': user.username,
		'review': request.POST['review'],
		'rating': request.POST['rating'],
		'image': image
	}

	average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))


	return JsonResponse(
		{
			'bool': True,
			'context': context,
			'average_reviews': average_reviews,
		}
	)

def search_view(request):
	# query = request.GET['q'] OR
	query = request.GET.get('q') 

	products = Product.objects.filter(title__icontains=query).order_by('-date')

	context = {
		'products': products,
		'query': query,
	}

	return render(request, 'core/search.html', context)

def filter_product(request):
	categories = request.GET.getlist('category[]')
	vendors = request.GET.getlist('vendor[]')

	min_price = request.GET.get('min_price')
	max_price = request.GET.get('max_price')

	products = Product.objects.filter(product_status='published').order_by('-id').distinct()

	products = products.filter(price__gte=min_price)
	products = products.filter(price__lte=max_price)

	if len(categories) > 0:
		products = products.filter(category_id_in=categories).distinct()
	if len(vendors) > 0:
		products = products.filter(vendor_id_in=vendors).distinct()

	context = {
		'products': products
	}

	data = render_to_string('core/async/product-list.html', context)
	return JsonResponse({'data': data})

def add_to_cart(request):
	cart_product = {}

	cart_product[str(request.GET['id'])] = {
		'qty': request.GET['qty'],
		'title': request.GET['title'],
		'price': request.GET['price'],
		'image': request.GET['image'],
		'pid': request.GET['pid'],
	}

	if 'cart_data_object' in request.session:
		if str(request.GET['id']) in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
			cart_data.update(cart_data)
			request.session['cart_data_object'] = cart_data
		else:
			cart_data = request.session['cart_data_object']
			cart_data.update(cart_product)
			request.session['cart_data_object'] = cart_data
	else:
		request.session['cart_data_object'] = cart_product

	return JsonResponse({
			'data':request.session['cart_data_object'],
			'totalcartitems':len(request.session['cart_data_object'])
		})

def cart_view(request):
	cart_total_amount = 0
	if 'cart_data_object' in request.session:
		for product_id, item in request.session['cart_data_object'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])

		return render(request, 'core/cart.html', {
			'cart_data': request.session['cart_data_object'],
			'totalcartitems': len(request.session['cart_data_object']),
			'cart_total_amount': cart_total_amount
		})
		
	else:
		return render(request, 'core/cart.html')

def delete_from_cart(request):
	product_id = str(request.GET['id'])
	if 'cart_data_object' in request.session:
		if product_id in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			del request.session['cart_data_object'][product_id]
			request.session['cart_data_object'] = cart_data

	cart_total_amount = 0
	if 'cart_data_object' in request.session:
		for product_id, item in request.session['cart_data_object'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])

	context = render_to_string('core/async/cart-list.html', {
			'cart_data': request.session['cart_data_object'],
			'totalcartitems': len(request.session['cart_data_object']),
			'cart_total_amount': cart_total_amount
		})
	return JsonResponse({
			'data': context,
			'totalcartitems': len(request.session['cart_data_object']),
		})

def update_cart(request):
	product_id = str(request.GET['id'])
	product_qty = request.GET['qty']
	if 'cart_data_object' in request.session:
		if product_id in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			cart_data[str(request.GET['id'])]['qty'] = product_qty
			request.session['cart_data_object'] = cart_data

	cart_total_amount = 0
	if 'cart_data_object' in request.session:
		for product_id, item in request.session['cart_data_object'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])


	context = render_to_string('core/async/cart-list.html', {
			'cart_data': request.session['cart_data_object'],
			'totalcartitems': len(request.session['cart_data_object']),
			'cart_total_amount': cart_total_amount
		})
	return JsonResponse({
			'data': context,
			'totalcartitems': len(request.session['cart_data_object']),
		})


@login_required
def wishlist_view(request):
    # Directly filter the wishlist for the authenticated user
    wishlist = Wishlist.objects.filter(user=request.user)
    
    # Create context
    context = {
        'wishlist': wishlist,
    }
    
    return render(request, 'core/wishlist.html', context)

@login_required
def add_to_wishlist(request):
	product_id = request.GET['id']
	product = Product.objects.get(id=product_id)

	context = {}

	wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()

	if wishlist_count > 0:
		context	= {
			'bool': True,
			'wishlist_count': Wishlist.objects.filter(user=request.user).count()
		}
	else:
		new_wishlist = Wishlist.objects.create(
			product=product,
			user=request.user
		)
		context = {
			'bool': True,
			'wishlist_count': Wishlist.objects.filter(user=request.user).count()
		}

	return JsonResponse(context)

def remove_from_wishlist(request):
	product_id = request.GET['id']
	wishlist = Wishlist.objects.filter(user=request.user)

	product = Wishlist.objects.get(id=product_id)
	product.delete()

	context = {
		'bool': True,
		'wishlist': wishlist
	}
	qs_json = serializers.serialize('json', wishlist)
	data = render_to_string('core/async/wishlist-list.html', context)
	return JsonResponse({'data': data, 'wishlist': qs_json})

def contact(request):
	return render(request, 'core/contact.html')

def ajax_contact_form(request):
	name = request.GET['name']
	email = request.GET['email']
	message = request.GET['message']

	contact = ContactUs.objects.create(
		name=name,		
		email=email,		
		message=message,		
	)

	data = {
		'bool': True,
	}

	return JsonResponse({'data': data})

def about(request):
	return render(request, 'core/about.html')

#payments
from django.shortcuts import render
from django.conf import settings
import requests
import urllib.parse
import hashlib

def data_to_string(data_dict):
    """
    Convert dictionary to parameter string.
    """
    pf_output = '&'.join([f"{key}={urllib.parse.quote_plus(str(val).strip())}" for key, val in data_dict.items() if val != ''])
    return pf_output

def generate_payment_identifier(data):
    """
    Send the PayFast payment request to get UUID for onsite payment using the sandbox environment.
    """
	#change to live payment
    url = "https://sandbox.payfast.co.za/eng/process"
    
    # Create the PayFast string data with signature
    data_string = data_to_string(data)
    
    # Send the request to PayFast
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(url, data=data_string, headers=headers)
        response_data = response.json()

        if response_data.get('uuid'):
            return response_data['uuid']
        else:
            print("Error in PayFast response:", response_data)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def generate_signature(data, passphrase=None):
    """
    Generate a signature for the data using an optional passphrase.
    """
    pf_output = '&'.join([f"{key}={urllib.parse.quote_plus(str(val).strip())}" for key, val in data.items() if val != ''])
    
    if passphrase:
        pf_output += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
    
    return hashlib.md5(pf_output.encode('utf-8')).hexdigest()


from django.conf import settings
from django.shortcuts import render
import uuid
def checkout(request):
    cart_total_amount = 0
    discount_amount = float(request.session.get('discount_amount', 0) or 0)

    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

        final_total = cart_total_amount - discount_amount

        # Retrieve any session messages for display
        error_message = request.session.pop('coupon_error', None)
        success_message = request.session.pop('success', None)
    else:
        return redirect('core:cart')

    # Prepare PayFast data using final_total
    data = {
        'merchant_id': settings.PAYFAST_MERCHANT_ID,
        'merchant_key': settings.PAYFAST_MERCHANT_KEY,
        'amount': f"{final_total:.2f}",
        'item_name': 'Cart Items',
        'name_first': 'First Name',
        'name_last': 'Last Name',
        'email_address': 'test@test.com',
        'm_payment_id': str(uuid.uuid4()),
        'return_url': settings.PAYFAST_RETURN_URL,
        'cancel_url': settings.PAYFAST_CANCEL_URL,
        'notify_url': settings.PAYFAST_NOTIFY_URL,
    }

    context = {
        'cart_total_amount': cart_total_amount,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'error': error_message,
        'success': success_message,
        'payfast_data': data,
    }
    return render(request, 'core/checkout.html', context)

@csrf_exempt
def payfast_return(request):
    payment_status = "COMPLETE"  # This should be fetched from PayFast
    order_number = request.GET.get('m_payment_id')  # This should correspond to the unique ID

    if payment_status == "COMPLETE":
        # Payment was successful; process the order.
        cart_data = request.session.get('cart_data_object', {})
        cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in cart_data.values())

        # Create Order
        order = Order.objects.create(
            order_number=f"UMP-{str(uuid.uuid4())[:12].upper()}",  # Ensure the order number is unique
            user=request.user,
            total_amount=cart_total_amount,
        )

        # Create Order Items
        for product_id, item in cart_data.items():
            CartOrderItems.objects.create(
                order=order,
                invoice_no=str(uuid.uuid4()),  # Unique invoice number for each item
                item=item['title'],
                image=item['image'],  # Store the image URL from the cart
                price=item['price'],
                qty=item['qty'],
            )

        # Clear cart data and redirect to order confirmation
        request.session['cart_data_object'] = {}
        messages.success(request, 'Your payment was successful! Thank you for your order.')
        return HttpResponseRedirect(reverse('core:order-confirmation',args=[order.id]))

    # Handle payment failure or cancellation
    messages.error(request, 'Your payment was not successful. Please try again.')
    return HttpResponseRedirect(reverse('core:payment_cancel'))


from django.shortcuts import render, get_object_or_404
from .models import Order

def order_confirmation(request, order_id):
    # Retrieve the order and associated items
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()  # Fetches CartOrderItems associated with the order
    for item in items:
        item.total = item.price * item.qty 
    # Calculate the subtotal
    subtotal = sum(item.price * item.qty for item in items)

    context = {
        'order': order,
        'items': items,
        'subtotal': subtotal,
    }

    # Retrieve the user from the order (ensure `user` is a field on the Order model)
    user = order.user

    # Send the order confirmation email
    send_order_confirmation_email(user, order)

    return render(request, 'core/order_confirmation.html', context)


@csrf_exempt
def payment_notify(request):
    if request.method == 'POST':
        received_data = request.POST.dict()
        received_signature = received_data.pop('signature', None)

        if received_signature != generate_signature(received_data, settings.PAYFAST_PASSPHRASE):
            return HttpResponse("Invalid signature", status=400)

        try:
            response = requests.post('https://sandbox.payfast.co.za/eng/query/validate', data=request.POST)
            if response.text == 'VALID':
                payment_id = request.POST.get('pf_payment_id')
                payment = get_object_or_404(Payment, payfast_id=payment_id)
                payment.status = 'Complete'
                payment.save()
                return HttpResponse("Payment status updated", status=200)
            else:
                return HttpResponse("Payment validation failed", status=400)
        except requests.RequestException:
            return HttpResponse("Error communicating with PayFast", status=500)

    return render(request, 'core/payment_notify.html')

def payment_cancel(request):
    # Clear the cart session
    request.session['cart_data_object'] = {}

    # Provide feedback to the user
    return render(request, 'core/payment-cancel.html', {
        'message': 'Your payment has been canceled. You can return to the cart and try again.'
    })

from django.shortcuts import redirect, render
from .models import Order

def order_list(request):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    # Get the orders for the current user, using prefetch_related for efficiency
    orders = Order.objects.filter(user=request.user).prefetch_related('items')

    context = {
        'orders': orders,
    }
    return render(request, 'core/order_list.html', context)





from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    # Fetch the order object or return 404 if not found
    order = get_object_or_404(Order, id=order_id)
    
    # Fetch all items associated with the order
    items = order.items.all()
    
    # Calculate the total for each item (if needed for display)
    for item in items:
        item.total = item.price * item.qty  # Calculate total per item
    
    # Pass the order and items to the template
    return render(request, 'core/order_detail.html', {'order': order, 'items': items})


from django.views.generic import ListView, DetailView
from .models import Order
from django.db.models import Prefetch

class OrderListView(ListView):
    model = Order
    template_name = 'core/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Prefetch related items to optimize database queries
        return Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('items', queryset=CartOrderItems.objects.all())
        )
# Order detail view
class OrderDetailView(DetailView):
    model = Order
    template_name = 'core/order_detail.html'

    def get_object(self):
        order_id = self.kwargs.get('order_id')  # Ensure this matches your URL pattern
        return get_object_or_404(Order, id=order_id)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        # Fetch the order object
        order = self.get_object()

        # Fetch CartOrderItems associated with the order
        items = order.items.all()  # Adjust if your related name is different

        # Calculate the total for each item and the subtotal
        for item in items:
            item.total = item.price * item.qty
        
        # Calculate the subtotal
        subtotal = sum(item.price * item.qty for item in items)

        # Update context with order, items, and subtotal
        context['order'] = order
        context['items'] = items
        context['subtotal'] = subtotal
        
        # Retrieve the user from the order (ensure `user` is a field on the Order model)
        context['user'] = order.user

        return context
	
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(user, order):
    subject = 'Your Order Confirmation'
    
    # Extract items and calculate subtotal
    items = order.items.all()  # Ensure order has a related items field
    subtotal = sum(item.price * item.qty for item in items)  # Calculate subtotal
    for item in items:
        item.total = item.price * item.qty 
    # Render the HTML message with additional context
    html_message = render_to_string('core/order_confirmation_email.html', {
        'user': user,
        'items': items,
        'subtotal': subtotal,
    })
    recipient_list = [user.email]
    
    # Send email with HTML content
    send_mail(
        subject,
        '',  # Plain text message is empty
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message
    )

#Coupons
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import Coupon, UserCoupon

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True, expiration_date__gte=timezone.now())
                
                # Get the current cart total amount to check against minimum spend
                cart_total_amount = 0
                if 'cart_data_object' in request.session:
                    for item in request.session['cart_data_object'].values():
                        cart_total_amount += int(item['qty']) * float(item['price'])

                # Check if the cart total meets the minimum spend requirement
                if cart_total_amount < coupon.minimum_spend:
                    request.session['coupon_error'] = f'Minimum spend of {coupon.minimum_spend} required to apply this coupon.'
                else:
                    if not UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
                        discount_amount = coupon.discount_amount
                        request.session['coupon_code'] = coupon_code
                        request.session['discount_amount'] = float(discount_amount)
                        UserCoupon.objects.create(user=request.user, coupon=coupon)
                        
                        # Set success message
                        request.session['success'] = 'Coupon applied successfully!'
                    else:
                        request.session['coupon_error'] = 'You have already used this coupon.'

            except Coupon.DoesNotExist:
                request.session['coupon_error'] = 'Invalid or expired coupon.'

    return redirect(reverse('core:checkout'))


def clear_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    return redirect('core:checkout')
