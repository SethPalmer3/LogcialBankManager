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

# @login_required(login_url="/login/")
# def user_partition_view(request, partition_id):
#     '''
#     View for an individual partition page
#     '''
#     try:
#         part = Partition.objects.get(id=partition_id)
#     except:
#         messages.error(request, "Could Not Find Partition")
#         return redirect(reverse('users:home'))
#     return render(request, 'partition.html', {'partition_data': part})

# @login_required(login_url="/login/")
# def user_partition_edit(request, partition_id):
#     '''
#     Edit page for a partition
#     '''
#     try:
#         part = Partition.objects.get(id=partition_id)
#     except Partition.DoesNotExist:
#         messages.error(request, "Could Not Find partition")
#         return redirect(reverse('users:home'))

#     if request.method == "POST":
#         form = PartitionEditForm(request.POST, instance=part)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Successfully changed partiton")
#             return redirect('users:partition', partition_id=partition_id)
#     else:
#         form = PartitionEditForm(instance=part)

#     return render(request, "partition_edit.html", {'form': form, 'partition_id': partition_id})

# @login_required(login_url="/login/")
# def add_partition(request):
#     '''
#     Add a partition page
#     '''
#     if request.method == "POST":
#         form = NewPartiton(request.POST)
#         if form.is_valid():
#             part = form.save(commit=True)
#             part.owner = request.user
#             part.save()
#             messages.success(request, f'Successfully created a partition {part.label}')
#             return redirect('users:partition', partition_id=part.id)
#     else:
#         form = NewPartiton()
#     return render(request, "add_partition.html", {'form': form})

# @login_required(login_url="/login/")
# def remove_partiton(request, partition_id):
#     '''
#     Remove partition page
#     '''
#     try:
#         p = Partition.objects.get(id=partition_id)
#         if p is not None and not p.is_unallocated:
#             label = p.label
#             p.delete()
#             messages.success(request, f"Successfully deleted partition {label}")
#         else:
#             messages.error(request, "Could not delete partitoin")
#         
#     except:
#         messages.error(request, "Couldn\'t find partition")

#     return redirect(reverse('users:home')) # Redirects to their new home screen
