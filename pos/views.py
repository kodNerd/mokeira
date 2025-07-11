from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Stock, Expense, Injection, UserProfile
from django.db.models import Sum, F, Q
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
import random
from django.contrib.auth.decorators import login_required
# from reportlab.pdfgen import canvas  # Uncomment if using reportlab

def index(request):
    """Main POS interface view"""
    return render(request, 'pos/index.html')

@login_required
def dash(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_type = request.POST.get('product_type')
        buying_price = request.POST.get('buying_price')
        selling_price = request.POST.get('selling_price')
        quantity = request.POST.get('quantity')
        expiry_date = request.POST.get('expiry_date')
        supplier = request.POST.get('supplier')

        # Validation for required fields
        if not all([product_name, buying_price, selling_price, quantity]):
            messages.error(request, 'Please fill in all required fields (Product Name, Buying Price, Selling Price, Quantity).')
            return redirect(reverse('pos:home'))

        stock = Stock(
            product_name=product_name,
            product_type=product_type or None,
            buying_price=buying_price,
            selling_price=selling_price,
            quantity=quantity,
            expiry_date=expiry_date or None,
            supplier=supplier or None
        )
        stock.save()
        messages.success(request, 'Stock added successfully!')
        return redirect(reverse('pos:inventory'))
    stocks = Stock.objects.all()
    low_stock_count = stocks.filter(quantity__lte=5).count()
    from .models import Expense, Injection
    from django.db.models import Sum
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_injections = Injection.objects.aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'stocks': stocks,
        'low_stock_count': low_stock_count,
        'total_expenses': total_expenses,
        'total_injections': total_injections,
    }
    return render(request, 'pos/home.html', context)

@login_required
def inventory(request):
    # Single search box for all fields
    search = request.GET.get('search', '').strip()
    stocks = Stock.objects.all()
    if search:
        stocks = stocks.filter(
            Q(product_name__icontains=search) |
            Q(product_type__icontains=search) |
            Q(supplier__icontains=search)
        )
    stocks = stocks.order_by('-created_at')
    total_products = stocks.count()
    total_value = stocks.aggregate(value=Sum(F('buying_price') * F('quantity')))['value'] or 0
    low_stock_count = stocks.filter(quantity__lte=5).count()
    context = {
        'stocks': stocks,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'search': search,
    }
    return render(request, 'pos/inventory.html', context)

# PDF Export (simple version, CSV alternative if no reportlab)
@login_required
def inventory_export_pdf(request):
    # Single search box for all fields
    search = request.GET.get('search', '').strip()
    stocks = Stock.objects.all()
    if search:
        stocks = stocks.filter(
            Q(product_name__icontains=search) |
            Q(product_type__icontains=search) |
            Q(supplier__icontains=search)
        )
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont('Helvetica-Bold', 14)
    p.drawString(40, y, 'Inventory Export')
    y -= 30
    p.setFont('Helvetica', 10)
    p.drawString(40, y, f'Filter: search={search}')
    y -= 20
    p.setFont('Helvetica-Bold', 10)
    p.drawString(40, y, 'Product')
    p.drawString(140, y, 'Type')
    p.drawString(220, y, 'Buying')
    p.drawString(280, y, 'Selling')
    p.drawString(340, y, 'Qty')
    p.drawString(380, y, 'Expiry')
    p.drawString(440, y, 'Supplier')
    y -= 15
    p.setFont('Helvetica', 10)
    for stock in stocks:
        if y < 50:
            p.showPage()
            y = height - 40
        p.drawString(40, y, str(stock.product_name))
        p.drawString(140, y, str(stock.product_type or '-'))
        p.drawString(220, y, str(stock.buying_price))
        p.drawString(280, y, str(stock.selling_price))
        p.drawString(340, y, str(stock.quantity))
        p.drawString(380, y, str(stock.expiry_date or '-'))
        p.drawString(440, y, str(stock.supplier or '-'))
        y -= 15
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def stock_create(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_type = request.POST.get('product_type')
        buying_price = request.POST.get('buying_price')
        selling_price = request.POST.get('selling_price')
        quantity = request.POST.get('quantity')
        expiry_date = request.POST.get('expiry_date')
        supplier = request.POST.get('supplier')
        stock = Stock(
            product_name=product_name,
            product_type=product_type or None,
            buying_price=buying_price,
            selling_price=selling_price,
            quantity=quantity,
            expiry_date=expiry_date or None,
            supplier=supplier or None
        )
        stock.save()
        messages.success(request, 'Product added to inventory!')
        return redirect(reverse('pos:inventory'))
    return render(request, 'pos/stock_form.html', {'action': 'Add'})

@login_required
def stock_update(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.product_name = request.POST.get('product_name')
        stock.product_type = request.POST.get('product_type')
        stock.buying_price = request.POST.get('buying_price')
        stock.selling_price = request.POST.get('selling_price')
        stock.quantity = request.POST.get('quantity')
        stock.expiry_date = request.POST.get('expiry_date') or None
        stock.supplier = request.POST.get('supplier')
        stock.save()
        messages.success(request, 'Product updated!')
        return redirect(reverse('pos:inventory'))
    return render(request, 'pos/stock_form.html', {'stock': stock, 'action': 'Edit'})

@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Product deleted!')
        return redirect(reverse('pos:inventory'))
    return render(request, 'pos/stock_confirm_delete.html', {'stock': stock})

def expenses(request):
    return render(request, 'pos/expenses.html')

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'pos/expenses.html', {'expenses': expenses})

@login_required
def expense_create(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        staff = request.POST.get('staff')
        if not description or not amount:
            messages.error(request, 'Description and amount are required.')
            return redirect('pos:expenses')
        Expense.objects.create(description=description, amount=amount, staff=staff)
        messages.success(request, 'Expense added successfully!')
        return redirect('pos:expenses')
    return redirect('pos:expenses')

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        staff = request.POST.get('staff')
        if not description or not amount:
            messages.error(request, 'Description and amount are required.')
            return redirect('pos:expenses')
        expense.description = description
        expense.amount = amount
        expense.staff = staff
        expense.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('pos:expenses')
    return redirect('pos:expenses')

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('pos:expenses')
    return redirect('pos:expenses')

@login_required
def injection_list(request):
    injections = Injection.objects.all().order_by('-date')
    return render(request, 'pos/injections.html', {'injections': injections})

@login_required
def injection_create(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        staff = request.POST.get('staff')
        if not description or not amount:
            messages.error(request, 'Description and amount are required.')
            return redirect('pos:injections')
        Injection.objects.create(description=description, amount=amount, source=source, staff=staff)
        messages.success(request, 'Injection added successfully!')
        return redirect('pos:injections')
    return redirect('pos:injections')

@login_required
def injection_update(request, pk):
    injection = get_object_or_404(Injection, pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        staff = request.POST.get('staff')
        if not description or not amount:
            messages.error(request, 'Description and amount are required.')
            return redirect('pos:injections')
        injection.description = description
        injection.amount = amount
        injection.source = source
        injection.staff = staff
        injection.save()
        messages.success(request, 'Injection updated successfully!')
        return redirect('pos:injections')
    return redirect('pos:injections')

@login_required
def injection_delete(request, pk):
    injection = get_object_or_404(Injection, pk=pk)
    if request.method == 'POST':
        injection.delete()
        messages.success(request, 'Injection deleted successfully!')
        return redirect('pos:injections')
    return redirect('pos:injections')

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        shop_name = request.POST.get('shop_name')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        if not all([full_name, shop_name, username, phone, password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'pos/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'pos/register.html')
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'pos/register.html')
        user = User.objects.create_user(username=username, password=password, is_active=True, is_superuser=True, is_staff=True)
        profile = UserProfile.objects.create(user=user, full_name=full_name, shop_name=shop_name, phone=phone, is_verified=True)
        auth_login(request, user)
        messages.success(request, 'Registration successful! You are now logged in as superuser.')
        return redirect('pos:dash')
    return render(request, 'pos/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('pos:dash')
        else:
            messages.error(request, 'Invalid credentials or account not verified.')
    return render(request, 'pos/login.html')

@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('pos:index')