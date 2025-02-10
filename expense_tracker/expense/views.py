from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from .models import ExpenseCategory, User, MoneyAllocation, Transaction
from .forms import ExpenseCategoryForm, MoneyAllocationForm
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index_view(request):
    if request.user.user_type == 'admin':
        base_template = 'base.html'
    elif request.user.user_type in ['ted', 's2l']:
        base_template = 'department_base.html'
    else:
        # Optional: provide a default if needed
        base_template = 'department_base.html'

    return render(request, 'admin_dashboard.html', {'base_template': base_template})

# @login_required
# def index_view(request):
#     if request.user.is_authenticated:
#         if request.user.user_type == 'admin':
#             template = 'admin_dashboard.html'
#         elif request.user.user_type in ['ted', 's2l']:
#             template = 'department_dashboard.html'
#         return render(request, template)




class TedS2lCategoryList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ExpenseCategory
    template_name = 'categorylist.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        user_type = self.kwargs.get('user_type')
        if user_type not in user_type:
            return ExpenseCategory.objects.none()  

        return ExpenseCategory.objects.filter(
            created_by__user_type=user_type
        ).order_by('-created_at')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_button'] = self.request.user.user_type != 'admin' 
        return context
    
    def test_func(self):
        return self.request.user.user_type == 'admin' or self.request.user.is_superuser





@login_required
def allocated_money(request):
    # Only admin users can allocate money.
    if request.user.user_type != 'admin':
        raise PermissionDenied("Only an admin can allocate money.")
    
    if request.method == 'POST':
        form = MoneyAllocationForm(request.POST, request=request)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.allocated_by = request.user  # Set the admin making the allocation.
            
            if allocation.allocated_to == request.user:
                # Allocating to self: No deduction, add directly
                allocation.save()
                return redirect('allocated_money')
            else:
                # Check if admin has enough balance
                if allocation.amount > request.user.balance:
                    form.add_error('amount', "Insufficient balance to allocate this amount.")
                else:
                    try:
                        # Deduct from admin's balance and save
                        request.user.balance -= allocation.amount
                        request.user.save()
                        # Save allocation (adds to target's balance)
                        allocation.save()
                        return redirect('allocated_money')
                    except Exception as e:
                        form.add_error(None, str(e))
        # If form is invalid or exceptions, fall through to render form with errors
    else:
        form = MoneyAllocationForm(request=request)
    
    # Retrieve all allocations, sorted with the most recent first.
    allocations = MoneyAllocation.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'allocations': allocations,
    }
    return render(request, 'allocated_money.html', context)

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from datetime import datetime
from .models import Transaction, ExpenseCategory

from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from account.models import User  # Adjust this import as needed.
from .models import Transaction, ExpenseCategory

class TedS2lExpenseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Transaction
    template_name = 'expenselist.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        user_type = self.kwargs.get('user_type')
        qs = Transaction.objects.filter(user__user_type=user_type)
        
        # Date filter
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                qs = qs.filter(created_at__date=date_obj)
            except ValueError:
                pass

        # Category filter
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)

        # Amount filter
        amount = self.request.GET.get('amount')
        if amount:
            try:
                amount_val = Decimal(amount)
                qs = qs.filter(ammount=amount_val)
            except Exception:
                pass

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.kwargs.get('user_type')
        now = timezone.localtime(timezone.now())  # Bangladesh time

        # Today's boundaries
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Aggregates
        today_expense = Transaction.objects.filter(
            user__user_type=user_type,
            created_at__range=(start_of_today, end_of_today)
        ).aggregate(total=Sum('ammount'))['total'] or 0

        total_expense = Transaction.objects.filter(
            user__user_type=user_type
        ).aggregate(total=Sum('ammount'))['total'] or 0

        user_stats = User.objects.filter(user_type=user_type).aggregate(
            total_balance=Sum('balance'),
            total_loan_balance=Sum('loan_balance')
        )
        user_type = self.kwargs.get('user_type')
        context['user_type'] = user_type 
        context['show_button'] = self.request.user.user_type != 'admin'
        context.update({
            
            'today_expense': today_expense,
            'total_expense': total_expense,
            'balance': user_stats['total_balance'] or 0,
            'loan_balance': user_stats['total_loan_balance'] or 0,
            'categories': ExpenseCategory.objects.filter(created_by=self.request.user)
        })
        return context

    def test_func(self):
        return self.request.user.user_type == 'admin' or self.request.user.is_superuser





# ------------------------------------------------------------------------------
# List View: Display all categories created by the current user.
# ------------------------------------------------------------------------------
class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = 'categorylist.html'  # Your list page template.
    context_object_name = 'categories'
   
    
    def get_queryset(self):
        # Only return the categories created by the logged-in user.
        return ExpenseCategory.objects.filter(created_by=self.request.user).order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_button'] = True

        return context
# ------------------------------------------------------------------------------
# Create View: Add a new expense category.
# ------------------------------------------------------------------------------
class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'addcategory.html'  # Reuse for add & edit.
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        # Automatically assign the current user as the creator.
        form.instance.created_by = self.request.user
        return super().form_valid(form)


# ------------------------------------------------------------------------------
# Update View: Edit an existing expense category.
# ------------------------------------------------------------------------------
class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'addcategory.html'
    success_url = reverse_lazy('category-list')

    def get_queryset(self):
        # Restrict edits to categories created by the current user.
        return ExpenseCategory.objects.filter(created_by=self.request.user)


# ------------------------------------------------------------------------------
# AJAX Delete View: Delete a category inline via AJAX from the list page.
# ------------------------------------------------------------------------------
class ExpenseCategoryAjaxDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            # Get the category, ensuring the user is the creator.
            category = ExpenseCategory.objects.get(pk=pk, created_by=request.user)
            category.delete()
            return JsonResponse({'success': True})
        except ExpenseCategory.DoesNotExist:
            return JsonResponse(
                {'success': False, 'error': 'Category not found.'},
                status=404
            )


# views.py
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Transaction, ExpenseCategory
from .forms import TransactionForm

from django.db import transaction

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'addexpense.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=self.request.user.pk)
            amount = form.cleaned_data['ammount']

            if user.balance < amount:
                form.add_error('ammount', 'Insufficient balance.')
                return self.form_invalid(form)

            user.balance -= amount
            user.save()

            form.instance.user = user
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ExpenseCategory.objects.filter(created_by=self.request.user).order_by('-created_at')
        context['is_update'] = False  # Set flag to indicate it's a creation view
        return context


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'addexpense.html'
    success_url = reverse_lazy('expense-list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        with transaction.atomic():
            transaction_obj = self.get_object()
            transaction_obj = Transaction.objects.select_for_update().get(pk=transaction_obj.pk)
            user = User.objects.select_for_update().get(pk=self.request.user.pk)

            original_amount = transaction_obj.ammount
            new_amount = form.cleaned_data['ammount']
            amount_diff = new_amount - original_amount

            if amount_diff > 0 and user.balance < amount_diff:
                form.add_error('ammount', 'Insufficient balance to cover the increase.')
                return self.form_invalid(form)

            user.balance -= amount_diff
            user.save()

            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ExpenseCategory.objects.filter(created_by=self.request.user).order_by('-created_at')
        context['is_update'] = True  # Set flag to indicate it's an update view
        return context


# views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from datetime import datetime
from .models import Transaction, ExpenseCategory

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'expenselist.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        
        # Filters
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                qs = qs.filter(created_at__date=date_obj)
            except ValueError:
                pass

        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)

        amount = self.request.GET.get('amount')
        if amount:
            try:
                amount_val = Decimal(amount)
                qs = qs.filter(ammount=amount_val)
            except Exception:
                pass

        transaction_type = self.request.GET.get('transaction_type')
        if transaction_type:
            qs = qs.filter(transaction_type=transaction_type)

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.localtime(timezone.now())  # Bangladesh time

        # Today's boundaries
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Aggregates
        today_expense = Transaction.objects.filter(
            user=user,
            created_at__range=(start_of_today, end_of_today)
        ).aggregate(total=Sum('ammount'))['total'] or 0
        context['user_type'] = None 
        context['show_button'] = True 
        context['lone_hide'] = self.request.user.user_type == 'admin' 
        context.update({
            'today_expense': today_expense,
            'total_expense': Transaction.objects.filter(user=user).aggregate(total=Sum('ammount'))['total'] or 0,
            'balance': user.balance,
            'loan_balance': user.loan_balance,
            'categories': ExpenseCategory.objects.filter(created_by=user)
        })
        return context
    
class ExpenseDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            with transaction.atomic():
                # Lock the transaction and user rows
                expense = Transaction.objects.select_for_update().get(pk=pk, user=request.user)
                user = User.objects.select_for_update().get(pk=request.user.pk)

                user.balance += expense.ammount
                user.save()

                expense.delete()
                return JsonResponse({'success': True})
        except Transaction.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Expense not found.'}, status=404)




# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import LoanRequest, User
from .forms import LoanRequestForm

@login_required
def create_loan_request(request):
    # Only allow TED and S2L users to create a loan request.
    if request.user.user_type not in ['ted', 's2l']:
        messages.error(request, "Only TED and S2L departments can create loan requests.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoanRequestForm(request.POST, user=request.user)
        if form.is_valid():
            loan_request = form.save(commit=False)
            # Automatically set the “from_department” as the current user’s department.
            loan_request.from_department = request.user.user_type
            loan_request.save()
            messages.success(request, "Loan request submitted successfully.")
            return redirect('loan_ted_s2l')
    else:
        form = LoanRequestForm(user=request.user)
    
    # List all loan requests from the current user’s department.
    allocations = LoanRequest.objects.filter(from_department=request.user.user_type).order_by('-requested_at')
    return render(request, 'loan_ted_s2l.html', {'form': form, 'allocations': allocations})

# Helper function for admin check
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import LoanRequest, User
from .forms import LoanRequestForm

def is_admin(user):
    return user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def loan_admin(request):
    # Retrieve all loan requests (regardless of status)
    loans = LoanRequest.objects.all().order_by('-requested_at')
    
    # Get today's date
    today = timezone.now().date()
    
    # Aggregate approved loans taken today by department.
    # For example, if a department takes a loan, its department code is stored in from_department.
    ted_today = LoanRequest.objects.filter(
        status='approved',
        requested_at__date=today,
        from_department='ted'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    s2l_today = LoanRequest.objects.filter(
        status='approved',
        requested_at__date=today,
        from_department='s2l'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Aggregate overall approved loans by department.
    ted_total = LoanRequest.objects.filter(
        status='approved',
        from_department='ted'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    s2l_total = LoanRequest.objects.filter(
        status='approved',
        from_department='s2l'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    context = {
        'loans': loans,
        'ted_today': ted_today,
        's2l_today': s2l_today,
        'ted_total': ted_total,
        's2l_total': s2l_total,
    }
    return render(request, 'loan_admin.html', context)

@login_required
@user_passes_test(is_admin)
def approve_loan_request(request, pk):
    loan_request = get_object_or_404(LoanRequest, pk=pk)
    try:
        loan_request.approve(request.user)
        messages.success(request, f"Loan request #{loan_request.id} approved.")
    except Exception as e:
        messages.error(request, f"Error approving loan request: {str(e)}")
    return redirect('loan_admin')

@login_required
@user_passes_test(is_admin)
def decline_loan_request(request, pk):
    loan_request = get_object_or_404(LoanRequest, pk=pk)
    try:
        loan_request.decline(request.user)
        messages.success(request, f"Loan request #{loan_request.id} declined.")
    except Exception as e:
        messages.error(request, f"Error declining loan request: {str(e)}")
    return redirect('loan_admin')