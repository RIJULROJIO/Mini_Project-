from django.shortcuts import render,redirect
from .forms import SignupForm,UserProfileFilterForm
from .models import UserProfile
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.contrib import messages  # Import the messages module




#@never_cache
def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')  # Success message
            return redirect('signup')  # Redirect to the index page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')  # Validation error messages
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = UserProfile.objects.filter(username=username, password=password).first()
        
        if user is not None:
            # Store user data in the session
            request.session['user_id'] = user.id
            request.session['user_role'] = user.role
            request.session['username'] = user.username

            # Redirect based on user role (if needed)
            if user.role == 'tenant':
                return redirect('tenantpage')
            elif user.role == 'owner':
                return redirect('ownerpage')
            # Add more role-based redirects as needed

            #return redirect('index')  # Redirect to the index page after successful login
        else:
            # Handle invalid login credentials
            messages.error(request, 'Invalid username or password.')

    response= render(request, 'login.html')
    response['Cache-Control']='no-store,must-revalidate'
    return response

def tenantpage(request):
  
    user_role=request.session.get('user_role')
    if user_role=='tenant':
     response= render(request, 'tenantpage.html')
     response['Cache-Control']='no-store,must-revalidate'
     return response
    else:
        return redirect('login')

def logout_view(request):


  logout(request)
  

  return redirect('index')


def ownerpage(request):
    user_role=request.session.get('user_role')
    if user_role=='owner':
     response= render(request, 'ownerpage.html')
     response['Cache-Control']='no-store,must-revalidate'
     return response
    else:
        return redirect('login')
def adminhome(request):
    return render(request,'adminhome.html')

def user_profile_list(request):
    profiles = UserProfile.objects.all()
    form = UserProfileFilterForm(request.GET)

    if form.is_valid():
        username = form.cleaned_data['username']
        role = form.cleaned_data['role']

        if username:
            profiles = profiles.filter(username__icontains=username)
        if role:
            profiles = profiles.filter(role=role)

    return render(request, 'adminregusers.html', {'profiles': profiles, 'form': form})







