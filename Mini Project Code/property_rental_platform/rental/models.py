from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    # Add custom fields here if needed
    role = models.CharField(max_length=15)  # For custom user roles, if needed

    def __str__(self):
        return self.username  # You can use any field for representation

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    current_address = models.CharField(max_length=255, null=True, blank=True)
    photo_id = models.FileField(upload_to='photo_ids/', null=True, blank=True)

    def __str__(self):
        return str(self.user)

class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    current_address = models.CharField(max_length=255, null=True, blank=True)
    photo_id = models.FileField(upload_to='photo_ids/', null=True, blank=True)


    def __str__(self):
        return str(self.user)

class Property(models.Model):
    property_owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    property_type = models.CharField(max_length=20, choices=[('apartment', 'Apartment'), ('house', 'House'), ('office', 'Office')])
    address = models.CharField(max_length=255)
   
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    lease_duration = models.CharField(max_length=20, choices=[('1 year', '1 Year'), ('month-to-month', 'Month-to-Month')])
    availability_date = models.DateField()
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='pending',
    )
      # Soft deletion field
    deleted = models.BooleanField(default=False)
    in_cart = models.BooleanField(default=False)


    def __str__(self):
        return self.address
   

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)  # Add a category field
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return self.image.name

class Amenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')

    # Fields specific to different property types
    squarefootage = models.PositiveIntegerField(null=True, blank=True)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    stories = models.PositiveIntegerField(null=True, blank=True)
    acresofland = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rentspace = models.CharField(max_length=8, choices=[
        ('full', 'Full'),
        ('partial', 'Partial')
    ], null=True, blank=True)
    noofrooms = models.PositiveIntegerField(null=True, blank=True)
    parkingspace = models.TextField(null=True, blank=True)
    purpose = models.TextField(null=True, blank=True)
    acrescent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.property.name


class PropertyDocument(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)  # Example: 'ownership-docs', 'financial-docs', etc.
    document = models.FileField(upload_to='property_documents/')
    
    def __str__(self):
        return f"{self.property.address} - {self.document_type}"


class RentalRequest(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)


    def __str__(self):
     return f'RentalRequest - {self.property} - {self.tenant} - Status: {self.status}'





    





