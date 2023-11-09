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
IS_VAL_OR_REF = 'value_or_ref'

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


def rule_entity_stringify(ent_id, ent_type, ent_name, is_current=False):
    value = f"{ent_id},{ent_type},{ent_name}"
    if is_current:
        disp = f"[{ent_type}]: {ent_name}(current)"
    else:
        disp = f"[{ent_type}]: {ent_name}"

    return (value,disp)

def rule_entity_destringify(string):
    (value,_) = string
    (ent_id, ent_type, ent_name) = value.split(',')
    return (ent_id, ent_type, ent_name)


def entities_list(user_id, partition_id):
    from .models import Partition
    from users.models import UserProfile
    ret = []
    userprof = UserProfile.objects.get(id=user_id)
    user = userprof.user
    for p in Partition.objects.filter(owner=user): # Get all partitons
        ret.append(rule_entity_stringify(p.id, "Partition", p.label, p.id==partition_id))
    ret.append(rule_entity_stringify(userprof.pk, "User", user.username))
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