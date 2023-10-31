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

@login_required(login_url="/login/")
def user_home(request):
    '''
    The home page view for a logged in user
    '''
    if request.user is None or not request.user.is_authenticated:
        return redirect(reverse('logins:login'))
    partitons = Partition.objects.filter(owner=request.user)
    userprof = UserProfile.objects.filter(user=request.user).first()
    diff = check_partitions(partitons, request.user)
    if diff >= 0.0: # checking if partition total is the same or lower than user total
        part = Partition.objects.filter(is_unallocated=True).first()
        if part is not None:
            part.current_amount = diff
            part.save()
        else:
            create_partition(request.user, True, "Unallocated", diff)
            partitons = Partition.objects.filter(owner=request.user)
    else: # If the partition allocation is bigger than user total
        part = Partition.objects.filter(is_unallocated=True).first()
        if part is not None:
            if part.current_amount + diff >= 0.0:
                part.current_amount += diff
                part.save()
            else:
                part.delete()
                messages.error(request, f"Over allocated balance by ${abs(diff)}")
        else:
            messages.error(request, f"Over allocated balance by ${abs(diff)}")
    partitons = Partition.objects.filter(owner=request.user)
    return render(request, 'home.html', {'user_parts': partitons, 'user_profile': userprof})

