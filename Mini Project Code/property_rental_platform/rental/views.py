from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
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
from .models import CustomUser,UserProfile,Profile,Property,PropertyImage,Amenity,PropertyDocument,RentalRequest,LeaseAgreement,Notification # Import your custom user model

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

def index(request):
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
    context = {
            'properties': filtered_properties,
        }
    
    return render(request, 'index.html',context)

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

    user_profile = Profile.objects.get(user=request.user)
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

        context = {
            'user_profile': user_profile,
            'properties': filtered_properties,
        }

        response = render(request, 'tenantpg.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')
    

# def add_to_cart(request):
#     if request.method == 'POST':
#         property_id = request.POST.get('property_id')
#         property = get_object_or_404(Property, id=property_id)

#         # Assuming you have a UserProfile model with a cart field
#         if 'username' in request.session:
#             username = request.session['username']
#             user_profile = Profile.objects.get(user__username=username)

#             messages.success(request, "Property Added to Cart")

#             # Add the property to the user's cart
#             user_profile.cart.add(property)


#     # Redirect back to the tenantpg page
#     return redirect('tenantpg')




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
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Check if the user profile is found
        if user_profile:
            # Get non-deleted properties associated with the property owner
            properties = Property.objects.filter(property_owner=user_profile.user, deleted=False)

            context = {
                'user_profile': user_profile,
                'properties': properties,  # Add properties to the context
            }

            return render(request, 'manageprop.html', context)
        else:
            # Handle the case where the user profile is not found
            return redirect('index')
    else:
        return redirect('index')


from django.http import Http404

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
def property_images(request, property_id):
    property = Property.objects.get(pk=property_id)
    images = PropertyImage.objects.filter(property=property)

    return render(request, 'property_images.html', {'property': property, 'images': images})

    
def admprop(request):
    # Retrieve all properties
    properties = Property.objects.all()

    return render(request, 'admprop.html', {'properties': properties})

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


# def view_cart(request):
#     # Get the user's profile
#     user_profile = get_object_or_404(Profile, user=request.user)

    
#     # Get properties in the user's cart
#     cart_properties = user_profile.cart.all()

#     context = {'cart_properties': cart_properties}
#     return render(request, 'cart.html', context)

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
def rentnxt(request):
    # Amount to be paid (in paisa), you can change this dynamically based on your logic
    amount = 100

    # Create a Razorpay order (you need to implement this based on your logic)
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': 'order_rcptid_11',
        'payment_capture': '1',  # Auto-capture payment
    }

    # Create an order
    order = razorpay_client.order.create(data=order_data)

    context = {
        'razorpay_api_key': razorpay_api_key,
        'amount': order_data['amount'],
        'currency': order_data['currency'],
        'order_id': order['id'],
    }

    return render(request, 'payment.html', context)


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
def generate_property_pdf(request, property_id):
    # Get the property object
    property = get_object_or_404(Property, id=property_id)

    # Add logic to check if the property is rented (use your own conditions)
    # if property.is_rented:
    #     return HttpResponse("This property is not rented.")  # or redirect to an error page

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{property.property_type}_invoice.pdf"'

    # Create the PDF content
    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Property Invoice for {property.property_type}")

    # Add more property details to the PDF
    p.drawString(100, 780, f"Property Type: {property.property_type}")
    p.drawString(100, 760, f"Address: {property.address}")
    p.drawString(100, 740, f"Monthly Rent: Rs{property.monthly_rent}")
    # Add more details as needed

    # Save the PDF content
    p.showPage()
    p.save()

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











    
            

    

