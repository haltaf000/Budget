from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum


class User(AbstractUser):
    INCOME_CHOICES = (
        (15000, '$15,000 - $24,999'),
        (25000, '$25,000 - $44,999'),
        (30000, '$30,000 - $39,999'),
        (40000, '$40,000 - $49,999'),
        (50000, '$50,000 - $59,999'),
        (60000, '$60,000 - $69,999'),
        (70000, '$70,000 - $79,999'),
        (80000, '$80,000 - $89,999'),
        (90000, '$90,000 - $99,999'),
        (100000, '$100,000 - $124,999'),
        (125000, '$125,000 - $149,999'),
        (150000, '$150,000 - $174,999'),
        (175000, '$175,000 - $199,999'),
        (200000, '$200,000 - $224,999'),
        (225000, '$225,000 - $249,999'),
        (250000, '$250,000 or more'),
    )

    name = models.CharField(max_length=200, null=True)
    income = models.IntegerField(choices=INCOME_CHOICES, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Budget(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget')
    is_monthly = models.BooleanField(default=False)

    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="Something")
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
        
class SavingGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_range = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_range', to_field='income')
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
    
    
class Leaderboard(models.Model):
    saving_goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, related_name='leaderboard')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    current_savings = models.DecimalField(max_digits=10, decimal_places=2)

class Reward(models.Model):
    saving_goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, related_name='rewards')
    name = models.CharField(max_length=255)
    achievement_amount = models.DecimalField(max_digits=10, decimal_places=2)
    achieved = models.BooleanField(default=False)

