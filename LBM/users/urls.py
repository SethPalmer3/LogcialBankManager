from django.urls import path
from django.contrib import admin
from . import views

app_name = "users"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='login')
]
