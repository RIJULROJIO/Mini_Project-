from django.shortcuts import render,redirect
from .forms import SignupForm
from .models import UserProfile
from django.contrib.auth import logout
from django.contrib.sessions.models import Session


from django.contrib.auth import authenticate, login
from django.contrib import messages  # Import the messages module





def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')  # Success message
            return redirect('signup.html')  # Redirect to the index page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')  # Validation error messages
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = UserProfile.objects.filter(username=username, password=password).first()
        if user is not None:
            print(f'User Role: {user.role}')

            request.session['user_id'] = user.id
            request.session['user_role'] = user.role
            request.session['username'] = user.username  # Store the username in the session


            # Redirect based on user role (if needed)
            if user.role == 'tenant':
                return redirect('tenantpage.html')
            elif user.role == 'owner':
                return redirect('ownerpage.html')
            # Add more role-based redirects as needed

            return redirect('index.html')  # Redirect to the index page after successful login
        else:
            # Handle invalid login credentials
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')
def logout_view(request):
    request.session.flush()  # Clear the current session
    logout(request)
    return redirect('index.html')







def tenantpage(request):
    # Retrieve user role from the session
    user_role = request.session.get('user_role')

    # Check if the user is logged in as a tenant
    if user_role == 'tenant':
        # Render the tenant page
        return render(request, 'tenantpage.html')
    else:
        # Redirect to the login page or show an error message
        return redirect('login')

def ownerpage(request):
    return render(request,'ownerpage.html')





