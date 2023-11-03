from datetime import timezone
from django.contrib import messages
from django.db.models import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse
import requests
from requests.auth import HTTPBasicAuth
from rest_framework.fields import datetime
from .models import ExternalWebApp, UserProfile
from partitions.models import Partition

def check_partitions( partitons: QuerySet, user=None, total_amount = 0.0):
    """
    checks if the query set of partitons amounts are allowed. if user is non 

    partitons: The query set of partitions
    user: the associated user profile(default=None)
    total_amount: The amount to check against(if user is None)

    Return: the difference from the allowed total and the partition total
    """
    if total_amount < 0.0:
        return None
    total = 0
    for p in partitons:
        if not p.is_unallocated:
            total += p.current_amount

    if user is None:
        return total_amount - total
    userprof = UserProfile.objects.filter(user=user).first()
    if userprof is not None and userprof.total_amount is not None:
        return userprof.total_amount - total
    else:
        return None

def create_partition(owner, is_unallocated=False, label="Undefined", amount = 0.0, description=""):
    """
    Creates and returns a new partition

    owner: User model associated with the new partition
    label: Label for new partition(default="Undefined")
    amount: Starting amount(default=0.0)
    description: description of the partition

    Return: the new partition
    """
    first_partition = Partition.objects.create()
    first_partition.owner = owner
    first_partition.is_unallocated = is_unallocated
    first_partition.label = label
    first_partition.current_amount = amount
    first_partition.description = description
    first_partition.save()
    return first_partition

def get_UserProfile(user):
    """
    Returns the associated user profile model
    """
    return UserProfile.objects.filter(user=user).first()

def bank_login_auth(name, username, password):
    """
    Make a web request to bank to get credentials
    """
    bank = ExternalWebApp.objects.filter(name=name).first()
    if bank is not None:
        request_obj = bank.get_bank_account
        req_creds = request_obj['get_credentials']
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
        }
        response = requests.post(
            req_creds['url'],
            data=data,
            auth=HTTPBasicAuth(bank.client_key, bank.secret_key)
        )
        return response
    return None

def request_bank_accounts(name, token_type, access_token):
    """
    Make a web request to bank to get bank account information
    """
    bank = ExternalWebApp.objects.filter(name=name).first()
    if bank is not None:
        request_obj = bank.get_bank_account['get_accounts']
        headers = {
            'Authorization': f"{token_type} {access_token}",
        }
        response = requests.get(request_obj['url'], headers=headers)
        return response
    return None

def update_user_total(account_info, request, messages):
    """
    From account_info which holds bank account information. 
    Update the total amount the user can partition
    """
    accounts = account_info.json()['account_holder']['bank_accounts']
    total = 0.0
    for acc in accounts:
        total += float(acc['balance'])

    userprof = get_UserProfile(request.user)
    if userprof is None:
        messages.error(request, 'User Profile does not exist')
        return None

    userprof.total_amount = total
    userprof.save()
    messages.success(request, "Successfully updated user profile total")
    return None

def bank_login_form_sequence(request, messages):
    """
    Makes a request to bank to get credentials from login form.
    On success, stores the credentials in session
    """
    try:
        credentials = bank_login_auth("Dummy Bank", request.POST['username'], request.POST['password'])
        if credentials is None or credentials.status_code != 200:
            messages.error(request, 'Failed to log into Bank')
            return render(request, 'bank_login.html')
        cred_details = credentials.json()

        userprof = request.user.userprofile
        if userprof is None:
            messages.error(request, 'Could not find user profile')
            return render(request, 'bank_login.html')
        userprof.access_token = cred_details['access_token']
        userprof.token_type = cred_details['token_type']
        userprof.last_refreshed = datetime.datetime.now(timezone.utc)
        userprof.token_expire_time = cred_details['expires_in']
        userprof.refresh_token = cred_details['refresh_token']
        userprof.valid_token = True
        userprof.save()

        messages.success(request, "Successfully logged into bank")
        account_info = request_bank_accounts("Dummy Bank", userprof.token_type, userprof.access_token)
        if account_info is None or account_info.status_code != 200:
            messages.error(request, 'Failed to retrieve accounts')
            return render(request, 'bank_login.html')

        update_user_total(account_info, request, messages)
        return redirect(reverse('users:home'))

    except requests.RequestException as e:
        messages.error(request, f"Error fetching bank data: {e}")
    return render(request, 'bank_login.html')

def get_bank_accounts(name, request, messages):
    '''
    Get bank accounts. Does not automatically redirect to bank login
    '''
    userprof = request.user.userprofile
    if userprof is not None and userprof.valid_token:
        account_info = request_bank_accounts(name, userprof.token_type, userprof.access_token)
        if account_info is None:
            messages.error(request, f'Failed to retrieve accounts')
            return None
        return account_info.json()['account_holder']['bank_accounts']
    else:
        # TODO: Redirect to external bank login and retry
        messages.error(request, "Please login before getting bank accounts")
    return None

def request_transfer(name, request, from_acc, to_acc, amount):
    bank = ExternalWebApp.objects.filter(name=name).first()
    userprof = request.user.userprofile
    if bank is not None and userprof is not None and userprof.valid_token:
        request_obj = bank.get_bank_account['transfer']
        headers = {
            'Authorization': f"{userprof.token_type} {userprof.access_token}",
        }
        data = request_obj['data']
        data['from_account_id'] = from_acc
        data['to_account_id'] = to_acc
        data['amount'] = amount
        response = requests.post(request_obj['url'], headers=headers, data=data)
        return response
    elif not userprof.valid_token:
        messages.error(request, "Please login before making transfer")
    return None

# def request_transfer(name, request, from_acc, to_acc, amount):
#     bank = ExternalWebApp.objects.filter(name=name).first()
#     if bank is not None and 'bank_credentials' in request.session:
#         response_obj = request.session['bank_credentials']
#         request_obj = bank.get_bank_account['transfer']
#         headers = {
#             'Authorization': f"{response_obj['token_type']} {response_obj['access_token']}",
#         }
#         data = request_obj['data']
#         data['from_account_id'] = from_acc
#         data['to_account_id'] = to_acc
#         data['amount'] = amount
#         response = requests.post(request_obj['url'], headers=headers, data=data)
#         return response
#     elif 'bank_credentials' not in request.session:
#         messages.error(request, "Please login before making transfer")
#     return None

