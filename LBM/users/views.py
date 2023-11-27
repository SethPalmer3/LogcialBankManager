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
def user_home(request: HttpRequest):
    '''
    The home page view for a logged in user
    '''
    if TEST_MESSAGES:
        messages.success(request, "Success")
        messages.error(request, "Error")

    if request.user is None or not request.user.is_authenticated:
        return redirect(reverse('logins:login'))
    partitions = Partition.objects.filter(owner=request.user, is_unallocated=False)
    sorted_partitions = sorted([obj for obj in partitions], key=lambda x: x.label.lower())
    try:
        userprof = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        logout(request)
        return redirect(reverse('users:home'))

    diff = check_partitions(partitions, request.user)
    try:
        unallocated_partition: Partition|None = Partition.objects.get(owner=request.user, is_unallocated=True)
    except Partition.DoesNotExist:
        unallocated_partition = None

    if diff is None or userprof.total_amount is None: # Checks if userprof has a total_amount
        if unallocated_partition is not None:
            unallocated_partition.delete()
            unallocated_partition = None
        try:
            unallocated_partition: Partition|None = Partition.objects.get(owner=request.user, is_unallocated=True)
        except Partition.DoesNotExist:
            unallocated_partition = None
        partitions = Partition.objects.filter(owner=request.user, is_unallocated=False)
        sorted_partitions = sorted([obj for obj in partitions], key=lambda x: x.label.lower())
        return render(request, 'home.html', {'user_parts': partitions, 'user_profile': userprof, 'unalloc': unallocated_partition})

    if diff >= 0.0: # checking if partition total is the same or lower than user total
        if unallocated_partition is not None:
            unallocated_partition.current_amount = diff
            unallocated_partition.save()
        else:
            create_partition(request.user, True, "Unallocated", Decimal(diff))
    else: # If the partition allocation is bigger than user total
        if unallocated_partition is not None:
            if unallocated_partition.current_amount + diff >= 0.0:
                unallocated_partition.current_amount += diff
                unallocated_partition.save()
            else:
                unallocated_partition.delete()
                unallocated_partition = None
                messages.error(request, f"Over allocated balance by ${abs(diff)}")
        else:
            messages.error(request, f"Over allocated balance by ${abs(diff)}")
    try:
        unallocated_partition: Partition|None = Partition.objects.get(owner=request.user, is_unallocated=True)
    except Partition.DoesNotExist:
        unallocated_partition = None
    partitions = Partition.objects.filter(owner=request.user, is_unallocated=False)
    sorted_partitions = sorted([obj for obj in partitions], key=lambda x: x.label.lower())
    return render(request, 'home.html', {'user_parts': sorted_partitions, 'user_profile': userprof, 'unalloc': unallocated_partition})

