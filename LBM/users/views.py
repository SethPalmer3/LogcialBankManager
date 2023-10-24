from django.shortcuts import Http404, HttpResponse, render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction

import requests

from .models import UserProfile, Partition
from .forms import NewPartiton, SignUpForm, PartitionEditForm

ABS_AMOUNT = 'amount'
PART_NAME = 'parition_name'
NA = 'NA'



# Create your views here.
def index(request):
    return redirect(reverse('users:login'))

# Login page (initial page)
def user_login(request):
    if request.user.is_authenticated:
        print('authenticated ')
        return redirect(reverse('users:home'))

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

def user_logout(request):
    logout(request)
    return redirect(reverse('users:login'))

def user_signup(request):
    if request.method == "POST": # If the user has inputted data
        form = SignUpForm(request.POST) # Parse signup form information
        if form.is_valid():
            try:
                with transaction.atomic(): # Discards all model instances if a problem arises
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password']) # Setting password
                    user.save()

                    profile = UserProfile() # Custom user information
                    profile.user = user
                    profile.save()
                    first_parition = Partition.objects.create()
                    first_parition.owner.add(user)
                    first_parition.label = "Undefined"
                    first_parition.current_amount = 0.0
                    first_parition.save()

                login(request, user) # Persistant login of user
                return redirect(reverse('users:home')) # Redirects to their new home screen
            except Exception as e:
                print(e)
                form = SignUpForm()
                return render(request, 'signup.html', {'form': form, 'error': e})
                
    else: # First time going to page
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def user_home(request):
    if request.user is None:
        print('User does not exist')
        return redirect(reverse('users:login'))
    partitons = Partition.objects.filter(owner=request.user)
    userprof = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'home.html', {'user_parts': partitons, 'user_profile': userprof})

@login_required
def user_partition_view(request, partition_id):
    part = Partition.objects.get(id=partition_id)
    print(vars(part))
    return render(request, 'partition.html', {'partition_data': part})

@login_required
def user_partition_edit(request, partition_id):
    if request.method == "POST":
        form = PartitionEditForm(request.POST)
        if form.is_valid():
            part = Partition.objects.get(id=partition_id)
            part.label = form.cleaned_data["new_label"]
            part.current_amount = form.cleaned_data["new_amount"]
            part.save()
            return redirect('users:partition', partition_id=partition_id)
    else:
        form = PartitionEditForm()

    return render(request, "partition_edit.html", {'form': form, 'partition_id': partition_id})

@login_required
def add_partition(request):
    if request.method == "POST":
        form = NewPartiton(request.POST)
        if form.is_valid():
            part = form.save(commit=True)
            part.owner.set([request.user])
            part.save()
            return redirect('users:partition', partition_id=part.id)
    else:
        form = NewPartiton()
    return render(request, "add_partition.html", {'form': form})

@login_required
def remove_partiton(request, partition_id):
    Partition.objects.get(id=partition_id).delete()
    return redirect(reverse('users:home')) # Redirects to their new home screen

def get_bank(request):
    return Http404()
    if request.user:
        userprof = UserProfile.objects.filter(user=request.user).first()
        response = requests.get('http://127.0.0.1:7000/account-holder/1/')
        total = 0.0
        for bank_acc in response.json()['bank_accounts']:
            total += float(bank_acc['balance'])

        userprof.total_amount = total
        userprof.save()
        print(response.json())
        print(total)
    return redirect(reverse('users:home')) # Redirects to their new home screen
