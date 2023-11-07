from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Partition, PartitionRule
from .forms import EditRule, NewPartiton, PartitionEditForm

from users.helper_funcs import *

# Create your views here.
@login_required(login_url="/login/")
def user_partition_view(request, partition_id):
    '''
    View for an individual partition page
    '''
    try:
        part = Partition.objects.get(id=partition_id)
        rules = PartitionRule.objects.filter(partition=part)
    except:
        messages.error(request, "Could Not Find Partition")
        return redirect(reverse('users:home'))
    return render(request, 'partition.html', {'partition_data': part, 'partition_rules': rules})

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

    if request.method == "POST":
        form = PartitionEditForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
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
            part = form.save(commit=True)
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

@login_required(login_url="/login/")
def edit_rule(request, rule_id):
    rule = PartitionRule.objects.get(id=rule_id)
    part = rule.get_partiton()
    form = EditRule(request.POST or None, instance=rule)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully changed rule")
            return redirect('partitions:partition', partition_id=part.id)
        else:
            messages.error(request, "Invalid form")
            return render(request, 'edit_rule.html', context={'form': form, 'part_id': part.id})
    else:
        form = EditRule(instance=rule)
        return render(request, 'edit_rule.html', context={'form': form, 'part_id': part.id})
