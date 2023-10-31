from django.urls import path
from . import views

app_name = "partitions"
urlpatterns = [
    path('partition/<uuid:partition_id>/', views.user_partition_view, name='partition'),
    path('partitionedit/<uuid:partition_id>/', views.user_partition_edit, name='edit_partition'),
    path('addpartition/', views.add_partition, name='add_partition'),
    path('removepartition/<uuid:partition_id>/', views.remove_partiton, name='remove_partition'),
] 
