from datetime import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from partitions.models import Partition

from .helper_funcs import *

# Create your views here.
def index(request):
    '''
    Index of the site. Just redirects to login page
    '''
    return redirect(reverse('logins:login'))

def clear_token(request):
    request.user.userprofile.valid_token = False
    request.user.userprofile.save()
    return redirect(reverse('users:home'))

@login_required(login_url="/login/")
def user_home(request):
    '''
    The home page view for a logged in user
    '''

    if request.user is None or not request.user.is_authenticated:
        return redirect(reverse('logins:login'))
    partitons = Partition.objects.filter(owner=request.user)
    userprof = UserProfile.objects.filter(user=request.user).first()
    # print((datetime.datetime.now(timezone.utc) - userprof.last_refreshed).seconds)

    diff = check_partitions(partitons, request.user)
    unallocated_partition = Partition.objects.filter(is_unallocated=True).first()
    if diff is None or userprof.total_amount is None: # Checks if userprof has a total_amount
        if unallocated_partition is not None:
            unallocated_partition.delete()
        partitons = Partition.objects.filter(owner=request.user)
        return render(request, 'home.html', {'user_parts': partitons, 'user_profile': userprof})

    if diff >= 0.0: # checking if partition total is the same or lower than user total
        if unallocated_partition is not None:
            unallocated_partition.current_amount = diff
            unallocated_partition.save()
        else:
            create_partition(request.user, True, "Unallocated", diff)
            partitons = Partition.objects.filter(owner=request.user)
    else: # If the partition allocation is bigger than user total
        if unallocated_partition is not None:
            if unallocated_partition.current_amount + diff >= 0.0:
                unallocated_partition.current_amount += diff
                unallocated_partition.save()
            else:
                unallocated_partition.delete()
                messages.error(request, f"Over allocated balance by ${abs(diff)}")
        else:
            messages.error(request, f"Over allocated balance by ${abs(diff)}")
    partitons = Partition.objects.filter(owner=request.user)
    return render(request, 'home.html', {'user_parts': partitons, 'user_profile': userprof})

