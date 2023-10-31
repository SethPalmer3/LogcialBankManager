from django.urls import path
from django.contrib import admin
from . import views

app_name = "users"
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('home/', views.user_home, name='home'),
    path('partition/<uuid:partition_id>/', views.user_partition_view, name='partition'),
    path('partitionedit/<uuid:partition_id>/', views.user_partition_edit, name='edit_partition'),
    path('addpartition/', views.add_partition, name='add_partition'),
    path('removepartition/<uuid:partition_id>/', views.remove_partiton, name='remove_partition'),
] 
