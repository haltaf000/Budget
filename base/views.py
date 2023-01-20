from django.shortcuts import render, redirect, get_object_or_404
from .forms import BudgetForm, IncomeForm, ExpenseForm, CategoryForm, CustomUserCreateForm, ReportForm
from django.contrib.auth.decorators import login_required
from .models import Budget, Income, Expense, Category, Report
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse



def home(request):
    total_income = Income.objects.all().aggregate(Sum('amount'))
    total_expense = Expense.objects.all().aggregate(Sum('amount'))
    if total_income and total_expense:
        budget_balance = (total_income['amount__sum'] or 0) - (total_expense['amount__sum'] or 0)
    else:
        budget_balance = None
        
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'budget_balance': budget_balance,
    }

    return render(request, 'home.html', context)


from datetime import datetime, timedelta




def login_page(request):
    page = 'login'
    
    if request.method == 'POST':
        user = authenticate(email=request.POST['email'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            messages.info(request, 'You have successfully logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Email or Password is incorrect')
            return redirect('login')
    
    context = {'page':page}
    return render(request, 'login_register.html', context)

def register_page(request):
    form = CustomUserCreateForm()
    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request, user)
            messages.success(request, 'User account was created!')
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during registration')
    
    
    page = 'register'
    context = {'page':page, 'form':form}
    return render(request, 'login_register.html', context)

def logout_user(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('home')



@login_required(login_url='/login')
def create_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm()
    return render(request, 'create_income.html', {'form': form})

@login_required(login_url='/login')
def income_list(request):
    incomes = Income.objects.all()
    return render(request, 'income_list.html', {'incomes': incomes})

@login_required(login_url='/login')
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'edit_income.html', {'form': form})

@login_required(login_url='/login')
def delete_income(request, pk):
    income = Income.objects.get(pk=pk)
    income.delete()
    return redirect('income_list')


@login_required(login_url='/login')
def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'create_expense.html', {'form': form})

@login_required(login_url='/login')
def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'expense_list.html', {'expenses': expenses})

@login_required(login_url='/login')
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'edit_expense.html', {'form': form})

@login_required(login_url='/login')
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('expense_list')
    

@login_required(login_url='/login')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.budget = request.user.budget
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'create_category.html', {'form': form})


@login_required(login_url='/login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

@login_required(login_url='/login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})

@login_required(login_url='/login')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('category_list')
    



@login_required(login_url='/login')
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budget_list.html', {'budgets': budgets})

@login_required(login_url='/login')
def budget_detail(request, pk):
    budget = Budget.objects.get(pk=pk, user=request.user)
    incomes = Income.objects.filter(budget=budget)
    expenses = Expense.objects.filter(budget=budget)
    return render(request, 'budget_detail.html', {'budget': budget, 'incomes': incomes, 'expenses': expenses})

@login_required(login_url='/login')
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget_detail', pk=budget.pk)
    else:
        form = BudgetForm()
    return render(request, 'create_budget.html', {'form': form})

@login_required(login_url='/login')
def edit_budget(request, pk):
    budget = Budget.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('budget_detail', pk=budget.pk)
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'edit_budget.html', {'form': form})

@login_required(login_url='/login')
def delete_budget(request, pk):
    budget = Budget.objects.get(pk=pk, user=request.user)
    budget.delete()
    return redirect('budget_list')


@login_required(login_url='/login')
def generate_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            user = request.user
            budget = user.budget

            # Get all income and expenses within the specified date range
            incomes = Income.objects.filter(budget=budget, date_received__range=[start_date, end_date])
            expenses = Expense.objects.filter(budget=budget, date_incurred__range=[start_date, end_date])

            # Calculate total income, expenses, and budget balance
            total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            budget_balance = (total_income - total_expenses) or 0

            # Create a new report object and call the generate_report function
            report = Report(start_date=start_date, end_date=end_date, budget=budget)
            report.generate_report()
            report.save()

            context = {
                'start_date': start_date,
                'end_date': end_date,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'budget_balance': budget_balance,
                'incomes': incomes,
                'expenses': expenses
            }
            
            # Redirect to the view_report page with the report_id as an argument
            return redirect(reverse('view_report', kwargs={'report_id': report.pk}))
    else:
        form = ReportForm()
        context = {'form': form}
        return render(request, 'generate_report.html', context)




@login_required(login_url='/login')
def report_form(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            return redirect('report_list', report_id=report.pk)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'form': form})



@login_required(login_url='/login')
def report_list(request):
    user = request.user
    budget = user.budget

    # Get all income and expenses within the specified date range
    incomes = Income.objects.filter(budget=budget)
    expenses = Expense.objects.filter(budget=budget)

    if len(incomes) > 0:
        total_income = incomes.aggregate(Sum('amount'))['amount__sum']
    else:
        total_income = 0
    
    if len(expenses) > 0:
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
    else:
        total_expenses = 0
    budget_balance = total_income - total_expenses
    reports = Report.objects.filter(budget=budget)
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'budget_balance': budget_balance,
        'incomes': incomes,
        'expenses': expenses,
        'reports': reports
    }
    return render(request, 'report_list.html', context)





@login_required(login_url='/login')
def view_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    budget = report.budget
    incomes = Income.objects.filter(budget=budget)
    expenses = Expense.objects.filter(budget=budget)
    total_income = incomes.aggregate(Sum('amount'))['amount__sum']
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
    budget_balance = total_income - total_expenses
    context = {
        'report': report,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'budget_balance': budget_balance,
        'incomes': incomes,
        'expenses': expenses
    }
    return render(request, 'view_report.html', context)



@login_required(login_url='/login')
def delete_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    report.delete()
    return redirect('report_list')



def forecast_budget(request):
    user = request.user
    budget = user.budget

    if request.method == 'POST':
        forecast_period = request.POST.get('forecast_period')

        if forecast_period == 'month':
            period = 30
        elif forecast_period == 'quarter':
            period = 90

        last_month_start = datetime.now() - timedelta(days=period)
        incomes = Income.objects.filter(budget=budget, date_received__gte=last_month_start)
        expenses = Expense.objects.filter(budget=budget, date_incurred__gte=last_month_start)

        # Calculate total income, expenses, and budget balance for last month
        total_income = incomes.aggregate(Sum('amount'))['amount__sum']
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
        budget_balance = total_income - total_expenses

        # Use the average income and expense amounts from the last month to forecast budget for the next month
        forecast_income = total_income / period * (period+1)
        forecast_expenses = total_expenses / period * (period+1)
        forecast_budget_balance = forecast_income - forecast_expenses
        
        context = {
            'forecast_income': forecast_income,
            'forecast_expenses': forecast_expenses,
            'forecast_budget_balance': forecast_budget_balance,
            'budget_balance': budget_balance,
            
        }

        return render(request, 'forecast_budget.html', context)
    else:
        return render(request, 'forecast_budget.html')
