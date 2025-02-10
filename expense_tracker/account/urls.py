
from django.urls import path
from . import views

urlpatterns = [
    path('users/login/', views.index_view, name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
]

