from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import mark_safe
from django.core.validators import RegexValidator

class User(AbstractUser):
    STUDENT = 'student'
    STAFF = 'staff'
    USER_TYPE_CHOICES = [
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
    ]
    
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=9,  # Set to 9 since student numbers are at most 9 digits
        validators=[RegexValidator(regex=r'^\d{5,9}$', message="Enter a valid Student No./Staff No. (5 or 9 digits).")]
    )
    name = models.CharField(max_length=100, null=True, blank=True, default='')
    phone = models.CharField(max_length=100, null=True, blank=True, default='')
    bio = models.CharField(max_length=100, null=True, blank=True, default='')
    image = models.ImageField(upload_to='account-images', default="user.jpg")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Automatically set user_type based on username length
        if len(self.username) == 9:
            self.user_type = self.STUDENT
        elif len(self.username) == 5:
            self.user_type = self.STAFF
        super().save(*args, **kwargs)

    def user_image(self):
        return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

    def __str__(self):
        return self.username
