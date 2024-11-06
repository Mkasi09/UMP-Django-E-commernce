from datetime import timezone
from django.contrib import admin
from core.models import Coupon, Order, Product, Category, UserCoupon, Vendor, CartOrder, CartOrderItems, \
ProductImages, ProductReview, Wishlist, Address, ContactUs

class ProductImagesAdmin(admin.TabularInline):
	model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'product_image', 'get_price', 'category', 'vendor', 'featured', 'product_status', 'pid']
    
    def get_queryset(self, request):
        # Store the user type in the request object
        self.user_type = getattr(request.user, 'user_type', None)  # Assuming user_type is an attribute on your User model
        return super().get_queryset(request)

    def get_price(self, obj):
        """ Returns the price based on user type (student or staff). """
        if self.user_type == 'student':  # Check if the user is a student
            return obj.student_price
        elif self.user_type == 'staff':  # Check if the user is staff
            return obj.staff_price
        return obj.price  # Default to general price if user type is unknown

    get_price.short_description = 'Price'  # Set a custom label for the column

class CartOrderItemsInline(admin.TabularInline):
    model = CartOrderItems
    fields = ['product_status', 'item', 'qty', 'price', 'total']
    readonly_fields = ['total']
    extra = 0  # Number of empty `CartOrderItems` forms to display if creating a new order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'created_at', 'status', 'total_amount']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__username']
    inlines = [CartOrderItemsInline]  # Adds the inline items for each order

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Calculate the total amount based on items
        

class CategotyAdmin(admin.ModelAdmin):
	list_display = ['title', 'category_image', 'cid']

class VendorAdmin(admin.ModelAdmin):
	list_display = ['title', 'vendor_image', 'vid']

# class CartOrderAdmin(admin.ModelAdmin):
# 	list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status']

# class CartOrderItemsAdmin(admin.ModelAdmin):
# 	list_display = ['order', 'invoice_no', 'item', 'image', 'qty', 'price', 'total']

class ProductReviewAdmin(admin.ModelAdmin):
	list_display = ['user', 'product', 'rating']

class WishlistAdmin(admin.ModelAdmin):
	list_display = ['user', 'product', 'date']

# class AddressAdmin(admin.ModelAdmin):
# 	list_display = ['user', 'address', 'status']

class ContactUsAdmin(admin.ModelAdmin):
	list_display = ['name', 'email']
      

      #coupon   
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_amount', 'expiration_date', 'active','minimum_spend']
    search_fields = ['code']
    list_filter = ['active', 'expiration_date']

class UserCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'used_at']
    search_fields = ['user_username', 'coupon_code']

    def save_model(self, request, obj, form, change):
        """Check if the user coupon is valid and if the minimum spend is met."""
        if obj.coupon.expiration_date < timezone.now():
            raise ValueError("Coupon has expired.")
        
        if obj.spend_amount < obj.coupon.minimum_spend:
            raise ValueError(f"Minimum spend of {obj.coupon.minimum_spend} not met.")

        obj.save()	

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategotyAdmin)
admin.site.register(Vendor, VendorAdmin)
# admin.site.register(CartOrder, CartOrderAdmin)
# admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
# admin.site.register(Address, AddressAdmin)
admin.site.register(ContactUs, ContactUsAdmin)

admin.site.register(Order, OrderAdmin)
admin.site.register(CartOrderItems)

#Coupon 
admin.site.register(Coupon)
admin.site.register(UserCoupon)