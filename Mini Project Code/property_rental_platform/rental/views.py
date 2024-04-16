import base64
import datetime
from decimal import Decimal
from io import BytesIO
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
import razorpay
import requests
from .utils import *
from django.views.generic import View
#for activating user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string

from django.conf import settings
from django.core.mail import EmailMessage
#threading
import threading
from django.db.models import Q  # Import Q for complex queries

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import CustomUser, User,UserProfile,Profile,Property,PropertyImage,Amenity,PropertyDocument,RentalRequest,LeaseAgreement,Notification,ServiceProviderProfile,Payment,Service,PropertyFeedback,ServiceRequest,ScheduledService,Pay,LoanApplication # Import your custom user model

from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView,PasswordResetDoneView,PasswordResetCompleteView
from .utils import TokenGenerator,generate_token
from django.urls import reverse_lazy

from social_django.models import UserSocialAuth


def google_authenticate(request):
    # Handle the Google OAuth2 authentication process
    # ...

    # After successful authentication, create or get the user
    try:
        user_social = UserSocialAuth.objects.get(provider='google-oauth2', user=request.user)
        user = user_social.user
    except UserSocialAuth.DoesNotExist:
        user = request.user

    # Set a default role for users signing in with Google (e.g., "Patient")
    user.role = 'tenant'
    user.save()
    print(f"User role set to: {user.role}")

    # Redirect to the desired page (phome.html for Patient role)
    if user.role == 'tenant':
        return redirect('tenantpage')  # Make sure you have a URL named 'phome'



class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'  # Your template for the password reset form
    email_template_name = 'password_reset_email.html'  # Your email template for the password reset email
    success_url = reverse_lazy('password_reset_done')  # URL to redirect after successful form submission
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'  # Your template for password reset confirmation form
    success_url = reverse_lazy('password_reset_complete')  # URL to redirect after successful password reset
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'  # Your template for password reset done page
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'  # Your template for password reset complete page
    
class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        super().__init__()  #Call the parent class's __init_ method

    def run(self):
        self.email_message.send()

from django.db.models import Avg


def index(request):
    filtered_properties = Property.objects.filter(approval_status='Approved')
    properties_for_sale = Propertysell.objects.all()


    property_type = request.GET.get('property_type')
    min_rent = request.GET.get('min_rent')
    max_rent = request.GET.get('max_rent')

    # Create Q objects to build complex queries
    filter_params = Q()

    if property_type:
        filter_params &= Q(property_type=property_type)

    if min_rent:
        filter_params &= Q(monthly_rent__gte=min_rent)

    if max_rent: 
        filter_params &= Q(monthly_rent__lte=max_rent)

    # Apply the filters
    filtered_properties = filtered_properties.filter(filter_params)

    for property in filtered_properties:
        # Check if a rental request has been accepted for each property
        property.is_rental_request_accepted = property.rentalrequest_set.filter(status='Accepted').exists()
        property.latest_rating = PropertyFeedback.objects.filter(property=property).aggregate(Avg('rating'))['rating__avg']


    context = {
        'properties': filtered_properties,
        'properties_for_sale': properties_for_sale,

    }

    return render(request, 'index.html', context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')
        role = request.POST.get('role')  # Add role selection in your signup form

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Already Registered Email!!")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!!!")
        elif password != confirmPassword:
            messages.error(request, "Passwords do not match!!!")
        else:
            user = CustomUser(username=username, email=email, role=role)
            user.set_password(password)
            user.is_active=False  #make the user inactive
            user.save()
            current_site=get_current_site(request)  
            email_subject="Activate your account"
            message=render_to_string('activate.html',{
                   'user':user,
                   'domain':current_site.domain,
                   'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                   'token':generate_token.make_token(user)


            })

            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
            EmailThread(email_message).start()
            messages.info(request,"Active your account by clicking the link send to your email")

            messages.success(request, "Waiting for Account Activation")
            return redirect("login")
    return render(request, 'signup.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "admin" and password == "admin":
            # Admin login credentials are fixed
            request.session['username'] = username
            return redirect("adminhome")  # Redirect to the admin dashboard

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session['username'] = username
            if user.role == 'tenant':
                return redirect("tenantpage")
            elif user.role == 'owner':
                return redirect("ownerpage")  # Create an 'ownerpage' URL
            elif user.role == 'provider':
                return redirect("serproviderpage")
            elif user.role == 'admin':
                return redirect("adminhome")
        else:
            messages.error(request, "Invalid login credentials")

    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, must-revalidate'
    return response


@login_required(login_url='login')
def logout(request):
    auth_logout(request)  # Use the logout function to log the user out
    return redirect('index')

def tenant(request):
    if request.method == "POST":
        full_name = request.POST.get('fullname')
        date_of_birth = request.POST.get('dateofbirth')
        gender = request.POST.get('gender')
        phone_number = request.POST.get('phoneno')
        current_address = request.POST.get('currentaddress')
        photoid_file = request.FILES.get('photoid')

        # Get the user's profile based on the currently logged-in user
        user_profile, created = Profile.objects.get_or_create(user=request.user)

        # Update user_profile fields with the data from the POST request
        user_profile.full_name = full_name
        user_profile.date_of_birth = date_of_birth
        user_profile.gender = gender
        user_profile.phone_number = phone_number
        user_profile.current_address = current_address

        if photoid_file:
            user_profile.photo_id = photoid_file

        # Save the updated user_profile
        user_profile.save()

        # Redirect or show a success message as needed
        messages.success(request, "Profile updated successfully.")
        return redirect("tenantpg")

    user_profile = get_object_or_404(Profile, user=request.user)
    context = {"user_profile": user_profile}

    if 'username' in request.session:
        response = render(request, 'tenantpage.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')

    
def owner(request):
     if request.method == "POST":
        full_name = request.POST.get('fullname')
        date_of_birth = request.POST.get('dateofbirth')
        gender = request.POST.get('gender')
        phone_number = request.POST.get('phoneno')
        current_address = request.POST.get('currentaddress')
        photoid_file = request.FILES.get('photoid')

        # Get the user's profile based on the currently logged-in user
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update user_profile fields with the data from the POST request
        user_profile.full_name = full_name
        user_profile.date_of_birth = date_of_birth
        user_profile.gender = gender
        user_profile.phone_number = phone_number
        user_profile.current_address = current_address
        user_profile.photoid_file=photoid_file

        if photoid_file:
            user_profile.photo_id = photoid_file

        # Save the updated user_profile
        user_profile.save()

        # Redirect or show a success message as needed
        messages.success(request, "Profile updated successfully.")
        return redirect("ownerpg")

     user_profile = UserProfile.objects.get(user=request.user)
     context = {"user_profile": user_profile}
     return render(request, "ownerpage.html", context)

     if 'username' in request.session:
        response = render(request, 'ownerpage.html')
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
     else:
        return redirect('index')

    
    
    
def adminh(request):
    
     if 'username' in request.session:
        response = render(request, 'adminhome.html')
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
     else:
        return redirect('index')


def adminreg(request):
    role_filter = request.GET.get('role')
    
    # Filter users based on role and exclude superusers
    if role_filter:
        if role_filter == "tenant":
            profiles = CustomUser.objects.filter(Q(role=role_filter) & ~Q(is_superuser=True))
        else:
            profiles = CustomUser.objects.filter(Q(role=role_filter) & ~Q(is_superuser=True))
    else:
        profiles = CustomUser.objects.filter(~Q(is_superuser=True))  # Exclude superusers
    
    return render(request, 'adminregusers.html', {'profiles': profiles})
   
class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=CustomUser.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account activated sucessfully")
            return redirect('login')
        return render(request,"activatefail.html")
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"User '{user.username}' has been deactivated.")
    else:
        messages.warning(request, f"User '{user.username}' is already deactivated.")
    return redirect('adminregusers')

def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f"User '{user.username}' has been activated.")
    else:
        messages.warning(request, f"User '{user.username}' is already active.")
    return redirect('adminregusers')




def ownerpg(request):
    if request.method == 'POST':
        # Check if the user is logged in
        if 'username' in request.session:
            # Get the username from the session
            username = request.session['username']

            # Try to get the user's profile
            try:
                user_profile = UserProfile.objects.get(user__username=username)
            except UserProfile.DoesNotExist:
                user_profile = None

            if user_profile:
                # Extract user profile information
                user = user_profile.user
                property_type = request.POST.get('property_type')
                address = request.POST.get('address')
              
                monthly_rent = request.POST.get('monthly_rent')
                security_deposit = request.POST.get('security_deposit')
                lease_duration = request.POST.get('lease_duration')
                availability_date = request.POST.get('availability_date')

                # Get the uploaded image

                # Create and save a new Property instance associated with the property owner
                property = Property(
                    property_type=property_type,
                    address=address,
                   
                    monthly_rent=monthly_rent,
                    security_deposit=security_deposit,
                    lease_duration=lease_duration,
                    availability_date=availability_date,
                    property_owner=user,  # Assign the property owner
                )
                property.save()
                messages.success(request, "Property Added successfully")

            else:
                # Handle the case where the user profile is not found
                return redirect('index')

    if 'username' in request.session:
        username = request.session['username']

        # Get the user's profile
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Check if the user profile is found
        if user_profile:
            context = {
                'user_profile': user_profile,  # Add user_profile to the context
            }

            response = render(request, 'ownerpg.html', context)
            response['Cache-Control'] = 'no-store, must-revalidate'
            return response
        else:
            # Handle the case where the user profile is not found
            return redirect('index')
    else:
        return redirect('index')

# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

    
from datetime import datetime


def tenantpg(request):
    filtered_properties = Property.objects.filter(approval_status='Approved')

    property_type = request.GET.get('property_type')
    min_rent = request.GET.get('min_rent')
    max_rent = request.GET.get('max_rent')

    # Create Q objects to build complex queries
    filter_params = Q()

    if property_type:
        filter_params &= Q(property_type=property_type)

    if min_rent:
        filter_params &= Q(monthly_rent__gte=min_rent)

    if max_rent: 
        filter_params &= Q(monthly_rent__lte=max_rent)

    # Apply the filters
    filtered_properties = filtered_properties.filter(filter_params)

    rented_properties = []  # Initialize rented_properties as an empty list

    if 'username' in request.session:
        username = request.session['username']

        # Get the user's profile
        try:
            user_profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            user_profile = None

        # Check if a rental request has been accepted for each property
        for property in filtered_properties:
            property.is_rental_request_accepted = property.rentalrequest_set.filter(tenant=user_profile, status='Accepted').exists()

            if property.is_rental_request_accepted:
                # Calculate the number of payments made for the property
                num_payments = Payment.objects.filter(property=property, user_profile=user_profile).count()

                # Calculate upcoming rent payment date based on availability date and lease duration
                availability_date = property.availability_date
                lease_duration = property.lease_duration

                if lease_duration == '1 year':
                    upcoming_payment_date = availability_date + relativedelta(months=num_payments * 12)
                elif lease_duration == 'Month-to-month':
                    upcoming_payment_date = availability_date + relativedelta(months=num_payments)
                else:
                    upcoming_payment_date = None

                property.upcoming_payment_date = upcoming_payment_date
                rented_properties.append(property)

                # Fetch lease agreement details for the rented property
                lease_agreements = LeaseAgreement.objects.filter(property=property)

                if lease_agreements.exists():
                    # If there are multiple lease agreements, choose the latest one
                    latest_lease_agreement = lease_agreements.order_by('-created_at').first()
                    property.lease_agreement = latest_lease_agreement
                else:
                    # Handle the case where no lease agreement is found
                    property.lease_agreement = None

        # Check if the payment for a rented property has been made
        payment_made = Payment.objects.filter(property__in=rented_properties, user_profile=user_profile).exists()

        context = {
            'user_profile': user_profile,
            'properties': filtered_properties,
            'rented_properties': rented_properties,
            'payment_made': payment_made,
        }

        response = render(request, 'tenantpg.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')

    




def manageprop(request):
    if 'username' in request.session:
        username = request.session['username']

        if request.method == 'POST':
            # Check if a property deletion request was submitted
            property_id_to_delete = request.POST.get('property_id_to_delete')
            if property_id_to_delete:
                # Soft delete the property by updating the 'deleted' field
                property_to_delete = get_object_or_404(Property, id=property_id_to_delete)
                property_to_delete.deleted = True
                property_to_delete.save()
                # You can add a success message here if needed

        # Get the user's profile
        try:
            # Ensure we retrieve the user profile correctly
            user_profile = get_object_or_404(UserProfile, user__username=username)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Check if the user profile is found
        if user_profile:
            # Get non-deleted properties associated with the property owner
            properties = Property.objects.filter(property_owner=user_profile.user, deleted=False)

            # Check if payment is made for each property
            for property in properties:
                property.payment_made = Payment.objects.filter(property=property).exists()
            
            for property in properties:
                property.feedback = PropertyFeedback.objects.filter(property=property)

            context = {
                'user_profile': user_profile,
                'properties': properties,  # Add properties to the context
            }

            return render(request, 'manageprop.html', context)
        else:
            # Handle the case where the user profile is not found more gracefully
            return render(request, 'manageprop.html', {'error_message': 'User profile not found.'})
    else:
        return redirect('index')
    




def clear_rental_requests(request, property_id):
    try:
        property_instance = Property.objects.get(id=property_id)
        rental_requests = property_instance.rentalrequest_set.all()
        rental_requests.delete()

        messages.success(request, "Rental requests cleared successfully.")
    except Property.DoesNotExist:
        messages.error(request, "Property not found.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('manageprop')



from django.http import Http404, HttpResponseBadRequest, JsonResponse

def propimgup(request, property_id):
    try:
        property = Property.objects.get(pk=property_id)
    except Property.DoesNotExist:
        raise Http404("Property does not exist")

    if request.method == 'POST':
        category = request.POST.get('category')
        images = request.FILES.getlist('image')

        for image in images:
            PropertyImage.objects.create(property=property, category=category, image=image)

        messages.success(request, "Images Added successfully")
        return redirect('manageprop')

    context = {
        'property': property,
    }

    return render(request, 'propimgup.html', context)

def propsellimgup(request, property_id):
    try:
        property = Propertysell.objects.get(pk=property_id)
    except Propertysell.DoesNotExist:
        raise Http404("Property does not exist")

    if request.method == 'POST':
        images = request.FILES.getlist('image')

        for image in images:
            property.property_images = image  # Assign the uploaded image to the property

        property.save()  # Save the property to store the uploaded images

        messages.success(request, "Images added successfully")
        return redirect('manageprop')

    context = {
        'property': property,
    }

    return render(request, 'propimgup.html', context)

def property_images(request, property_id):
    property = Property.objects.get(pk=property_id)
    images = PropertyImage.objects.filter(property=property)

    return render(request, 'property_images.html', {'property': property, 'images': images})



    
def admprop(request):
    # Retrieve all properties from both models
    rental_properties = Property.objects.all()
    sale_properties = Propertysell.objects.all()

    return render(request, 'admprop.html', {'rental_properties': rental_properties, 'sale_properties': sale_properties})


def verify_property(request, property_id):
    # Retrieve the property with the given ID
    property = get_object_or_404(Propertysell, pk=property_id)
    
    # Perform verification logic here, for example, updating the verification status
    property.verification_status = 'verified'
    property.save()
    
    # Redirect back to the property list page
    return redirect('admprop')

from django.http import HttpResponseRedirect
from django.urls import reverse


def approve_property(request, property_id):
    property = Property.objects.get(pk=property_id)
    property.approval_status = 'Approved'
    property.save()
    return HttpResponseRedirect(reverse('admprop'))

def reject_property(request, property_id):
    property = Property.objects.get(pk=property_id)
    property.approval_status = 'Rejected'
    property.save()
    return HttpResponseRedirect(reverse('admprop'))

def propamenity(request, property_id):
    if request.method == "POST":
        property = Property.objects.get(id=property_id)
        
        # Create an Amenity object
        amenity = Amenity(property=property)

        # Get the selected property type from the form
        property_type = request.POST.get("property_type")

        # Update amenity details based on property type
        if property_type == 'apartment':
            amenity.squarefootage = request.POST.get("sqfootage_apartment")
            amenity.bedrooms = request.POST.get("bedrooms_apartment")
            amenity.bathrooms = request.POST.get("bathrooms_apartment")
        elif property_type == 'house':
            amenity.squarefootage = request.POST.get("sqfootage_house")
            amenity.bedrooms = request.POST.get("bedrooms_house")
            amenity.bathrooms = request.POST.get("bathrooms_house")
            amenity.stories = request.POST.get("stories")
            amenity.rentspace = request.POST.get("rentspace")
        elif property_type == 'officespace':
            amenity.noofrooms = request.POST.get("noofrooms_office")
            amenity.squarefootage = request.POST.get("sqfootage_office")
            amenity.parkingspace = request.POST.get("parkingspace_office")
        elif property_type == 'warehouse':
            amenity.noofrooms = request.POST.get("noofrooms_warehouse")
            amenity.squarefootage = request.POST.get("sqfootage_warehouse")
            amenity.parkingspace = request.POST.get("parkingspace_warehouse")
        elif property_type == 'land':
            amenity.purpose = request.POST.get("purpose")
            amenity.acrescent = request.POST.get("acrescent")

        # Other common fields
        amenity.balcony = request.POST.get("balcony")

        # Save the amenity to the database
        amenity.save()

        return redirect('manageprop')

    return render(request, 'propamenity.html')



from django.db.models import Max

def property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    # Fetch the latest entered amenity for this property
    latest_amenity = Amenity.objects.filter(property=property).latest('id')

        
    return render(request, 'property_detail.html', {'property': property, 'latest_amenity': latest_amenity})



def ownerinfo(request, property_id):
    # Retrieve the property based on the property_id
    property = get_object_or_404(Property, pk=property_id)

    # Retrieve the property owner's profile
    owner_profile = UserProfile.objects.get(user=property.property_owner)

    context = {
        "property": property,
        "owner_profile": owner_profile,
    }

    return render(request, "ownerinfo.html", context)


from django.http import HttpResponse

def propdocs(request, property_id):
    if request.method == 'POST':
        property_instance = Property.objects.get(id=property_id)

        # Assuming the input names in your HTML form are 'ownership-docs', 'financial-docs', etc.
        document_types = ['ownership-docs', 'financial-docs', 'property-details', 'maintenance-records']
        
        for doc_type in document_types:
            document = request.FILES.get(doc_type, None)
            
            if document:
                PropertyDocument.objects.create(property=property_instance, document_type=doc_type, document=document)

        return redirect('manageprop')  # You can redirect to another page if needed
    else:
        return render(request, 'propdocs.html', {'property_id': property_id})
    

def admviewdocs(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_documents = PropertyDocument.objects.filter(property=property_obj)
    context = {'property': property_obj, 'property_documents': property_documents}
   
    return render(request, 'admviewdocs.html', context)


def submit_rental_request(request, property_id):
    if request.method == 'POST':
        # Assuming you have a form with the tenant's information
        # In a real scenario, you might want to authenticate the user or get the tenant information in some way

        # Get the property and tenant based on the IDs
        property = Property.objects.get(pk=property_id)
        tenant = request.user.profile  # Assuming the tenant information is associated with the user's profile

        # Check if a rental request already exists for this property and tenant
        existing_request = RentalRequest.objects.filter(property=property, tenant=tenant).exists()

        if not existing_request:
            # Create a new rental request
            rental_request = RentalRequest(property=property, tenant=tenant)
            rental_request.save()

            messages.success(request, 'Rental request submitted successfully!')
        else:
            messages.warning(request, 'You have already submitted a rental request for this property.')

        # Redirect back to the property details page or wherever you want

    # Handle the case where the request method is not POST (optional)
    return redirect('tenantpage')  # 

# 


def accept_rental_request(request, request_id):
    if request.method == 'POST':
        # Get the rental request based on the request_id
        rental_request = get_object_or_404(RentalRequest, id=request_id)

        # Add logic to update the rental request status to 'Accepted'
        rental_request.status = 'Accepted'
        rental_request.save()

        # Add any additional logic you need (e.g., send notifications, update other models, etc.)

    # Redirect back to the manage properties page
    return redirect('manageprop')




# # views.py

# from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from razorpay import Client


razorpay_api_key = settings.RAZORPAY_API_KEY
razorpay_secret_key = settings.RAZORPAY_API_SECRET

razorpay_client = Client(auth=(razorpay_api_key, razorpay_secret_key))

@csrf_exempt
def rentnxt(request, property_id):
    try:
        # Retrieve the Property object
        property = Property.objects.get(pk=property_id)

        # Get the user profile of the logged-in user
        user_profile = request.user.profile

        # Calculate the amount based on the monthly rent
        amount = int((property.monthly_rent + property.security_deposit) * 100)

        # Create a Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_rcptid_{property.id}',
            'payment_capture': '1',  # Auto-capture payment
        }

        # Create an order
        order_response = razorpay_client.order.create(data=order_data)
        order = order_response

        # Store the order details in the session to retrieve later
        request.session['razorpay_order_id'] = order['id']
        request.session['property_id'] = property_id

        context = {
            'razorpay_api_key': razorpay_api_key,
            'amount': amount,
            'currency': order_data['currency'],
            'order_id': order['id'],
        }

        return render(request, 'payment.html', context)

    except Property.DoesNotExist:
        return HttpResponseBadRequest('Invalid Property ID')




from razorpay.errors import BadRequestError

@login_required  # Add this decorator to ensure the user is logged in
@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')

        # Debug information
        print(f"Received Razorpay Order ID: {razorpay_order_id}")

        try:
            # Retrieve the property based on the order ID
            order = razorpay_client.order.fetch(razorpay_order_id)
            property_id = int(order['receipt'][len('order_rcptid_'):])
            property = Property.objects.get(pk=property_id)

            # Get the user profile of the logged-in user
            user_profile = request.user.profile

            amount_in_rupees = Decimal(order['amount']) / 100


            # Create a Payment record with the associated user profile
            payment = Payment.objects.create(
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                property=property,
                user_profile=user_profile,
                amount=amount_in_rupees,
                # Add other fields as needed
            )

            # Update any status or details in your Property model if needed
            property.payment_status = 'Paid'
            property.save()

            return JsonResponse({'status': 'success'})
        except BadRequestError as e:
            # Handle Razorpay API errors
            print(f"Razorpay API error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Razorpay API error'})
        except Property.DoesNotExist:
            # Handle property not found error
            print(f"Property not found for ID: {property_id}")
            return JsonResponse({'status': 'error', 'message': 'Property not found'})
        except Exception as e:
            # Handle other unexpected errors
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unexpected error'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




def lease(request, property_id):
    # Try to get the Property object or return a 404 response if it doesn't exist
    property = get_object_or_404(Property, pk=property_id)

    if request.method == 'POST':
        # Get data from the form
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        rent_amount = request.POST.get('rent_amount')
        security_deposit = request.POST.get('security_deposit')

        # Create a LeaseAgreement instance and save it to the database
        lease_agreement = LeaseAgreement(
            property=property,
            start_date=start_date,
            end_date=end_date,
            rent_amount=rent_amount,
            security_deposit=security_deposit,
        )
        lease_agreement.save()

        # You can add a success message or redirect to another page
        return redirect('manageprop')

    return render(request, 'lease.html', {'property': property})

# def view_lease_agreement(request, lease_agreement_id):
#     lease_agreement = get_object_or_404(LeaseAgreement, id=lease_agreement_id)
#     return render(request, 'viewlease.html', {'lease_agreement': lease_agreement})

def update_property_view(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        # Process the form data when the form is submitted
        property_instance.property_type = request.POST.get('property_type')
        property_instance.address = request.POST.get('address')
        property_instance.monthly_rent = request.POST.get('monthly_rent')
        property_instance.security_deposit = request.POST.get('security_deposit')
        property_instance.lease_duration = request.POST.get('lease_duration')
        property_instance.availability_date = request.POST.get('availability_date')

        # Save the updated property details
        property_instance.save()

        # Create a notification for the property owner
        Notification.objects.create(
            user=request.user,  # Property owner's user object
            sender=request.user,  # Assuming the property owner is the sender
            notification_type='info',  # You can adjust the type as needed
            message=f'Property details for {property_instance.property_type} updated successfully.',
        )

        # Redirect to the property details page after updating
        return redirect('manageprop')
    else:
        # Display the form with the current property details
        return render(request, 'updateprop.html', {'property': property_instance})




from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

from django.contrib.auth.decorators import login_required

@login_required
def generate_property_pdf(request, property_id):
    # Get the property object
    property = get_object_or_404(Property, id=property_id)

    

    # Get the tenant (user who brought the property) and property owner
    tenant_profile = request.user.profile  # Accessing the profile of the logged-in user
    owner_profile = property.property_owner.userprofile

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{property.property_type}_invoice.pdf"'

    # Create the PDF content using ReportLab
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Define styles for the PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        textColor=colors.blue,
        fontSize=18,
        spaceAfter=12
    )
    normal_style = styles['BodyText']

    # Build the PDF content
    content = []

    # Add title to the PDF
    title_text = f"<u>Property Invoice for {property.property_type}</u>"
    content.append(Paragraph(title_text, title_style))
    content.append(Paragraph("<br/>", normal_style))

    # Add property details to the PDF
    details = [
        f"<b>Property Type:</b> {property.property_type}",
        f"<b>Address:</b> {property.address}",
        f"<b>Monthly Rent:</b> Rs {property.monthly_rent}",
        f"<b>Security Deposit:</b> Rs {property.security_deposit}",
        f"<b>Lease Duration:</b> {property.lease_duration}",
        f"<b>Availability Date:</b> {property.availability_date}",
        # Add more details as needed
    ]

    for detail in details:
        content.append(Paragraph(detail, normal_style))
        content.append(Paragraph("<br/>", normal_style))

    # Add tenant details to the PDF
    content.append(Paragraph("<u>Tenant Information</u>", title_style))
    tenant_details = [
        f"<b>Name:</b> {tenant_profile.full_name}",
        f"<b>Date of Birth:</b> {tenant_profile.date_of_birth}",
        f"<b>Phone Number:</b> {tenant_profile.phone_number}",
        f"<b>Current Address:</b> {tenant_profile.current_address}",
        # Add more details as needed
    ]

    for detail in tenant_details:
        content.append(Paragraph(detail, normal_style))
        content.append(Paragraph("<br/>", normal_style))

    # Add owner details to the PDF
    content.append(Paragraph("<u>Property Owner Information</u>", title_style))
    owner_details = [
        f"<b>Name:</b> {owner_profile.full_name}",
        f"<b>Date of Birth:</b> {owner_profile.date_of_birth}",
        f"<b>Phone Number:</b> {owner_profile.phone_number}",
        f"<b>Current Address:</b> {owner_profile.current_address}",
        # Add more details as needed
    ]

    for detail in owner_details:
        content.append(Paragraph(detail, normal_style))
        content.append(Paragraph("<br/>", normal_style))

    # Add a stylish message for first payment
    content.append(Paragraph("<u>First Payment Information</u>", title_style))
    content.append(Paragraph("<b>First Payment:</b> <i>Done</i>", normal_style))
    content.append(Paragraph("<br/>", normal_style))

    # Build the PDF
    pdf.build(content)

    # Get the value of the BytesIO buffer and write it to the response
    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)

    return response




def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notifications})

def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.is_read = True
    notification.save()
    notification.delete()

    return redirect('view_notifications')

def serproviderpage(request):
    # Check if the user is logged in
    if 'username' in request.session:
        try:
            # Get the user's profile based on the currently logged-in user
            user_profile = ServiceProviderProfile.objects.get(user=request.user)
        except ServiceProviderProfile.DoesNotExist:
            user_profile = ServiceProviderProfile.objects.create(user=request.user)

        if request.method == "POST":
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            business_name = request.POST.get('business_name')
            experience = request.POST.get('experience')
            certification_file = request.FILES.get('certification_file')
            address = request.POST.get('address')

            # Update user_profile fields with the data from the POST request
            user_profile.name = name
            user_profile.phone = phone
            user_profile.business_name = business_name
            user_profile.experience = experience
            user_profile.address = address

            if certification_file:
                user_profile.certification_file = certification_file

            # Save the updated user_profile
            user_profile.save()

            # Check if the profile is approved or rejected
            if user_profile.approved:
                Notification.objects.create(
                    user=request.user,
                    sender=request.user,  # You can set the sender to None or to any user you want
                    notification_type='info',  # You can adjust the type as needed
                    message=f'Your service provider profile has been approved.',
                )
            elif user_profile.rejected:
                Notification.objects.create(
                    user=request.user,
                    sender=request.user,  # You can set the sender to None or to any user you want
                    notification_type='warning',  # You can adjust the type as needed
                    message=f'Your service provider profile has been rejected.',
                )

            # Redirect or show a success message as needed
            messages.success(request, "Profile updated successfully.")
            return redirect("serproviderpage")

        context = {"user_profile": user_profile}

        response = render(request, 'serproviderpage.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')



def adminserpropage(request):
    service_provider_profiles = ServiceProviderProfile.objects.prefetch_related('service_set').all()
    return render(request, 'adminserpropage.html', {'service_provider_profiles': service_provider_profiles})



def approve_profile(request, profile_id):
    profile = ServiceProviderProfile.objects.get(id=profile_id)
    profile.approved = True
    profile.save()

    # Create a notification for approval
    Notification.objects.create(
        user=profile.user,  # Assuming `user` is a foreign key in the profile model
        sender=profile.user,  # You can set the sender to None or to any user you want
        notification_type='info',  # You can adjust the type as needed
        message=f'Your service provider profile has been approved.',
    )

    messages.success(request, f"Profile for {profile.name} has been approved.")
    return redirect('adminserpropage')

def reject_profile(request, profile_id):
    profile = ServiceProviderProfile.objects.get(id=profile_id)
    profile.approved = False
    profile.save()

    # Create a notification for rejection
    Notification.objects.create(
        user=profile.user,  # Assuming `user` is a foreign key in the profile model
        sender=profile.user,  # You can set the sender to None or to any user you want
        notification_type='warning',  # You can adjust the type as needed
        message=f'Your service provider profile has been rejected.',
    )

    messages.warning(request, f"Profile for {profile.name} has been rejected.")
    return redirect('adminserpropage')


@login_required
def serproviderdash(request):
    
    provider_profile = ServiceProviderProfile.objects.get(user=request.user)

    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        service_category = request.POST.get('service_category')
        property_type = request.POST.get('property_type')
        service_description = request.POST.get('service_description')
        service_price = request.POST.get('service_price')
        location = request.POST.get('location')

        # Save the service to the database
        service = Service.objects.create(
            service_provider_profile=provider_profile,
            service_name=service_name,
            service_category=service_category,
            property_type=property_type,
            service_description=service_description,
            service_price=service_price,
            location=location
        )
       

    provider_services = Service.objects.filter(service_provider_profile=provider_profile)
    service_requests = ServiceRequest.objects.filter(service__in=provider_services)
    service_payments = Pay.objects.filter(service__in=provider_services)


    context = {
        'provider_profile': provider_profile,
        'provider_services': provider_services,
        'service_requests': service_requests,
        'service_payments': service_payments,

    }

    return render(request, "serproviderdash.html", context)
def schedule_service(request, request_id):
    if request.method == 'POST':
        scheduled_date = request.POST['scheduled_date']
        scheduled_time = request.POST['scheduled_time']

        # Create a ScheduledService instance
        scheduled_service = ScheduledService.objects.create(
            service_request_id=request_id,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time
        )

        messages.success(request, 'Service scheduled successfully.')

    return redirect('serproviderdash') 
def mark_as_done(request, request_id):
    scheduled_service = get_object_or_404(ScheduledService, pk=request_id)
    scheduled_service.is_done = True
    scheduled_service.save()
    return redirect('serproviderdash')









def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        # Handle form submission and update the service details
        service.service_name = request.POST.get('edit_service_name')
        service.service_category=request.POST.get('edit_service_category')
        service.property_type=request.POST.get('edit_property_type')
        service.service_description=request.POST.get('edit_service_description')
        service.service_price=request.POST.get('edit_service_price')
        service.location=request.POST.get('edit_location')



        # Update other fields as needed
        service.save()
        return redirect('serproviderdash')  # Redirect to the dashboard after editing


    context = {
        'service': service,

    }

    return render(request, "serproviderdash.html", context)

def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    return redirect('serproviderdash')


    
def view_locations(request):
    properties = Property.objects.all()

    # Add this block to fetch geocoded coordinates for each property
    for property in properties:
        address = property.address
        url = 'https://api.opencagedata.com/geocode/v1/json?q=' + address + '&key=YOUR_OPENCAGE_API_KEY'

        response = requests.get(url)
        data = response.json()

        if data.get('results') and data['results'][0].get('geometry'):
            property.latitude = data['results'][0]['geometry']['lat']
            property.longitude = data['results'][0]['geometry']['lng']
        else:
            property.latitude = None
            property.longitude = None
    return render(request,'view_locations.html',{'properties': properties})          

    

def admin_dashboard(request):
    # Retrieve all properties, profiles, and payments
    properties = Property.objects.all()
    profiles = Profile.objects.all()
    payments = Payment.objects.all()

    return render(request, 'adminpay.html', {'properties': properties, 'profiles': profiles, 'payments': payments})


from django.db.models import Sum

@login_required
def rent_collection(request):
    properties = Property.objects.filter(property_owner=request.user)

    rent_data = []
    total_earnings = 0  # Initialize total earnings

    for property in properties:
        tenants_payments = Payment.objects.filter(property=property)
        rent_data.append({'property': property, 'tenants_payments': tenants_payments})
        total_earnings += tenants_payments.aggregate(Sum('amount'))['amount__sum'] or 0  # Sum payments

    context = {'rent_data': rent_data, 'total_earnings': total_earnings}
    return render(request, 'rentcollect.html', context)



def property_feedback(request, property_id):
    property_obj = Property.objects.get(pk=property_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback')

        # Ensure user is authenticated before saving feedback
        if request.user.is_authenticated:
            PropertyFeedback.objects.create(
                property=property_obj,
                user=request.user,
                rating=rating,
                feedback=feedback
            )
            # You can add a success message here if needed
        else:
            # You can add an error message here if needed
            pass

    feedback_list = PropertyFeedback.objects.filter(property=property_obj)

    return render(request, 'propertyfeedback.html', {'property': property_obj, 'feedback_list': feedback_list})

@login_required
def view_services(request, property_type=None):
    # Retrieve all services from the database, prefetching related ServiceRequest and ScheduledService instances
    services = Service.objects.prefetch_related('servicerequest_set__scheduledservice_set').all()

    # Filter services based on property_type
    if property_type:
        services = services.filter(property_type=property_type)

    return render(request, 'services.html', {'services': services})




@login_required
def request_service(request, service_id):
    # Get the service instance
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        message = request.POST.get('message')

        # Create a service request
        ServiceRequest.objects.create(service=service, user=request.user.userprofile, message=message)
        # Ensure you use request.user.userprofile to get the UserProfile associated with the user

        # Redirect to a confirmation page or to the same page
        return redirect('manageprop')  # Update with the appropriate URL name

    # If the request is not POST, handle it accordingly
    # You might want to display a form to input the request message
    # or provide a button to trigger the request form
    # ...

    return render(request, 'services.html')  # Update with the appropriate template


from razorpay import Client


razorpay_api_key = settings.RAZORPAY_API_KEY
razorpay_secret_key = settings.RAZORPAY_API_SECRET

razorpay_client = Client(auth=(razorpay_api_key, razorpay_secret_key))

@csrf_exempt
def rentnxtt(request, property_id):
    try:
        # Retrieve the Property object
        property = Property.objects.get(pk=property_id)

        # Get the user profile of the logged-in user
        user_profile = request.user.profile

        # Calculate the amount based on the monthly rent
        amount = int((property.monthly_rent ) * 100)

        # Create a Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_rcptid_{property.id}',
            'payment_capture': '1',  # Auto-capture payment
        }

        # Create an order
        order_response = razorpay_client.order.create(data=order_data)
        order = order_response

        # Store the order details in the session to retrieve later
        request.session['razorpay_order_id'] = order['id']
        request.session['property_id'] = property_id

        context = {
            'razorpay_api_key': razorpay_api_key,
            'amount': amount,
            'currency': order_data['currency'],
            'order_id': order['id'],
        }

        return render(request, 'paymentnxt.html', context)

    except Property.DoesNotExist:
        return HttpResponseBadRequest('Invalid Property ID')




from razorpay.errors import BadRequestError

@login_required  # Add this decorator to ensure the user is logged in
@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')

        # Debug information
        print(f"Received Razorpay Order ID: {razorpay_order_id}")

        try:
            # Retrieve the property based on the order ID
            order = razorpay_client.order.fetch(razorpay_order_id)
            property_id = int(order['receipt'][len('order_rcptid_'):])
            property = Property.objects.get(pk=property_id)

            # Get the user profile of the logged-in user
            user_profile = request.user.profile

            amount_in_rupees = Decimal(order['amount']) / 100


            # Create a Payment record with the associated user profile
            payment = Payment.objects.create(
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                property=property,
                user_profile=user_profile,
                amount=amount_in_rupees,
                # Add other fields as needed
            )

            # Update any status or details in your Property model if needed
            property.payment_status = 'Paid'
            property.save()

            return JsonResponse({'status': 'success'})
        except BadRequestError as e:
            # Handle Razorpay API errors
            print(f"Razorpay API error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Razorpay API error'})
        except Property.DoesNotExist:
            # Handle property not found error
            print(f"Property not found for ID: {property_id}")
            return JsonResponse({'status': 'error', 'message': 'Property not found'})
        except Exception as e:
            # Handle other unexpected errors
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unexpected error'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



from razorpay import Client


razorpay_api_key = settings.RAZORPAY_API_KEY
razorpay_secret_key = settings.RAZORPAY_API_SECRET

razorpay_client = Client(auth=(razorpay_api_key, razorpay_secret_key))

@csrf_exempt
def serpay(request, service_id):
    try:
        # Retrieve the Property object
        service = Service.objects.get(pk=service_id)

        # Get the user profile of the logged-in user
        user_profile = request.user.userprofile

        # Calculate the amount based on the monthly rent
        amount = int((service.service_price ) * 100)

        # Create a Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_rcptid_{service.id}',
            'payment_capture': '1',  # Auto-capture payment
        }

        # Create an order
        order_response = razorpay_client.order.create(data=order_data)
        order = order_response

        # Store the order details in the session to retrieve later
        request.session['razorpay_order_id'] = order['id']
        request.session['service_id'] = service_id

        context = {
            'razorpay_api_key': razorpay_api_key,
            'amount': amount,
            'currency': order_data['currency'],
            'order_id': order['id'],
        }

        return render(request, 'payservice.html', context)

    except Service.DoesNotExist:
        return HttpResponseBadRequest('Invalid Service ID')




from razorpay.errors import BadRequestError

@login_required  # Add this decorator to ensure the user is logged in
@csrf_exempt
def handle_pay(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')

        # Debug information
        print(f"Received Razorpay Order ID: {razorpay_order_id}")

        try:
            # Retrieve the property based on the order ID
            order = razorpay_client.order.fetch(razorpay_order_id)
            service_id = int(order['receipt'][len('order_rcptid_'):])
            service = Service.objects.get(pk=service_id)

            # Get the user profile of the logged-in user
            user_profile = request.user.userprofile

            amount_in_rupees = Decimal(order['amount']) / 100


            # Create a Payment record with the associated user profile
            payment = Pay.objects.create(
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                service=service,
                user_profile=user_profile,
                amount=amount_in_rupees,
                # Add other fields as needed
            )

            # Update any status or details in your Property model if needed
            Service.payment_status = 'Paid'
            Service.save()

            return JsonResponse({'status': 'success'})
        except BadRequestError as e:
            # Handle Razorpay API errors
            print(f"Razorpay API error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Razorpay API error'})
        except Service.DoesNotExist:
            # Handle property not found error
            print(f"Service not found for ID: {service_id}")
            return JsonResponse({'status': 'error', 'message': 'Service not found'})
        except Exception as e:
            # Handle other unexpected errors
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unexpected error'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})













# views.py


# Your existing code...



from django.shortcuts import redirect
from urllib.parse import unquote

def ad_click(request):
    url = request.GET.get('url', '/')
    # Log the click or perform any other necessary action
    return redirect(unquote(url))

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from rental.models import Propertysell, LoanApplication

from django.contrib import messages
def finance(request):
    if request.method == 'POST':
        # Get form data
        applicant_name = request.POST.get('applicant_name')
        address = request.POST.get('address')
        state = request.POST.get('state')
        district = request.POST.get('district')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        age = request.POST.get('age')
        occupation = request.POST.get('occupation')
        loan_amount = request.POST.get('loan_amount')
        property_address = request.POST.get('property_address')
        nearest_bank = request.POST.get('nearest_bank')
        net_monthly_income = request.POST.get('net_monthly_income')

        # Validate if all required fields are provided
        if not (applicant_name and address and state and district and telephone and email and age and occupation and loan_amount and property_address and nearest_bank and net_monthly_income):
            messages.error(request, 'Please fill out all required fields')
            return redirect('finance')  # Redirect back to the finance page with the error message

        try:
            # Attempt to get the selected property
            selected_property = Propertysell.objects.get(address=property_address)
        except Propertysell.DoesNotExist:
            # Handle the case where the property does not exist
            messages.error(request, 'Selected property does not exist')
            return redirect('financecentre')  # Redirect back to the finance page with the error message

        # Create a LoanApplication instance with the form data and associated property
        LoanApplication.objects.create(
            user=request.user,
            applicant_name=applicant_name,
            address=address,
            state=state,
            district=district,
            telephone=telephone,
            email=email,
            age=age,
            occupation=occupation,
            loan_amount=loan_amount,
            property_address=property_address,
            nearest_bank=nearest_bank,
            net_monthly_income=net_monthly_income,
            property_sell=selected_property  # Associate the selected property with the loan application
        )

        # Redirect to a success page or another view
        return redirect('tenantpg')

    # If it's a GET request, render the finance page with the property data
    properties = Propertysell.objects.all()
    user_loan_application = LoanApplication.objects.filter(user=request.user).first()

    return render(request, 'financecentre.html', {'properties': properties, 'user_loan_application': user_loan_application})



from .models import Propertysell

def sellprop(request):
    if request.method == 'POST':
        # Assuming you have a UserProfile object associated with the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Create a Property object and populate it with the form data
        property_obj = Propertysell(
            user_profile=user_profile,
            property_type=request.POST.get('propertyType'),
            address=request.POST.get('address'),
            sale_price=request.POST.get('salePrice'),
            description=request.POST.get('description'),
            amenities=request.POST.get('amenities'),
            contact_information=request.POST.get('contact'),
            property_images=request.FILES.get('propertyImages'),  # Assuming only one image is uploaded
            ownership=request.POST.get('ownership'),
            plot_area=request.POST.get('plotArea'),
            constructed_year=request.POST.get('constructedYear'),
            ready_to_move=bool(request.POST.get('readyToMove')),
            state=request.POST.get('state'),
            district=request.POST.get('district'),
            town=request.POST.get('town'),
            locality=request.POST.get('locality'),
            street=request.POST.get('street')
        )
        property_obj.save()
        
        # Redirect to a success page or do something else
        return redirect('ownerpage')

    else:
        # Render the form for GET requests
        return render(request, 'sellproperty.html')
    
from .models import Propertysell, Schedule

def view_properties(request):
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        property_id = request.POST.get('property')
        visit_date = request.POST.get('visit_date')
        visit_time = request.POST.get('visit_time')
        note = request.POST.get('note')
        
        tenant = User.objects.get(pk=tenant_id)
        property = Propertysell.objects.get(pk=property_id)
        
        # Create a new Schedule instance and save it
        schedule = Schedule.objects.create(tenant=tenant, property=property, visit_date=visit_date, visit_time=visit_time, note=note)
        schedule.save()

        # Redirect or render success page
        return render(request, 'view_properties.html')

    else:
        user_properties = Propertysell.objects.filter(user_profile__user=request.user)
        available_tenants = User.objects.filter(role='tenant')

        return render(request, 'view_properties.html', {'properties': user_properties, 'available_tenants': available_tenants})

def view_property(request):
    # Retrieve all properties
    properties = Propertysell.objects.all()
    scheduled_visits = Schedule.objects.filter(tenant=request.user)


    # Filter properties based on user preferences if any
    if request.method == 'GET':
        property_type = request.GET.get('property_type')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        state = request.GET.get('state')
        district = request.GET.get('district')
        verification_status = request.GET.get('verification_status')

        if property_type:
            properties = properties.filter(property_type=property_type)

        if min_price:
            properties = properties.filter(sale_price__gte=min_price)

        if max_price:
            properties = properties.filter(sale_price__lte=max_price)

        if state:
            properties = properties.filter(state__icontains=state)

        if district:
            properties = properties.filter(district__icontains=district)

        if verification_status:
            properties = properties.filter(verification_status=verification_status)
        
    for prop in properties:
        prop.has_scheduled_visits = scheduled_visits.filter(property=prop).exists()

    return render(request, 'buyprop.html', {'properties': properties, 'scheduled_visits': scheduled_visits})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def inbox(request):
    user = request.user
    received_messages = Message.objects.filter(recipient=user).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=user).order_by('-timestamp')
    return render(request, 'inbox.html', {'received_messages': received_messages, 'sent_messages': sent_messages})

@login_required
def compose_message(request):
    if request.method == 'POST':
        sender = request.user
        recipient_username = request.POST.get('recipient')
        recipient = CustomUser.objects.get(username=recipient_username)
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        is_reply = request.POST.get('is_reply', False) == 'True'  # Convert string to boolean
        Message.objects.create(sender=sender, recipient=recipient, subject=subject, body=body, is_reply=is_reply)
        messages.success(request, 'Message sent successfully')  # Add success message

        # return redirect('tenantpg')
    return render(request, 'compose_message.html', {'users': CustomUser.objects.all()})

@login_required
def mark_as_read(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    message.is_read = True
    message.save()
    message.delete()  # Delete the message after marking it as read
    return redirect('inbox')

@login_required
def delete_message(request, message_id):
    message = Message.objects.get(id=message_id)
    message.delete()
    return redirect('inbox')


# views.py

from django.contrib.auth import get_user_model
from django.http import JsonResponse

def validate_username(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        User = get_user_model()
        try:
            User.objects.get(username=username)
            # Username exists, return False
            data = {'available': False}
        except User.DoesNotExist:
            # Username does not exist, return True
            data = {'available': True}
        return JsonResponse(data)
    # If the request is not a GET request, return 404
    return JsonResponse({}, status=404)


