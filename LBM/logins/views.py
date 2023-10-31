from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.urls import reverse

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
                    create_partition(user)

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
def get_bank(request):
    '''
    If no authentication token known, give login page. 
    On success or authentication known, get bank account info
    '''
    if 'bank_credentials' in request.session:
        account_info = request_bank_accounts("Dummy Bank", request.session['bank_credentials'])
        if account_info is None:
            messages.error(request, f'Failed to retrieve accounts')
            return render(request, 'bank_login.html')
        elif account_info.status_code == 401:
            # TODO: Refresh token before token expires
            return bank_login_form_sequence(request, messages)
        elif account_info.status_code != 200:
            messages.error(request, f'Failed to retrieve accounts code: {account_info.status_code}')
            return render(request, 'bank_login.html')
        update_user_total(account_info, request, messages)
        return redirect(reverse('users:home'))
    elif request.method == "POST":
        return bank_login_form_sequence(request, messages)
    else:
        return render(request, 'bank_login.html')

@login_required
def transfer(request):
    '''
    Transfer money from one account to another
    '''
    bank_accounts_list = get_bank_accounts("Dummy Bank", request, messages)
    try:
        form = BankTransferForm(bank_accounts=bank_accounts_list, data=request.POST or None)  # Moved this line here
    except:
        return redirect(reverse("logins:get_bank"))

    if bank_accounts_list is not None and request.method == 'POST':
        bank_accounts = {acc['id']: acc for acc in bank_accounts_list}
        if form.is_valid():
            from_acc = form.cleaned_data['from_bank_account']
            to_acc = form.cleaned_data['to_bank_account']
            amount = form.cleaned_data['amount']
            if from_acc != to_acc and Decimal(bank_accounts[from_acc]['balance']) >= amount:
                response = request_transfer("Dummy Bank", request, from_acc, to_acc, amount)
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
            print(form.errors.as_data())  # Moved this line here to print errors if form is not valid
            return render(request, "transfer.html", {'form': form})
    return render(request, "transfer.html", {'form': form})
