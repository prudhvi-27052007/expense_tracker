from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime



def signup_page(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")

        if password != confirmpassword:
            messages.error(request, "Passwords do not match")
            return redirect('/signup/')

        # check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect('/signup/')

        # create user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        return redirect('/login/')

    return render(request, 'signup.html')



def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # ADD THIS BLOCK HERE
        if not User.objects.filter(username=username).exists():
            messages.error(request, "User not registered")
            return redirect("/signup/")

        # authenticate user
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid password")
            return redirect("/login/")

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "login.html")




@login_required(login_url="/login/")
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
     # TOTAL EXPENSE AMOUNT
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # TOTAL CATEGORIES
    total_categories = expenses.values('category').distinct().count()

    # THIS MONTH EXPENSE
    current_month = datetime.now().month
    this_month = expenses.filter(date__month=current_month).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        "expenses": expenses,
        "total_expense": total_expense,
        "total_categories": total_categories,
        "this_month": this_month
    }
    return render(request, "dashboard.html", context)

# ADD EXPENSE
@login_required(login_url="/login/")
def add_expense(request):

    if request.method == "POST":
        title = request.POST.get("title")
        amount = request.POST.get("amount")
        category = request.POST.get("category")
        date = request.POST.get("date")


        Expense.objects.create(
            user=request.user, 
            title=title,
            amount=amount,
            category=category,
            date=date
        )

        return redirect("/dashboard/")

    return render(request, "add_expense.html")

@login_required(login_url="/login/")
def edit_expense(request, id):

    expense = Expense.objects.get(id=id)

    if request.method == "POST":
        expense.title = request.POST.get("title")
        expense.amount = request.POST.get("amount")
        expense.category = request.POST.get("category")
        expense.date = request.POST.get("date")

        expense.save()

        return redirect("/dashboard/")

    return render(request, "edit_expense.html", {"expense": expense})


@login_required(login_url="/login/")
def delete_expense(request, id):

    expense = Expense.objects.get(id=id)
    expense.delete()

    return redirect("/dashboard/")


# LOGOUT
def logout_page(request):
    logout(request)
    return redirect("/login/")