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
    

class LeaseAgreement(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Lease Agreement for {self.property}'


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ServiceProviderProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=200)
    experience = models.IntegerField(null=True, blank=True)
    certification_file = models.FileField(upload_to='certifications/')
    address = models.TextField()
    approved = models.BooleanField(null=True)


    def __str__(self):
        return self.name



class Payment(models.Model):
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_order_id = models.CharField(max_length=255)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Add this line for the timestamp

    def __str__(self):
        return f"Payment for Property {self.property.id} by {self.user_profile.user.username} at {self.timestamp}"



    
class Service(models.Model):
    service_provider_profile = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE)

    
    service_name = models.CharField(max_length=255,null=True)
    service_category = models.CharField(max_length=255,null=True)
    property_type = models.CharField(max_length=255,null=True)
    service_description = models.TextField(null=True)
    service_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    location = models.CharField(max_length=255,null=True)


    def __str__(self):
        return self.service_name


class PropertyFeedback(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.property.property_name} by {self.user.username}"

class ServiceRequest(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ScheduledService(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    is_done = models.BooleanField(default=False)  # New field to track service status


     

class Pay(models.Model):
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_order_id = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Add this line for the timestamp

    def __str__(self):
        return f"Payment for Property {self.service.id} by {self.user_profile.user.username} at {self.timestamp}"


class LoanApplication(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=255)
    address = models.TextField()
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    telephone = models.CharField(max_length=15)
    email = models.EmailField()
    age = models.IntegerField()
    occupation = models.CharField(max_length=20, choices=[('Employed', 'Employed'), ('Self-employed', 'Self-employed'), ('Retired', 'Retired')])
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    property_address = models.TextField()
    nearest_bank = models.CharField(max_length=255)
    net_monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Foreign key to Property model
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='loan_applications')

    def __str__(self):
        return f"{self.applicant_name}'s Loan Application"

class Propertysell(models.Model):
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        # Add more property types as needed
    ]
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    address = models.CharField(max_length=255)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    amenities = models.TextField()
    contact_information = models.CharField(max_length=100)
    property_images = models.ImageField(upload_to='property_images/')
    ownership = models.CharField(max_length=20)
    plot_area = models.CharField(max_length=20)
    constructed_year = models.IntegerField()
    ready_to_move = models.BooleanField(default=False)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')





User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_reply = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.recipient}"


class Schedule(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_visits')
    property = models.ForeignKey('Propertysell', on_delete=models.CASCADE)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Visit for {self.property.address} by {self.tenant.username} on {self.visit_date} at {self.visit_time}"