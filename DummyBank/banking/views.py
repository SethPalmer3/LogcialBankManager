from decimal import Decimal
from django.db import transaction
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework.views import APIView

from .models import BankAccount

from .serializers import  BankAccoutSerializer, UserSerializer


from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

class TransferBalanceView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = BankAccount.objects.all()
    serializer_class = BankAccoutSerializer
    def post(self, request):
        if not request.user.is_authenticated:
            print("Unauthorized")
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        from_account_id = request.POST.get('from_account_id')
        to_account_id = request.POST.get('to_account_id')
        print(f"{from_account_id} - {to_account_id}")
        amount = Decimal(request.POST.get('amount'))

        # from_account = get_object_or_404(BankAccount, id=from_account_id)
        # to_account = get_object_or_404(BankAccount, id=to_account_id)
        try:
            from_account = BankAccount.objects.get(id=from_account_id)
        except BankAccount.DoesNotExist as e:
            print(f"From Account Error: {e}")
            return JsonResponse({'error': f'From account not found: {from_account_id}'}, status=404)

        try:
            to_account = BankAccount.objects.get(id=to_account_id)
        except BankAccount.DoesNotExist as e:
            print(f"To Account Error: {e}")
            return JsonResponse({'error': f'To account not found: {to_account_id}'}, status=404)

        if request.user != from_account.holder.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        if from_account.balance < amount:
            return JsonResponse({'error': 'Insufficient funds'}, status=403)

        with transaction.atomic():
            from_account.balance -= Decimal(amount)
            to_account.balance += Decimal(amount)
            from_account.save()
            to_account.save()
        return JsonResponse({
            'from_account_new_balance': str(from_account.balance),
            'to_account_new_balance': str(to_account.balance)
        })

class UserList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer 

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserSerializer

    def get_object(self):
        if not self.request.user.is_authenticated:
            return None

        obj = get_object_or_404(User, pk=self.request.user.pk)

        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return User.objects.all()

def login_page(request):
    return render(request, 'login.html')
