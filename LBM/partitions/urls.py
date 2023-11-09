from django.urls import path
from . import views

app_name = "partitions"
urlpatterns = [
    path('partition/<uuid:partition_id>/', views.user_partition_view, name='partition'),
    path('partitionedit/<uuid:partition_id>/', views.user_partition_edit, name='edit_partition'),
    path('addpartition/', views.add_partition, name='add_partition'),
    path('removepartition/<uuid:partition_id>/', views.remove_partiton, name='remove_partition'),
    path('rule-expr-view/<uuid:partition_id>/', views.rule_expr_view, name='rule_expr_view'),
    path('rule-expr-edit/<uuid:expr_id>/', views.rule_expr_edit, name='rule_expr_edit'),
    path('rule-expr-delete/<uuid:expr_id>/', views.rule_expr_delete, name='rule_expr_delete'),
    path('rule-expr-unset-l/<uuid:expr_id>/', views.rule_expr_unset_l, name='rule_expr_unset_l'),
    path('rule-expr-unset-r/<uuid:expr_id>/', views.rule_expr_unset_r, name='rule_expr_unset_r'),
    path('rule-expr-set-l/<uuid:expr_id>/', views.rule_expr_set_l, name='rule_expr_set_l'),
    path('rule-expr-set-r/<uuid:expr_id>/', views.rule_expr_set_r, name='rule_expr_set_r'),
    path('rule-expr-parent/<uuid:expr_id>/', views.rule_expr_parent, name='rule_expr_parent'),
    path('rule-expr-create/<uuid:partition_id>/', views.rule_expr_create, name='rule_expr_create'),
] 
