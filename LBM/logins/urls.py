
from django.urls import path
from django.contrib import admin
from . import views

app_name = "logins"
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/', admin.site.urls),
    path('signup/', views.user_signup, name='signup'),
    path('get_bank/', views.get_bank, name='get_bank'),
    path('transfer/', views.transfer, name='transfer'),
] 
