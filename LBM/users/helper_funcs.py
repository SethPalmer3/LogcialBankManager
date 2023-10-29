from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse
import requests
from requests.auth import HTTPBasicAuth
from .models import ExternalWebApp, Partition, UserProfile

def check_partitions( partitons: QuerySet, user=None, total_amount = 0.0):
    """
    checks if the query set of partitons amounts are allowed. if user is non 

    partitons: The query set of partitions
    user: the associated user profile(default=None)
    total_amount: The amount to check against(if user is None)

    Return: the difference from the allowed total and the partition total
    """
    if total_amount < 0.0:
        return 0.0
    total = 0
    for p in partitons:
        total += p.current_amount

    if user is None:
        return total_amount - total
    userprof = UserProfile.objects.filter(user=user).first()
    try:
        return userprof.total_amount - total
    except:
        return 0.0

def create_partition(owner, label="Undefined", amount = 0.0):
    """
    Creates and returns a new partition

    owner: User model associated with the new partition
    label: Label for new partition(default="Undefined")
    amount: Starting amount(default=0.0)

    Return: the new partition
    """
    first_parition = Partition.objects.create()
    first_parition.owner.add(owner)
    first_parition.label = label
    first_parition.current_amount = amount
    first_parition.save()
    return first_parition

def get_UserProfile(user):
    """
    Returns the associated user profile model
    """
    return UserProfile.objects.filter(user=user).first()

def request_bank_info(name, username, password):
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

def request_bank_accounts(name, response_obj):
    bank = ExternalWebApp.objects.filter(name=name).first()
    if bank is not None:
        request_obj = bank.get_bank_account['get_accounts']
        headers = {
            'Authorization': f"{response_obj['token_type']} {response_obj['access_token']}",
        }
        response = requests.get(request_obj['url'], headers=headers)
        return response
    return None

def update_user_profile(account_info, request, messages):
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
