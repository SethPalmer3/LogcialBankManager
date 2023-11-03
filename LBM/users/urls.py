from django.urls import path
from django.contrib import admin
from . import views

app_name = "users"
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('home/', views.user_home, name='home'),
    path('clear/', views.clear_token, name='clear'),
] 
