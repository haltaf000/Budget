from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum

class User(AbstractUser):
    about_me = models.TextField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    total_budget_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.budget_name
    
class Category(models.Model):
    category_name = models.CharField(max_length=255)


    def __str__(self):
        return self.category_name
    
class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    expense_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return self.expense_name
    
class SavingGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    end_date = models.DateField()

    
    def __str__(self):
        return self.goal_name
    
    
class Saving(models.Model):
    saving_goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return self.amount_saved
    
class BudgetReport(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    saving_goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, blank=True, null=True)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2)
    date_range_start = models.DateField()
    date_range_end = models.DateField()

    def __str__(self):
        return f"{self.budget.budget_name} Report"
    
class RecurringExpense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    expense_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20) # monthly, quarterly, etc.
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return self.expense_name


class Income(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    income_source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
    def __str__(self):
        return self.income_source


class BudgetHistory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    saving_goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, blank=True, null=True)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.budget.budget_name} History"


class Reminder(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    reminder_title = models.CharField(max_length=255)
    reminder_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.reminder_title
