from django.db.models import QuerySet
from .models import Partition, UserProfile

def check_partitions( partitons: QuerySet, user=None, total_amount = 0.0):
    """
    checks if the query set of partitons amounts are allowed. if user is non 

    partitons: The query set of partitions
    user: the associated user profile(default=None)
    total_amount: The amount to check against(if user is None)

    Return: the difference from the allowed total and the partition total
    """
    if total_amount < 0.0:
        return 0.0
    total = 0
    for p in partitons:
        total += p.current_amount

    if user is None:
        return total_amount - total
    userprof = UserProfile.objects.filter(user=user).first()
    try:
        return userprof.total_amount - total
    except:
        return 0.0

def create_partition(owner, label="Undefined", amount = 0.0):
    """
    Creates and returns a new partition

    owner: User model associated with the new partition
    label: Label for new partition(default="Undefined")
    amount: Starting amount(default=0.0)

    Return: the new partition
    """
    first_parition = Partition.objects.create()
    first_parition.owner.add(owner)
    first_parition.label = label
    first_parition.current_amount = amount
    first_parition.save()
    return first_parition

def get_UserProfile(user):
    """
    Returns the associated user profile model
    """
    return UserProfile.objects.filter(user=user).first()
