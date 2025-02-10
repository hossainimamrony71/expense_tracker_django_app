# urls.py

from django.urls import path
from . import views
from .views import (
    ExpenseCategoryListView,
    ExpenseCategoryCreateView,
    ExpenseCategoryUpdateView,
    ExpenseCategoryAjaxDeleteView,
    ExpenseCreateView, 
    ExpenseUpdateView,
    ExpenseListView,
    ExpenseDeleteView,
    
    #admin dashbord creating
    TedS2lCategoryList,
    allocated_money,
    TedS2lExpenseListView,
)
# urls.py
from django.urls import path
from . import views






urlpatterns = [
    
    
    #admin dashbord
    path('categorieslist/<str:user_type>/', TedS2lCategoryList.as_view(), name='admin_category_list'),
    path('allocated-money/', allocated_money, name='allocated_money'),
    path('expenseslist/<str:user_type>/', TedS2lExpenseListView.as_view(), name='ted_s2l_expense_list'),
    


    path('categories/', ExpenseCategoryListView.as_view(), name='category-list'),
    path('categories/add/', ExpenseCategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>/edit/', ExpenseCategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', ExpenseCategoryAjaxDeleteView.as_view(), name='category-delete'),
    
    
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expenses/create/', ExpenseCreateView.as_view(), name='expense-create'),
    path('expenses/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense-update'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense-delete'),


    path('loan-request/', views.create_loan_request, name='loan_ted_s2l'),
    path('loans/', views.loan_admin, name='loan_admin'),
    path('loans/approve/<int:pk>/', views.approve_loan_request, name='approve_loan'),
    path('loans/decline/<int:pk>/', views.decline_loan_request, name='decline_loan'),

]
