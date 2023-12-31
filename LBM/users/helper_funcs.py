from datetime import timezone
from decimal import Decimal
# from uuid import uuid4
from django.contrib import messages
from django.core.handlers.asgi import HttpRequest
from django.db.models import QuerySet, UUIDField
from django.shortcuts import redirect, render
from django.urls import reverse
import requests
from requests.auth import HTTPBasicAuth
from rest_framework.fields import datetime

from logins.forms import BankSelectForm
from .models import ExternalWebApp, UserProfile
from partitions.models import Partition

def check_partitions( partitons: QuerySet, user=None, total_amount = 0.0) -> float|None:
    """Checks if the query set of partitons amounts are allowed. if user is non 

    Args:
        partitons(QuerySet): The query set of partitions
        user(User | None): the associated user profile(default=None)
        total_amount(Decimal): The amount to check against(if user is None)

    Returns: 
        float|None: the difference from the allowed total and the partition total
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

def create_partition(owner, is_unallocated=False, label="Undefined", amount = Decimal(0.00), description=""):
    """
    Creates and returns a new partition

    Args:
        owner(User): User model associated with the new partition
        label(str): Label for new partition(default="Undefined")
        amount(Decimal): Starting amount(default=0.0)
        description(str): description of the partition

    Returns:
        Partition: The new partition
    """
    first_partition = Partition.objects.create()
    first_partition.owner = owner
    first_partition.is_unallocated = is_unallocated
    first_partition.label = label
    first_partition.current_amount = amount
    first_partition.description = description
    first_partition.save()
    return first_partition

def get_UserProfile(user) -> UserProfile | None:
    """
    Returns the associated user profile model
    """
    return UserProfile.objects.filter(user=user).first()

def bank_login_auth(name: str, username: str, password: str) -> requests.Response | None:
    """Make a web request to bank to get credentials with login information

    Args:
        name (str): Name of the External Web App to call to.
        username (str): username associated with that Web App.
        password (str): Password associated with that Web App.
    Returns:
        requests.Response | None: Either the responded object from the Web App or None if no Web App with `name` was found
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

def request_bank_accounts(name: str, token_type: str, access_token: str) -> requests.Response | None:
    """Makes a web requests to a external web app of an already authenticated user to get their bank accounts.
    Args:
        name(str): Name of External Web App.
        token_type(str): Type of token for request
        access_token(str): Complementary access token
    Returns:
        requests.Response|None: The response object of the request or `None` if no Web App was found with `name`.

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

def request_refresh_access_token(request):
    '''
    Request a refreshed access token. Updates user profile.
    '''
    userprof = request.user.userprofile
    if userprof is not None:
        bank = userprof.bank
        if bank is not None:
            request_obj = bank.get_bank_account['refresh']
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': userprof.refresh_token,
            }
            response = requests.post(
                request_obj['url'],
                data=data,
                auth=HTTPBasicAuth(bank.client_key, bank.secret_key)
            )
            return response

def is_access_token_valid(request, acceptable_delta=15000):
    '''
    Checks if the users current access token is still valid.
    The acceptable delta is defined here.
    '''
    userprof = request.user.userprofile
    if userprof is not None and userprof.valid_token:
        delta = datetime.datetime.now(timezone.utc) - userprof.last_refreshed
        if delta.seconds >= acceptable_delta: # if token is invalid
            userprof.valid_token = False
            userprof.save()
            return False
        else:
            return True
    return False

def need_bank_login(request, messages):
    '''
    Check if an access token is expired.
    If so, refresh the token.
    returns if a bank login sequence is needed
    '''
    userprof = request.user.userprofile
    if userprof is None:
        messages.error(request, "Could not find user profile")
        return False

    if not is_access_token_valid(request, 60):
        response = request_refresh_access_token(request)
        if response is None:
            messages.error(request, "Could not make refresh request")
            return False
        if response.status_code == 200:
            res_json = response.json()
            userprof.access_token = res_json['access_token']
            userprof.token_type = res_json['token_type']
            userprof.last_refreshed = datetime.datetime.now(timezone.utc)
            userprof.token_expire_time = res_json['expires_in']
            userprof.refresh_token = res_json['refresh_token']
            userprof.valid_token = True
            userprof.save()
            messages.success(request, "Token Successfully refreshed")
            return False
        elif response.status_code == 401:
            return True
        else:
            messages.error(request, "Token could not be refreshed")
            return True
    else:
        messages.error(request, "Token doesn't need to be refreshed yet")
        return False


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

def get_bank_accounts(name:str, request:HttpRequest, messages):
    '''
    Get bank accounts. Does not automatically redirect to bank login
    '''
    if request.user:
        userprof = get_UserProfile(request.user)
    else: 
        return None
    if userprof is not None and userprof.valid_token:
        account_info = request_bank_accounts(name, userprof.token_type, userprof.access_token)
        if account_info is None:
            messages.error(request, f'Failed to retrieve accounts')
            return None
        return account_info.json()['account_holder']['bank_accounts']
    else:
        messages.error(request, "Please login before getting bank accounts")
    return None

def select_bank_sequence(request: HttpRequest, messages):
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
            selected_bank: ExternalWebApp|None = ExternalWebApp.objects.get(id=selected_bank_data)
            userprof = get_UserProfile(request.user)
            if userprof is None:
                messages.error(request, "Could not find user profile")
                return redirect(reverse('users:home'))
            userprof.bank = selected_bank
            userprof.save()
        return redirect(reverse('logins:get_bank'))
    else:
        # Provide selections
        return render(request, 'bank_select.html', context={'form': bank_form})

def request_transfer(name:str, request:HttpRequest, from_acc:str, to_acc:str, amount):
    bank = ExternalWebApp.objects.filter(name=name).first()
    userprof = get_UserProfile(request.user)
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
    elif userprof and not userprof.valid_token:
        messages.error(request, "Please login before making transfer")
    return None
