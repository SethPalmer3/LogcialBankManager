from django.db import transaction
from django.contrib import messages
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .models import Partition, RuleBiopExpression, RuleUniopExpression
from .forms import RuleExpressionAddForm, RuleExpressionEditForm, SetActionForm

from users.helper_funcs import *
from .partition_globals import *

def _has_parent(expr_node):
    left_query_set = RuleBiopExpression.objects.filter(left_expr=expr_node)
    right_query_set = RuleBiopExpression.objects.filter(right_expr=expr_node)
    return left_query_set.exists() or right_query_set.exists()

@login_required(login_url="/login/")
def rule_expr_view(request: HttpRequest, expr_id):
    """
    """
    expr_node = get_object_or_404(RuleBiopExpression, id=expr_id)
    if expr_node is None or not expr_node.is_root:
        messages.error(request, "Could not load this rule")
        return redirect(reverse('users:home'))
    form = SetActionForm(instance=expr_node or None, user=request.user, data=request.POST or None)
    return render(request, 'rule_expr.html', context={'form': form, 'expr': expr_node, 'part_id': expr_node.partition.id})

def rule_expr_edit(request, expr_id):
    expr_node = get_object_or_404(RuleBiopExpression, id=expr_id)
    form = RuleExpressionEditForm(request.POST or None, instance=expr_node)

    if request.method == "POST" and form.is_valid():
        _process_rule_expr_edit_form(expr_node, form)
        root_node = expr_node.get_root()
        if root_node:
            return redirect('partitions:rule_expr_view', expr_id=root_node.id)
        messages.error(request, "Could not find root node")
        return redirect('partitions:partition', partition_id=expr_node.partition)
    return render(request, 'rule_expr_edit.html', {'form': form, 'partition_id': expr_node.partition.id, 'expr': expr_node})

def _process_rule_expr_edit_form(expr_node, form):
    """
    Processes the rule expression edit form.
    """
    if expr_node.is_root:
        _update_root_expr_node(expr_node, form)

    if IS_VAL_OR_REF in form.cleaned_data:
        _update_val_or_ref_expr(expr_node, form)
    else:
        expr_node.operator = form.cleaned_data[FORM_OPERATOR]
        expr_node.save()

def _update_root_expr_node(expr_node, form):
    """
    Updates the root expression node.
    """
    expr_node.label = form.cleaned_data[FORM_EXPR_NAME]
    expr_node.save()

def _update_val_or_ref_expr(expr_node, form):
    """
    Updates the value or reference expression based on the form data.
    """
    if form.cleaned_data[IS_VAL_OR_REF] == EXPR_TYPE_VALUE:
        _update_value_expr(expr_node, form)
    elif form.cleaned_data[IS_VAL_OR_REF] == EXPR_TYPE_REF:
        _update_reference_expr(expr_node, form)

def _update_value_expr(expr_node, form):
    """
    Updates a value type expression.
    """
    expr_node.value.is_reference = False
    expr_node.value.value_type = form.cleaned_data[FORM_VALUE_TYPE]
    expr_node.value.set_appropiate_value(form.cleaned_data[FORM_VALUE_INPUT])
    expr_node.value.save()

def _update_reference_expr(expr_node, form):
    """
    Updates a reference type expression.
    """
    (ref_id, ref_type, _) = form.cleaned_data[FORM_REF_ENTS].split(',')
    (ref_t, ref_attr) = form.cleaned_data[FORM_REF_ATTRS].split(',')
    if ref_type != ref_t:
        return
    with transaction.atomic():
        expr_node.value.is_reference = True
        expr_node.value.reference_id = ref_id
        expr_node.value.reference_type = ref_type
        expr_node.value.reference_attr = ref_attr
        expr_node.value.save()

@login_required(login_url="/login/")
def rule_expr_unset_l(_, expr_id, direction="left"):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    part_id = expr_node.partition.id
    getattr(expr_node, f"{direction}_expr").delete()
    return redirect('partitions:rule_expr_view', expr_id=expr_node.get_root())

@login_required(login_url="/login/")
def rule_expr_unset_r(request, expr_id):
    return rule_expr_unset_l(request, expr_id, direction="right")

@login_required(login_url="/login/")
def rule_expr_set_l(request, expr_id):
    expr_node = get_object_or_404(RuleBiopExpression, id=expr_id)
    form = RuleExpressionAddForm(user_id=request.user.userprofile.id, partition_id=expr_node.partition.id, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        _process_rule_expr_set_form(expr_node, form, "left")
        root_node = expr_node.get_root()
        if root_node:
            return redirect('partitions:rule_expr_view', expr_id=root_node.id)
        messages.error(request, "Could not find root node")
        return redirect('partitions:partition', partition_id=expr_node.partition)

    return render(request, "rule_expr_add.html", {'form': form, 'partition_id': expr_node.partition.id})

@login_required(login_url="/login/")
def rule_expr_set_r(request, expr_id):
    expr_node = get_object_or_404(RuleBiopExpression, id=expr_id)
    form = RuleExpressionAddForm(user_id=request.user.userprofile.id, partition_id=expr_node.partition.id, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        _process_rule_expr_set_form(expr_node, form, "right")
        root_node = expr_node.get_root()
        if root_node:
            return redirect('partitions:rule_expr_view', expr_id=root_node.id)
        messages.error(request, "Could not find root node")
        return redirect('partitions:partition', partition_id=expr_node.partition)

    return render(request, "rule_expr_add.html", {'form': form, 'partition_id': expr_node.partition.id})

def _process_rule_expr_set_form(expr_node, form, direction):
    """
    Processes the rule expression set left/right form.
    """
    expr_type = form.cleaned_data[FORM_EXPR_TYPE]
    
    if expr_type == EXPR_TYPE_VALUE:
        _process_val_expr(expr_node, form, direction)
    elif expr_type == EXPR_TYPE_OP:
        _process_op_expr(expr_node, form, direction)
    elif expr_type == EXPR_TYPE_REF:
        _process_ref_expr(expr_node, form, direction)

def _process_val_expr(expr_node, form, direction):
    """
    Processes a value type expression.
    """
    # Code to process value type expression
    new_value = RuleUniopExpression()
    new_value.value_type = form.cleaned_data[FORM_VALUE_TYPE]
    new_value.set_appropiate_value(form.cleaned_data[FORM_VALUE_INPUT])
    new_value.save()
    new_expr = RuleBiopExpression()
    new_expr.partition = expr_node.partition
    new_expr.value = new_value
    new_expr.is_value = True
    new_expr.save()
    setattr(expr_node, f"{direction}_expr", new_expr)
    expr_node.save()

def _process_op_expr(expr_node, form, direction):
    """
    Processes an operator type expression.
    """
    # Code to process operator type expression
    new_op = RuleBiopExpression()
    new_op.partition = expr_node.partition
    new_op.operator = form.cleaned_data[FORM_OPERATOR]
    new_op.save()
    setattr(expr_node, f"{direction}_expr", new_op)
    expr_node.save()

def _process_ref_expr(expr_node, form, direction):
    """
    Processes a reference type expression.
    """
    # Code to process reference type expression
    (ref_id, ref_type, _) = form.cleaned_data[FORM_REF_ENTS].split(',')
    (_, ref_attr) = form.cleaned_data[FORM_REF_ATTRS].split(',')
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
        setattr(expr_node, f"{direction}_expr", new_biop)
        expr_node.save()

@login_required(login_url="/login/")
def rule_expr_delete(_, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    part = expr_node.partition
    expr_node.delete()
    return redirect('partitions:partition', partition_id=part.id)

def rule_expr_parent(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    part = expr_node.partition
    form = RuleExpressionAddForm(is_parent=True, partition_id=part.id, user_id=request.user.userprofile.id, data=request.POST or None)
    if not _has_parent(expr_node):
        if request.method == "POST":
            if form.is_valid():
                with transaction.atomic():
                    parent_node = RuleBiopExpression()
                    parent_node.operator = form.cleaned_data[FORM_OPERATOR]
                    if expr_node.is_root:
                        parent_node.is_root = True
                        expr_node.is_root = False
                    print(form.cleaned_data[FORM_CHILD_DIR])
                    setattr(parent_node, f"{form.cleaned_data[FORM_CHILD_DIR]}_expr", expr_node)
                    print(getattr(parent_node, f"{form.cleaned_data[FORM_CHILD_DIR]}_expr"))
                    parent_node.save()
                return redirect('partitions:rule_expr_view', expr_id=expr_node.get_root().id)
        return render(request, 'rule_expr_parent.html', context={'form': form, 'partition_id': part.id})
    messages.error(request, "This node already has a parent")
    return redirect('partitions:rule_expr_view', expr_id=expr_node.get_root().id)

def rule_expr_create(request, partition_id):
    part = Partition.objects.get(id=partition_id)
    form = RuleExpressionAddForm(is_parent=True, partition_id=partition_id, user_id=request.user.userprofile.id, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            with transaction.atomic():
                new_root = RuleBiopExpression()
                new_root.partition = part
                new_root.is_root = True
                new_root.operator = form.cleaned_data[FORM_OPERATOR]
                new_root.label = form.cleaned_data[FORM_EXPR_NAME]
                new_root.save()
            return redirect('partitions:rule_expr_view', expr_id=new_root.id)
    return render(request, 'rule_expr_parent.html', context={'form': form, 'partition_id': part.id, 'is_create': True})

def rule_expr_set_action(request, expr_id):
    expr_node = RuleBiopExpression.objects.get(id=expr_id)
    if not expr_node.is_root:
        return redirect('partitions:rule_expr_view', expr_id=expr_node.get_root().id)
    form = SetActionForm(instance=expr_node, user=request.user, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            expr_node.action = form.cleaned_data[FORM_ACTION]
            if expr_node.action == ACTION_TRANSFER:
                (to_id, _, _) = rule_entity_destringify(form.cleaned_data[ACTION_TRANSFER_TO])
                if expr_node.partition:
                    expr_node.partition.frozen = False
                if to_id != "":
                    to_partition = Partition.objects.get(id=to_id) or None
                else:
                    to_partition = None
                expr_node.transfer_amount = form.cleaned_data[ACTION_TRANSFER_AMOUNT]
                expr_node.transfer_to = to_partition
            expr_node.preformed_action = False
            expr_node.save()
            return redirect('partitions:rule_expr_view', expr_id=expr_node.get_root().id)
    return render(request, 'rule_set_action.html', context={'form': form, 'partition_id': expr_node.partition.id})
