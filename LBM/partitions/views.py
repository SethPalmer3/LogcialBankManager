"""
views.py

Controls the view logic for partition related updates/changes

"""

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Partition, RuleBiopExpression
from .forms import NewPartiton, PartitionEditForm

from users.helper_funcs import *
from .partition_globals import *

@login_required(login_url="/login/")
def user_partition_view(request, partition_id):
    '''
    View for an individual partition page
    '''
    try:
        part = Partition.objects.get(id=partition_id)
        rules = RuleBiopExpression.objects.filter(partition=part, is_root=True)
    except:
        messages.error(request, "Could Not Find Partition")
        return redirect(reverse('users:home'))
    return render(request, 'partition.html', {'partition_data': part, 'root_rules': rules})

@login_required(login_url="/login/")
def user_partition_edit(request, partition_id):
    '''
    Edit page for a partition
    '''
    try:
        part = Partition.objects.get(id=partition_id)
    except Partition.DoesNotExist:
        messages.error(request, "Could Not Find partition")
        return redirect(reverse('users:home'))
    form = PartitionEditForm(data=request.POST or None, instance=part)
    if request.method == "POST":
        if form.is_valid():
            change_fields = []
            change_fields += set_changed_field(part, form.LABEL, form.cleaned_data[form.LABEL])
            change_fields += set_changed_field(part, form.CURRENT_AMOUNT, form.cleaned_data[form.CURRENT_AMOUNT])
            change_fields += set_changed_field(part, form.DESCRIPTION, form.cleaned_data[form.DESCRIPTION])
            part.save(update_fields=change_fields)
            messages.success(request, "Successfully changed partiton")
            return redirect('partitions:partition', partition_id=partition_id)
        else:
            print(form.errors)
    else:
        form = PartitionEditForm(instance=part)

    return render(request, "edit_partition.html", {'form': form, 'partition_id': partition_id})

@login_required(login_url="/login/")
def add_partition(request):
    '''
    Add a partition page
    '''
    if request.method == "POST":
        form = NewPartiton(request.POST)
        if form.is_valid():
            part: Partition = form.save(commit=True)
            part.init_amount = part.current_amount
            part.owner = request.user
            part.save()
            messages.success(request, f'Successfully created a partition {part.label}')
            return redirect('partitions:partition', partition_id=part.id)
    else:
        form = NewPartiton()
    return render(request, "add_partition.html", {'form': form})

@login_required(login_url="/login/")
def remove_partiton(request, partition_id):
    '''
    Remove partition page
    '''
    try:
        p = Partition.objects.get(id=partition_id)
        if p is not None and not p.is_unallocated:
            label = p.label
            p.delete()
            messages.success(request, f"Successfully deleted partition {label}")
        else:
            messages.error(request, "Could not delete partitoin")
        
    except:
        messages.error(request, "Couldn\'t find partition")

    return redirect(reverse('users:home')) # Redirects to their new home screen
