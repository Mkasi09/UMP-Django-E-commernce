import random
from core.models import Product, Category, Vendor, CartOrder, \
CartOrderItems, ProductImages, ProductReview, Wishlist, Address
from blog.models import Post
from django.db.models import Min, Max
from django.contrib import messages
from taggit.models import Tag


def core_context(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    # Determine user type and set the price field accordingly
    user_profile = getattr(request.user, 'userauths', None)  # Adjust based on how you access user profiles
    user_type = user_profile.user_type if user_profile else 'student'  # Default to 'student'

    # Set the price field based on user type
    price_field = 'student_price' if user_type == 'student' else 'staff_price'

    # Calculate min and max price based on user type
    min_max_price = Product.objects.aggregate(
        min_price=Min(price_field),
        max_price=Max(price_field)
    )

    latest_products = Product.objects.filter(product_status='published').order_by('-date')

    # Safely fetch wishlist for authenticated users only
    wishlist = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user)

    all_product_tags = Tag.objects.filter(product__isnull=False).distinct()
    random_product_tags = random.sample(list(all_product_tags), min(6, len(all_product_tags)))

    blog_posts = Post.objects.filter(post_status='published').order_by("-date_created")

    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    return {
        'categories': categories,
        'vendors': vendors,
        'wishlist': wishlist,
        'min_max_price': min_max_price,
        'cart_total_amount': cart_total_amount,
        'latest_products': latest_products,
        'random_product_tags': random_product_tags,
        'blog_posts': blog_posts,
    }