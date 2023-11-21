from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID
from django.apps import apps

EXPR_TYPE_VALUE = 'value'
EXPR_TYPE_REF = 'reference'
EXPR_TYPE_OP = 'operation'
REF_TYPE_PART = 'Partition'
REF_TYPE_USER = 'User'
FORM_REF_ENTS = 'ref_ents'
FORM_REF_ATTRS = 'ref_attrs'
FORM_VALUE_INPUT = 'value_input'
FORM_VALUE_TYPE = 'value_type'
FORM_OPERATOR = 'operator'
FORM_EXPR_TYPE = 'expr_type'
FORM_CHILD_LEFT = 'left'
FORM_CHILD_RIGHT = 'right'
FORM_CHILD_DIR = 'l_or_r'
FORM_EXPR_NAME = 'expr_name'
IS_VAL_OR_REF = 'value_or_ref'
ACTION_FREEZE = 'freeze'
ACTION_TRANSFER = 'transfer'
ACTION_TRANSFER_FROM = 'transfer_from'
ACTION_TRANSFER_TO = 'transfer_to'
ACTION_TRANSFER_AMOUNT = 'transfer_amount'
FORM_ACTION = 'action'

ACTIONS_CHOICES = [
    (ACTION_TRANSFER, "Transfer"),
    (ACTION_FREEZE, "Freeze"),
]

BIOPS_CHOICES = [
    ('eq', "Equals"),
    ('lt', "Less Than"),
    ('gt', "Greater Than"),
    ('lte', "Less Than or Equal"),
    ('gte', "Greater Than or Equal"),
    ('add', "Add"),
    ('sub', "Subtract"),
    ('mul', "Multiply"),
    ('div', "Divide"),
]
BIOPS_CHOICE_FUNCS = {
    'eq': lambda a, b: a == b, 
    'lt': lambda a, b: a < b, 
    'gt': lambda a, b: a > b, 
    'lte': lambda a, b: a <= b, 
    'gte': lambda a, b: a >= b, 
    'add': lambda a, b: a + b, 
    'sub': lambda a, b: a - b, 
    'mul': lambda a, b: a * b, 
    'div': lambda a, b: a / b, 
}
UNIOP_VALUE_TYPE_CHOICES = [
    ('float', 'Float'),
    ('decimal', 'Decimal'),
    ('str', 'String'),
    ('string', 'String'),
    ('int', 'Integer'),
]
UNIOP_SELF_ATTRIBUTE_CONVERT = {
    'float': "float_value",
    'decimal': "decimal_value",
    'str': "string_value",
    'string': "string_value",
    'int': "int_value",
}
EXPR_REF_TYPE_CHOICES = [
    ('Partition', 'Partition'),
    ('User', 'User'),
]
EXPR_REF_TYPE_APP_CONVERT = {
    REF_TYPE_USER: 'users',
    REF_TYPE_PART: 'partitions',
}
EXPR_TYPE_CHOICES = [
    ('value', 'Value'),
    ('reference', 'External Reference'),
    ('operation', 'Operation'),
]
EXPR_ATTR_CHOICES = {
    REF_TYPE_PART: [
        ('Partition,init_amount', 'Inital Amount'),
        ('Partition,current_amount', 'Current Amount'),
    ],
    REF_TYPE_USER: [
        ('User,total_amount', 'Total Amount'),
    ]
}
PARENT_EXPR_DIR_CHOICES = [
    (FORM_CHILD_LEFT, "Put Left Hand Side"),
    (FORM_CHILD_RIGHT, "Put Right Hand Side"),
]

def rule_entity_stringify(ent_id, ent_type, ent_name, is_current=False):
    value = f"{ent_id},{ent_type},{ent_name}"
    if is_current:
        disp = f"[{ent_type}]: {ent_name}(current)"
    else:
        disp = f"[{ent_type}]: {ent_name}"

    return (value,disp)

def rule_entity_destringify(s: str) -> tuple[str, str, str]:
    """
    Splits a input select string into entity id, entity type, entity name in that order.
    """
    # (value,_) = s
    str_split = s.split(',')
    if len(str_split) == 3:
        (ent_id, ent_type, ent_name) = str_split
        return (ent_id, ent_type, ent_name)
    else:
        return ('', '', '')


def entities_list(user_id, partition_id):
    from .models import Partition
    from users.models import UserProfile
    ret = []
    userprof = UserProfile.objects.get(id=user_id)
    user = userprof.user
    for p in Partition.objects.filter(owner=user): # Get all partitons
        ret.append(rule_entity_stringify(p.id,REF_TYPE_PART, p.label, p.id==partition_id))
    ret.append(rule_entity_stringify(userprof.pk, REF_TYPE_USER, user.username))
    return ret

def operations_list(type_s):
    ret = []
    if type_s == "float" or type_s == "decimal" or type_s == "int":
        for (value, disp) in BIOPS_CHOICES:
            ret.append((value, disp))
    return ret


def entity_attr_list(ent_type=None):
    ret = []
    if ent_type == REF_TYPE_PART or ent_type is None:
        for val_dis in EXPR_ATTR_CHOICES[REF_TYPE_PART]:
            ret.append(val_dis)
    if ent_type == REF_TYPE_USER or ent_type is None:
        for val_dis in EXPR_ATTR_CHOICES[REF_TYPE_USER]:
            ret.append(val_dis)

    return ret

def get_type_string(obj_id: UUID, obj_type: str):
    app_conv = EXPR_REF_TYPE_APP_CONVERT[obj_type]
    if obj_type == REF_TYPE_USER:
        obj_type = "UserProfile"
    select_model = apps.get_model(app_conv, obj_type)
    return select_model.objects.get(id=obj_id)

D = TypeVar("D")
O = TypeVar("O")
def execute_or_default(f: Callable[..., O], d: D, *args, **kwargs) -> O | D:
    try:
        return f(*args, **kwargs)
    except:
        return d

def set_changed_field(obj: object, field: str, value: Any) -> list[str]:
    """
    Set attribute of object if value is different.
    Returns:
        Whether the attribute is the same value as given value
    """
    try:
        old_value = getattr(obj, field)
        if old_value == value:
            return []
        setattr(obj, field, value)
        return [field]
    except AttributeError:
        return []
