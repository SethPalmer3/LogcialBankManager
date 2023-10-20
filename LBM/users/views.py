from django.shortcuts import HttpResponse, render, redirect, reverse
from django.contrib.auth import authenticate, login

from .models import UserProfile, Partition
from .forms import SignUpForm
from pprint import pprint

ABS_AMOUNT = 'amount'
PART_NAME = 'parition_name'
NA = 'NA'



# Create your views here.
# Login page (initial page)
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('users:home'))
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials'})

    return render(request, 'login.html')

def user_signup(request):
    if request.method == "POST": # If the user has inputted data
        form = SignUpForm(request.POST) # Parse signup form information
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password']) # Setting password
                user.save()

                profile = UserProfile() # Custom user information
                profile.detail_json = {
                        ABS_AMOUNT: 0,
                        PART_NAME: NA
                        }
                profile.user = user
                profile.save()
                login(request, user) # Persistant login of user
                return redirect(reverse('users:home')) # Redirects to their new home screen
            except Exception as e:
                print(e)
                form = SignUpForm()
                return render(request, 'signup.html', {'form': form, 'error': "An Error Has Occured"})
                
    else: # First time going to page
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def user_home(request):
    partitons = Partition.objects.filter(owner=request.user)
    return render(request, 'home.html', {'user_parts': partitons})
