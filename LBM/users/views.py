from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile, Partition
from .forms import NewPartiton, PartitionEditForm

from .helper_funcs import *


# Create your views here.
def index(request):
    return redirect(reverse('logins:login'))

@login_required(login_url="/login/")
def user_home(request):
    print(vars(request.session))
    if request.user is None or not request.user.is_authenticated:
        return redirect(reverse('logins:login'))
    partitons = Partition.objects.filter(owner=request.user)
    userprof = UserProfile.objects.filter(user=request.user).first()
    diff = check_partitions(partitons, request.user)
    print(diff)
    if diff >= 0.0:
        part = Partition.objects.filter(is_unallocated=True).first()
        if part is not None:
            part.current_amount = diff
            part.save()
        else:
            create_partition(request.user, True, "Unallocated", diff)
            partitons = Partition.objects.filter(owner=request.user)
    elif diff < 0.0:
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
    return render(request, 'home.html', {'user_parts': partitons, 'user_profile': userprof})

@login_required(login_url="/login/")
def user_partition_view(request, partition_id):
    try:
        part = Partition.objects.get(id=partition_id)
    except:
        messages.error(request, "Could Not Find Partition")
        return redirect(reverse('users:home'))
    return render(request, 'partition.html', {'partition_data': part})

@login_required(login_url="/login/")
def user_partition_edit(request, partition_id):
    try:
        part = Partition.objects.get(id=partition_id)
    except Partition.DoesNotExist:
        messages.error(request, "Could Not Find partition")
        return redirect(reverse('users:home'))

    if request.method == "POST":
        form = PartitionEditForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            return redirect('users:partition', partition_id=partition_id)
    else:
        form = PartitionEditForm(instance=part)

    return render(request, "partition_edit.html", {'form': form, 'partition_id': partition_id})

@login_required(login_url="/login/")
def add_partition(request):
    if request.method == "POST":
        form = NewPartiton(request.POST)
        if form.is_valid():
            part = form.save(commit=True)
            part.owner.set([request.user])
            part.save()
            return redirect('users:partition', partition_id=part.id)
    else:
        form = NewPartiton()
    return render(request, "add_partition.html", {'form': form})

@login_required(login_url="/login/")
def remove_partiton(request, partition_id):
    try:
        Partition.objects.get(id=partition_id).delete()
    except:
        messages.error(request, "Couldn\'t find partition")

    return redirect(reverse('users:home')) # Redirects to their new home screen

def get_bank(request):
    '''
    Actually retreiving bank info
    '''
    if request.session['bank_credentials']:
        print(request.session['bank_credentials'])
        account_info = request_bank_accounts("Dummy Bank", request.session['bank_credentials'])
        # TODO: Take care of exception when token expires
        if account_info is None:
            messages.error(request, f'Failed to retrieve accounts')
            return render(request, 'bank_login.html')
        elif account_info.status_code == 401:
            return bank_login_form_sequence(request, messages)

        elif account_info.status_code != 200:
            messages.error(request, f'Failed to retrieve accounts code: {account_info.status_code}')
            return render(request, 'bank_login.html')


        update_user_profile(account_info, request, messages)
        return redirect(reverse('users:home'))
    elif request.method == "POST":
        return bank_login_form_sequence(request, messages)
