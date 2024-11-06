from django.conf import settings
from django.db import models
from django.utils.html import mark_safe
from userauths.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from shortuuid.django_fields import ShortUUIDField

STATUS_CHOICE = (
	("process", "Processing"),
	("shipped", "Shipped"),
	("delivered", "Delivered"),
)

STATUS = (
	("draft", "Draft"),
	("disabled", "Disabled"),
	("rejected", "Rejected"),
	("in_review", "In Review"),
	("published", "Published"),
)

RATING = (
	( 1, "★☆☆☆☆"),
	( 2, "★★☆☆☆"),
	( 3, "★★★☆☆"),
	( 4, "★★★★☆"),
	( 5, "★★★★★"),
)

def user_directory_path(instance, filename):
	return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
	cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='cat', alphabet='abcdefgh12345')
	title = models.CharField(max_length=100, default="Category Name")
	image = models.ImageField(upload_to='category', default="category.jpg")

	class Meta:
		verbose_name_plural = 'Categories'

	def category_image(self):
		return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

	def __str__(self):
		return self.title

class Tags(models.Model):
	pass

class Vendor(models.Model):
	vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='ven', alphabet='abcdefgh12345')
	
	title = models.CharField(max_length=100, default="Vendor Name")
	image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
	description = RichTextUploadingField(null=True, blank=True, default="Vendor Description")

	address = models.CharField(max_length=100, default="123 Main Street")
	contact = models.CharField(max_length=100, default="+123 (456) 789")
	email = models.CharField(max_length=100, default="example@mail.com")

	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

	class Meta:
		verbose_name_plural = 'Vendors'

	def vendor_image(self):
		return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

	def __str__(self):
		return self.title

class Product(models.Model):
    pid = ShortUUIDField(unique=True, max_length=30, alphabet='abcdefgh12345')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="product")

    title = models.CharField(max_length=100, default="Product Name")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = RichTextUploadingField(null=True, blank=True, default="Product Description")

    # Separate fields for student and staff prices
    student_price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
    staff_price = models.DecimalField(max_digits=10, decimal_places=2, default="2.99")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default="2.99")
    price = models.DecimalField(max_digits=10, decimal_places=2) 
	
    specifications = RichTextUploadingField(null=True, blank=True)
    stock_count = models.PositiveIntegerField(default=10, null=True, blank=True)
    shipping = models.CharField(max_length=100, default="1", null=True, blank=True)
    weight = models.CharField(max_length=100, default="0.7", null=True, blank=True)
    life = models.CharField(max_length=100, default="10", null=True, blank=True)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    tags = TaggableManager(blank=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, max_length=30, prefix="sku", alphabet='1234567890')

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Products'

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        """ Calculate discount percentage """
        new_price = ((self.old_price - self.get_price()) / self.old_price) * 100
        return new_price

    def get_price(self):
        """ Determine price based on user type (student or staff) """
        if self.user.user_type == 'student':
            return self.student_price
        return self.staff_price
		


class ProductImages(models.Model):
	images = models.ImageField(upload_to="product-images", default="product.jpg")
	product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Product Images'



####### Cart, Order #######

# Define choices for product status
STATUS_CHOICE = [
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICE, max_length=30, default='processing')


    def __str__(self):
        return f"Order #{self.id}"


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.99)  # Reasonable max_digits
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default='processing')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = 'Cart Orders'

class CartOrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default='processing')
    item = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2,)

    class Meta:
        verbose_name_plural = 'Cart Order Items'


    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50">' % self.image)

    def save(self, *args, **kwargs):
        self.total = int(self.qty) * float(self.price)  # Cast to int/float
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} - {self.qty} pcs"
	


####### Product Review, Wishlist, Address #######



class ProductReview(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='reviews')
	review = models.TextField()
	rating = models.IntegerField(choices=RATING, default=None)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Reviews'

	def __str__(self):
		return self.product.title

	def get_rating(self):
		return self.rating

class Wishlist(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Wishlists'

	def __str__(self):
		return self.product.title

class Address(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=100, null=True)
	status = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = 'Address'



####### Contact, Profile #######



class ContactUs(models.Model):
	name = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	message = models.TextField()

	class Meta:
		verbose_name = 'Contact Us'
		verbose_name_plural = 'Contact Us'

	def __str__(self):
		return self.name
	
from django.db import models
from django.conf import settings  # Import settings to access AUTH_USER_MODEL

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL here
    payfast_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Adjust as necessary
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.payfast_id} - {self.status}"

# Coupons

class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateField()
    active = models.BooleanField(default=True)
    minimum_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def _str_(self):
        return self.code

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user} - {self.coupon.code}"