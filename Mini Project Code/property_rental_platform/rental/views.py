from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import CustomUser  # Import your custom user model
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView,PasswordResetDoneView,PasswordResetCompleteView

from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'user/password_reset_form.html'  # Your template for the password reset form
    email_template_name = 'user/password_reset_email.html'  # Your email template for the password reset email
    success_url = reverse_lazy('password_reset_done')  # URL to redirect after successful form submission
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'  # Your template for password reset confirmation form
    success_url = reverse_lazy('password_reset_complete')  # URL to redirect after successful password reset
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'  # Your template for password reset done page
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user/password_reset_complete.html'  # Your template for password reset complete page

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        elif password != confirmPassword:
            messages.error(request, "Passwords do not match")
        else:
            # Create a CustomUser with the 'TENANT' role (or the desired default role)
            user = CustomUser(username=username, email=email, role='TENANT')
            user.set_password(password)
            user.save()
            messages.success(request, "Registered successfully")
            return redirect("login")
    return render(request, 'signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session['username'] = username
            messages.success(request, "Login successful!")
            # Redirect users based on their roles (customize as needed)
            return redirect("tenantpage")
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
    if 'username' in request.session:
     response = render(request, 'tenantpage.html')
     response['Cache-Control'] = 'no-store, must-revalidate'
     return response
    else:
        return redirect('index')