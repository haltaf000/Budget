from django.shortcuts import render, redirect, get_object_or_404
from .forms import BudgetForm, IncomeForm, ExpenseForm, CategoryForm, CustomUserCreateForm, ReportForm
from django.contrib.auth.decorators import login_required
from .models import Budget, Income, Expense, Category, Report
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse


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
            # Get the selected budget
            budget = form.cleaned_data.get('budget')
            if budget:
                category = form.save(commit=False)
                category.budget = budget
                category.save()
                return redirect('category_list')
            else:
                # set the budget field to a default value
                category = form.save(commit=False)
                category.budget = Budget.objects.filter(user=request.user).first()
                category.save()
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
    incomes = Income.objects.filter(budget=budget, date_received__gte=budget.start_date, date_received__lte=budget.end_date)
    expenses = Expense.objects.filter(budget=budget, date_incurred__gte=budget.start_date, date_incurred__lte=budget.end_date)
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_savings = total_income - total_expenses 
    context = {
        'budget': budget,
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_savings': total_savings
    }
    return render(request, 'budget_detail.html', context)

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
    user = request.user
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            budget = Budget.objects.filter(user=user).first()
            incomes = Income.objects.filter(budget=budget, date_received__range=[start_date, end_date])
            expenses = Expense.objects.filter(budget=budget, date_incurred__range=[start_date, end_date])
            total_income = incomes.aggregate(Sum('amount'))['amount__sum']
            total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
            remaining_balance = total_income - total_expenses
            report = Report.objects.create(user=user, budget=budget, start_date=start_date, end_date=end_date, total_income=total_income, total_expenses=total_expenses, remaining_balance=remaining_balance)
            context = {
                'incomes': incomes,
                'expenses': expenses,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'remaining_balance': remaining_balance,
            }
            return render(request, 'generate_report.html', context)
    else:
        form = ReportForm()
    return render(request, 'generate_report.html', {'form': form})

def report_detail(request, pk):
    report = Report.objects.get(pk=pk)
    context = {
        'report': report,
    }
    return render(request, 'report_detail.html', context)

def create_report(request):
    # Get information from generate_report form
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            selected_budget = form.cleaned_data.get('budget')
            if selected_budget:
                # Get all income and expenses for the selected budget within the specified date range
                incomes = Income.objects.filter(budget=selected_budget, date_received__range=[start_date, end_date])
                expenses = Expense.objects.filter(budget=selected_budget, date__range=[start_date, end_date])
            else:
                # Get all income and expenses for all budgets within the specified date range
                incomes = Income.objects.filter(date_received__range=[start_date, end_date])
                expenses = Expense.objects.filter(date__range=[start_date, end_date])

            if len(incomes) > 0:
                total_income = incomes.aggregate(Sum('amount'))['amount__sum']
            else:
                total_income = 0

            if len(expenses) > 0:
                total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
            else:
                total_expenses = 0

            budget_balance = total_income - total_expenses

            # Create the report
            report_name = form.cleaned_data.get('name')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(report_name)
            doc = SimpleDocTemplate(response, pagesize=landscape(letter))
            data = [['Incomes', 'Expenses', 'Balance'],
                    [total_income, total_expenses, budget_balance]]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            doc.build([table])
            # Save the report to the database
            report = Report(name=report_name, pdf=response.getvalue())
            report.save()

            # Redirect the user to the report_list view
            return redirect('report_list')
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
    reports = Report.objects.filter(user=request.user)
    context = {'reports': reports}
    return render(request, 'report_list.html', context)



@login_required(login_url='/login')
def download_report(request, report_id):
    report = Report.objects.get(id=report_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    data = [['Incomes', 'Expenses', 'Balance'],
            [report.total_income, report.total_expenses, report.remaining_balance]]
    table = Table(data)
    doc.build([table])
    return response



@login_required(login_url='/login')
def view_report(request, pk):
    report = Report.objects.get(pk=pk, user=request.user)
    budget = report.budget
    incomes = Income.objects.filter(budget=budget, date_received__gte=budget.start_date, date_received__lte=budget.end_date)
    expenses = Expense.objects.filter(budget=budget, date_incurred__gte=budget.start_date, date_incurred__lte=budget.end_date)
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    budget_balance = (total_income - total_expenses) or 0
    context = {
        'report': report,
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'budget_balance': budget_balance
    }
    return render(request, 'view_report.html', context)




@login_required(login_url='/login')
def delete_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    report.delete()
    return redirect('report_list')


@login_required(login_url='/login')
def forecast_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    forecast_income = budget.income * 1.1
    forecast_expenses = budget.expenses * 1.2
    forecast_balance = forecast_income - forecast_expenses
    return render(request, 'forecast.html', {'budget': budget, 'forecast_income': forecast_income, 'forecast_expenses': forecast_expenses, 'forecast_balance': forecast_balance})