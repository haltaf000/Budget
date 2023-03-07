from django import forms
from .models import Budget, Income, Expense, Category, User
from django.contrib.auth.forms import UserCreationForm

class ReportForm(forms.Form):
    start_date = forms.DateField(label='Start Date')
    end_date = forms.DateField(label='End Date')

class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-field--input'}),
            'name': forms.TextInput(attrs={'class':'form-field--input'}),
            'email':forms.EmailInput(attrs={'class':'form-field--input'})
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'start_date', 'end_date']

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['name', 'amount', 'date_received', 'budget']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date_incurred', 'budget', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
