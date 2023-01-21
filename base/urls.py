from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('budgets/', views.budget_list, name='budget_list'),
    path('budget/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budget/new/', views.create_budget, name='create_budget'),
    path('budget/<int:pk>/edit/', views.edit_budget, name='edit_budget'),
    path('budget/<int:pk>/delete/', views.delete_budget, name='delete_budget'),
    
    path('income/new/', views.create_income, name='create_income'),
    path('incomes/', views.income_list, name='income_list'),
    path('income/<int:pk>/edit/', views.edit_income, name='edit_income'),
    path('income/<int:pk>/delete/', views.delete_income, name='delete_income'),
    
    path('expense/new/', views.create_expense, name='create_expense'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expense/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    
    path('category/new/', views.create_category, name='create_category'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'), 
     
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),
    
    path('generate-report/', views.generate_report, name='generate_report'),
    path('report-form/', views.report_form, name='report_form'),
    path('create-report/', views.create_report, name='create_report'),
    path('report-list/', views.report_list, name='report_list'),
    path('view/<int:report_id>/', views.view_report, name='view_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('download-report/<int:report_id>/', views.download_report, name='download_report'),
    path('report-detail/<int:report_id>/', views.report_detail, name='report_detail'),


    path('forecast-budget/<int:pk>/', views.forecast_budget, name='forecast_budget'),



]