from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Budget(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    


class Income(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='income', null=True)

    def __str__(self):
        return self.name
    
    def category_name(self):
        return self.category.name


class Category(models.Model):
    CATEGORY_CHOICES = (
        ('FOOD', 'Food'),
        ('TRANSPORT', 'Transportation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('BILLS', 'Bills'),
        ('SHOPPING', 'Shopping'),
        ('HOUSING', 'Housing'),
        ("MISCELLANEOUS", "Miscellaneous"),
    )
     
    name = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    
    def __str__(self):
        return self.name
    
    


class Expense(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expense', null=True)

    def __str__(self):
        return self.name
    
    def category_name(self):
        return self.category.name
    
    def __str__(self):
        return self.name

    def expense_total(self):
        return self.amount
    
    def expense_by_category(self):
        return self.category.name
    
    def expense_by_month(self):
        return self.date_incurred.strftime('%B')
    
    def expense_percent_of_budget(self):
        budget_total = self.budget.total_budget()
        expense_total = self.expense_total()
        return (expense_total / budget_total) * 100



class Report(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    total_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def generate_report(self):
        incomes = Income.objects.filter(budget=self.budget, date_received__range=[self.start_date, self.end_date])
        expenses = Expense.objects.filter(budget=self.budget, date_incurred__range=[self.start_date, self.end_date])

        self.total_income = incomes.aggregate(Sum('amount'))['amount__sum']
        self.total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
        self.remaining_balance = self.total_income - self.total_expenses
        self.save()

'''
class SavingsGoal(models.Model):
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_progress = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='savings_goals/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    deadline = models.DateField()
    achieved = models.BooleanField(default=False)
    
    def add_savings(self, amount):
        self.current_savings += amount
        if self.current_savings >= self.goal_amount:
            self.achieved = True
        self.save()
        
    def __str__(self):
        return self.goal_name
'''