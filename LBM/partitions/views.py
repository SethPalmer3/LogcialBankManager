from django.db import transaction
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from requests import delete

from .models import Partition, Rule, RuleBiopExpression, RuleUniopExpression
from .forms import NewPartiton, PartitionEditForm, RuleAttributeSelectForm, RuleExpressionAddForm, RuleExpressionEditForm, RuleNameAndEntitySelectForm, RuleOperatorSelectForm, RuleValueSetForm 

from users.helper_funcs import *

# Create your views here.
@login_required(login_url="/login/")
def user_partition_view(request, partition_id):
    '''
    View for an individual partition page
    '''
    try:
        part = Partition.objects.get(id=partition_id)
    except:
        messages.error(request, "Could Not Find Partition")
        return redirect(reverse('users:home'))
    return render(request, 'partition.html', {'partition_data': part})

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
def add_rule(request, partition_id):
    user = request.user
    # userprof = user.userprofile
    part = Partition.objects.get(id=partition_id)
    form = RuleNameAndEntitySelectForm(user_id=user.id, partition_id=part.id, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new_rule = Rule()
            (new_rule.entity_id, new_rule.entity_type, new_rule.entity_name) = form.cleaned_data['entity'].split(',')
            new_rule.name = form.cleaned_data['name']
            new_rule.partition = part
            new_rule.save()
            return redirect('partitions:set_attribute', rule_id=new_rule.id)
    return render(request, 'rule_step.html', context={'form': form})

@login_required(login_url="/login/")
def set_rule_attribute(request, rule_id):
    # user = request.user
    rule = Rule.objects.get(id=rule_id)
    form = RuleAttributeSelectForm(ent_type=rule.entity_type, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            rule.attribute = form.cleaned_data['attribute']
            rule.attribute_type = "float"
            rule.save()
            return redirect('partitions:set_operation', rule_id=rule_id)
    return render(request, 'rule_step.html', context={'form': form})

@login_required(login_url="/login/")
def set_rule_operator(request, rule_id):
    rule = Rule.objects.get(id=rule_id)
    form = RuleOperatorSelectForm(attr_type=rule.attribute_type,data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            rule.operation = form.cleaned_data['operators']
            rule.save()
            return redirect('partitions:set_value', rule_id=rule_id)
    return render(request, 'rule_step.html', context={'form': form})

@login_required(login_url="/login/")
def set_rule_value(request, rule_id):
    rule = Rule.objects.get(id=rule_id)
    form = RuleValueSetForm(type_s=rule.attribute_type, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            rule.value = form.cleaned_data['value']
            rule.save()
            return redirect('partitions:partition', partition_id=rule.partition.id)
    return render(request, 'rule_step.html', context={'form': form})

@login_required(login_url="/login/")
def rule_expr_view(request, partition_id):
    # root_expr = RuleBiopExpression.objects.all().first()
    part = Partition.objects.get(id=partition_id)
    root_expr = RuleBiopExpression.objects.get(partition=part, is_root=True)
    return render(request, 'rule_expr.html', context={'expr': root_expr})

@login_required(login_url="/login/")
def rule_expr_edit(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    form = RuleExpressionEditForm(instance=expr_node, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if expr_node.is_value:
                if expr_node.value.is_reference:
                    (ref_id, ref_type, _) = form.cleaned_data['ref_ents'].split(',')
                    (ref_t, ref_attr) = form.cleaned_data['ref_attrs'].split(',')
                    if ref_type != ref_t:
                        messages.error(request, "The attribute doesn't fit the entity")
                        return render(request, 'rule_expr_edit.html', context={'form': form, 'partition_id': expr_node.partition.id, 'expr': expr_node})
                    with transaction.atomic():
                        # print(f"{ref_id} {ref_type} {ref_attr}")
                        expr_node.value.reference_id = ref_id
                        expr_node.value.reference_type = ref_type
                        expr_node.value.reference_attr = ref_attr
                        expr_node.value.save()
                else:
                    expr_node.value.set_appropiate_value(form.cleaned_data['value_input'])
                    expr_node.value.save()
            else:
                expr_node.operator = form.cleaned_data['operator']
                expr_node.save()
            return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)
    return render(request, 'rule_expr_edit.html', context={'form': form, 'partition_id': expr_node.partition.id, 'expr': expr_node})

@login_required(login_url="/login/")
def rule_expr_unset_l(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    expr_node.left_expr.delete()
    return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)

@login_required(login_url="/login/")
def rule_expr_unset_r(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    expr_node.right_expr.delete()
    return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)

@login_required(login_url="/login/")
def rule_expr_set_l(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    user = request.user
    part = expr_node.partition
    form = RuleExpressionAddForm(user_id=user.id, partition_id=part.id, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if form.cleaned_data['expr_type'] == 'value':
                with transaction.atomic():
                    new_value = RuleUniopExpression()
                    new_value.value_type = form.cleaned_data['value_type']
                    new_value.set_appropiate_value(form.cleaned_data['value_input'])
                    new_value.save()
                    new_expr = RuleBiopExpression()
                    new_expr.partition = expr_node.partition
                    new_expr.value = new_value
                    new_expr.is_value = True
                    new_expr.save()
                    expr_node.left_expr = new_expr
                    expr_node.save()
                return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)
            elif form.cleaned_data['expr_type'] == 'operation':
                with transaction.atomic():
                    new_op = RuleBiopExpression()
                    new_op.partition = expr_node.partition
                    new_op.operator = form.cleaned_data['operator']
                    new_op.save()
                    expr_node.left_expr = new_op
                    expr_node.save()
            elif form.cleaned_data['expr_type'] == 'reference':
                with transaction.atomic():
                    (ref_id, ref_type, ref_name) = form.cleaned_data['ref_ents'].split(',')
                    (ref_t, ref_attr) = form.cleaned_data['ref_attrs'].split(',')
                    with transaction.atomic():
                        new_ref = RuleUniopExpression()
                        new_ref.is_reference = True;
                        new_ref.reference_id = ref_id
                        new_ref.reference_type = ref_type
                        new_ref.reference_attr = ref_attr
                        new_ref.save()
                        new_biop = RuleBiopExpression()
                        new_biop.is_value = True
                        new_biop.partition = expr_node.partition
                        new_biop.value = new_ref
                        new_biop.save()
                        expr_node.left_expr = new_biop
                        expr_node.save()
                return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)
    return render(request, "rule_expr_add.html", context={'form': form, 'partition_id': expr_node.partition.id})

@login_required(login_url="/login/")
def rule_expr_set_r(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    user = request.user
    part = expr_node.partition
    form = RuleExpressionAddForm(user_id=user.id, partition_id=part.id, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if form.cleaned_data['expr_type'] == 'value':
                with transaction.atomic():
                    new_value = RuleUniopExpression()
                    new_value.value_type = form.cleaned_data['value_type']
                    new_value.set_appropiate_value(form.cleaned_data['value_input'])
                    new_value.save()
                    new_expr = RuleBiopExpression()
                    new_expr.partition = expr_node.partition
                    new_expr.value = new_value
                    new_expr.is_value = True
                    new_expr.save()
                    expr_node.right_expr = new_expr
                    expr_node.save()
                return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)
            elif form.cleaned_data['expr_type'] == 'operation':
                with transaction.atomic():
                    new_op = RuleBiopExpression()
                    new_op.partition = expr_node.partition
                    new_op.operator = form.cleaned_data['operator']
                    new_op.save()
                    expr_node.right_expr = new_op
                    expr_node.save()
            elif form.cleaned_data['expr_type'] == 'reference':
                with transaction.atomic():
                    (ref_id, ref_type, ref_name) = form.cleaned_data['ref_ents'].split(',')
                    (ref_t, ref_attr) = form.cleaned_data['ref_attrs'].split(',')
                    with transaction.atomic():
                        new_ref = RuleUniopExpression()
                        new_ref.is_reference = True;
                        new_ref.reference_id = ref_id
                        new_ref.reference_type = ref_type
                        new_ref.reference_attr = ref_attr
                        new_ref.save()
                        new_biop = RuleBiopExpression()
                        new_biop.is_value = True
                        new_biop.partition = expr_node.partition
                        new_biop.save()
                        expr_node.right_expr = new_biop
                return redirect('partitions:rule_expr_view', partition_id=expr_node.partition.id)
    return render(request, "rule_expr_add.html", context={'form': form, 'partition_id': expr_node.partition.id})

def rule_expr_delete(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    part = expr_node.partition
    expr_node.delete()
    return redirect('partitions:rule_expr_view', partition_id=part.id)
