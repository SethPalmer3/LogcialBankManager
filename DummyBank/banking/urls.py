from django.urls import path

from .views import AccountHolderDetail

urlpatterns = [
    path('account-holder/<int:pk>/', AccountHolderDetail.as_view(), name='account-holder')
]
