from django.contrib import messages
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from partitions.models import Partition

from .helper_funcs import *

TEST_MESSAGES = False

# Create your views here.
def index(_):
    '''
    Index of the site. Just redirects to login page
    '''
    return redirect(reverse('logins:login'))

def empty_user_total(request):
    request.user.userprofile.total_amount = None
    request.user.userprofile.save()
    return redirect(reverse('users:home'))

def invalidate_user_token(request: HttpRequest):
    userprof = get_UserProfile(request.user)
    if userprof:
        userprof.valid_token = False
        userprof.refresh_token = None
        userprof.save()
    return redirect(reverse('users:home'))

def refresh_user_token(reqeust):
    if need_bank_login(reqeust, messages):
        return redirect(reverse('logins:get_bank'))
    return redirect(reverse('users:home'))

@login_required(login_url="/login/")
def user_home(request:HttpRequest):
    '''
    The home page view for a logged in user
    '''
    if TEST_MESSAGES:
        messages.success(request, "Success")
        messages.error(request, "Error")

    if request.user is None or not request.user.is_authenticated:
        return redirect(reverse('logins:login'))
    try:
        userprof = UserProfile.objects.get(user=request.user)
        total_amount = userprof.total_amount
    except UserProfile.DoesNotExist:
        total_amount = Decimal(-1.0)

    (unalloc, partitions) = Partition.update_unallocated_partition(request.user, total_amount=total_amount)
    sorted_partitions = sorted([obj for obj in partitions], key=lambda x: x.label.lower())
    try:
        userprof = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        logout(request)
        return redirect(reverse('users:home'))

    return render(request, Partition.get_partition_list_html(), context={"parent": "home.html", "unalloc": unalloc, "user_parts": sorted_partitions})

