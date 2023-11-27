from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.urls import reverse
from requests import RequestException

from users.models import UserProfile
from .forms import BankTransferForm, SignUpForm
from users.helper_funcs import *

# Create your views here.
def user_login(request):
    '''
    User login page view
    '''
    if request.user.is_authenticated:
        return redirect(reverse('users:home'))

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('users:home'))
            else:
                messages.error(request, "Account is inactive")
        else:
            messages.error(request, "Invalid Credentials")
            # return render(request, 'login.html', {'error': 'Invalid Credentials'})
        return render(request, 'login.html')

    return render(request, 'login.html')

def user_logout(request):
    '''
    User logout view. No page.
    '''
    logout(request)
    return redirect(reverse('logins:login'))

def user_signup(request):
    '''
    User signup page view
    '''
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
                    create_partition(user, is_unallocated=True)

                login(request, user) # Persistant login of user
                return redirect(reverse('users:home')) # Redirects to their new home screen
            except Exception as e:
                messages.error(request, f"{e}")
                form = SignUpForm()
                return render(request, 'signup.html', {'form': form, 'error': e})
                
    else: # First time going to page
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def get_bank(request, return_url='/home/'):
    '''
    If no authentication token known, give login page. 
    On success or authentication known, get bank account info
    '''
    userprof = request.user.userprofile
    if userprof is None:
        messages.error(request, "Can not find users profile")
        return redirect(reverse('users:home'))

    if userprof.bank is None:
        return select_bank_sequence(request, messages)
    try: 
        if request.method == "POST": # If submitting a login
            return bank_login_form_sequence(request, messages)

        if need_bank_login(request, messages): # If cannot refresh token send bank login
            return render(request, 'bank_login.html')
    except RequestException as e:
        messages.error(request, f"Cannot make connection to {userprof.bank.__str__()}")
        return redirect(reverse('users:home'))
    if userprof.valid_token: # checking if valid credentials
        account_info = request_bank_accounts("Dummy Bank", userprof.token_type, userprof.access_token)
        try:
            update_user_total(account_info, request, messages)
            return redirect(return_url)
        except Exception as e:
            messages.error(request, f"{e}")
            return render(request, 'bank_login.html')
    else:
        return render(request, 'bank_login.html')

def select_bank(request):
    banks = [{'id': b.id.__str__(), 'name': b.name} for b in ExternalWebApp.objects.all()]
    try:
        bank_form = BankSelectForm(banks=banks, data=request.POST or None)
    except Exception as e:
        messages.error(request, f"Cant create bank select form {e}")
        return redirect(reverse('users:home'))
    if request.method == "POST":
        # Make selection
        if bank_form.is_valid():
            selected_bank_data = bank_form.cleaned_data['bank_select']
            print(selected_bank_data)
            selected_bank = ExternalWebApp.objects.get(id=selected_bank_data)
            userprof = request.user.userprofile
            if userprof is None:
                messages.error(request, "Could not find user profile")
                return redirect(reverse('users:home'))
            userprof.bank = selected_bank
            userprof.save()
        return redirect(reverse('logins:get_bank'))
    else:
        # Provide selections
        return render(request, 'bank_select.html', context={'form': bank_form})


@login_required
def transfer(request):
    '''
    Transfer money from one account to another
    '''
    if need_bank_login(request, messages):
        return redirect(reverse('logins:get_bank'), return_url=reverse('logins:transfer'))
    bank_accounts_list = get_bank_accounts("Dummy Bank", request, messages)
    # TODO test this
    if bank_accounts_list is None:
        return redirect(reverse("logins:get_bank"))
    form = BankTransferForm(bank_accounts=bank_accounts_list, data=request.POST or None)

    if bank_accounts_list is not None and request.method == 'POST':
        bank_accounts = {acc['id']: acc for acc in bank_accounts_list}
        if form.is_valid():
            from_acc = form.cleaned_data['from_bank_account']
            to_acc = form.cleaned_data['to_bank_account']
            amount = form.cleaned_data['amount']
            if from_acc != to_acc and Decimal(bank_accounts[from_acc]['balance']) >= amount:
                response = request
                if response is not None:
                    if response.status_code == 200:
                        messages.success(request, "Successful transfer")
                        return redirect(reverse("users:home"))
                    else:
                        messages.error(request, "Failed to transfer")
                        return redirect(reverse("users:home"))
                else:
                    messages.error(request, "Failed to make transfer request")
                    return redirect(reverse("users:home"))
        else:
            return render(request, "transfer.html", {'form': form})
    return render(request, "transfer.html", {'form': form})
