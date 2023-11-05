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
from .models import CustomUser,UserProfile,Profile,Property,PropertyImage,Amenity  # Import your custom user model

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
    return render(request, 'index.html')

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
    return render(request,'adminhome.html')

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
    # Get all approved properties
    filtered_properties = Property.objects.filter(approval_status='Approved')

    # Handle search and filters
    property_type = request.GET.get('property_type')
    monthly_rent = request.GET.get('monthly_rent')
    furnished = request.GET.get('furnished')
    square_footage = request.GET.get('square_footage')

    # Apply filters
    if property_type:
        filtered_properties = filtered_properties.filter(property_type=property_type)
    if monthly_rent:
        filtered_properties = filtered_properties.filter(monthly_rent=monthly_rent)
    if furnished:
        filtered_properties = filtered_properties.filter(furnished=True)
    if square_footage:
        filtered_properties = filtered_properties.filter(square_footage=square_footage)

    if 'username' in request.session:
        username = request.session['username']

        # Get the user's profile
        try:
            user_profile = Profile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            user_profile = None

        context = {
            'user_profile': user_profile,  # Add user_profile to the context
            'properties': filtered_properties,  # Use filtered properties for display
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
                property_to_delete = get_object_or_404(Property, id=property_id_to_delete)
                property_to_delete.delete()
                # You can add a success message here if needed

        # Get the user's profile
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Check if the user profile is found
        if user_profile:
            # Get properties associated with the property owner
            properties = Property.objects.filter(property_owner=user_profile.user)

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

        # Check the property type to determine which form fields to use
        property_type = property.property_type

        if property_type in ['apartment', 'house']:
            amenity.squarefootage = request.POST.get("sqfootage") or None
            amenity.bedrooms = request.POST.get("bedrooms") or None
            amenity.bathrooms = request.POST.get("bathrooms") or None
            if property_type == 'house':
                amenity.stories = request.POST.get("stories") or None
                amenity.rentspace = request.POST.get("rentspace") or None
        elif property_type in ['officespace', 'warehouse']:
            amenity.noofrooms = request.POST.get("noofrooms") or None
            amenity.squarefootage = request.POST.get("sqfootage") or None
            amenity.parkingspace = request.POST.get("parkingspace") or None
        elif property_type == 'land':
            amenity.purpose = request.POST.get("purpose") or None
            amenity.acrescent = request.POST.get("acrescent") or None

        amenity.balcony = request.POST.get("balcony")
        amenity.parkingspace = request.POST.get("parkingspace")

        amenity.save()

        return redirect('manageprop')

    return render(request, 'propamenity.html')


def property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    amenities = Amenity.objects.filter(property=property)  # Fetch amenities related to this property
    return render(request, 'property_detail.html', {'property': property, 'amenities': amenities})






    
            

    

