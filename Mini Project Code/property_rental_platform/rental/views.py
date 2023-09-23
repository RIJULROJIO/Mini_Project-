from django.shortcuts import render
from .forms import SignupForm
from django.shortcuts import redirect



def index(request):
    return render(request, 'index.html')
from django.contrib import messages  # Import the messages module
from .forms import SignupForm
from django.shortcuts import render, redirect

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
    return render(request,'login.html')


