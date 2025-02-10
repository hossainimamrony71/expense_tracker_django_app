from django.db import models
from account.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class ExpenseCategory(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# models.py
from django.db import models
from django.core.exceptions import ValidationError
from account.models import User

class MoneyAllocation(models.Model):
    allocated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='allocations_made',
        help_text="Admin user who makes this allocation."
    )
    allocated_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='allocations_received',
        help_text="The user who receives the allocated money."
    )
    amount = models.DecimalField(
        max_digits=200,
        decimal_places=2,
        help_text="The amount to add to the target account (must be greater than zero)."
    )
    source = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validate that the amount is positive.
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

    def save(self, *args, **kwargs):
        # Disallow updates.
        if self.pk is not None:
            raise ValidationError("Updates are not allowed for MoneyAllocation once created.")
        # Ensure allocated_by is an admin.
        if self.allocated_by.user_type != 'admin':
            raise ValidationError("Only an admin can allocate money.")
        # Run model validations (including clean() method).
        self.full_clean()
        # Update the recipient's balance.
        self.allocated_to.balance += self.amount
        self.allocated_to.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Deletion of MoneyAllocation records is not allowed.")

    def __str__(self):
        return f"Allocation of {self.amount} to {self.allocated_to} by {self.allocated_by}"







class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
    ammount = models.DecimalField(max_digits=200, decimal_places=2)
    category = models.ForeignKey( ExpenseCategory, on_delete=models.CASCADE, related_name="category", blank=True, null=True)
    source = models.CharField(max_length=150, default="cash")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} --{self.ammount} "







class LoanRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    
    from_department = models.CharField(max_length=50, choices=User.CHOICES_USER_TYPE)
    to_department = models.CharField(max_length=50, choices=User.CHOICES_USER_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_loans'
    )

    def __str__(self):
        return f"Loan from {self.get_from_department_display()} to {self.get_to_department_display()} - {self.amount}"
    
    def approve(self, user):
        if self.status != 'pending':
            raise ValueError('Loan is not pending')
        
        # Find users by department type (this example assumes one user per department)
        from_user = User.objects.filter(user_type=self.from_department).first()
        to_user = User.objects.filter(user_type=self.to_department).first()
        
        if not to_user or not from_user:
            raise ValueError('User not found')
        
        if self.amount > to_user.balance:
            raise ValueError('Insufficient balance')
        
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save()
        
        # Update balances
        to_user.balance -= self.amount
        from_user.balance += self.amount
        
        # Update loan balances
        to_user.loan_balance += self.amount
        from_user.loan_balance -= self.amount
        
        to_user.save()
        from_user.save()
    
    def decline(self, user):
        if self.status != 'pending':
            raise ValueError('Loan is not pending')
        self.status = 'declined'
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save()
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = LoanRequest.objects.get(pk=self.pk)
            if original.status == 'approved':
                raise ValidationError('Approved loan requests cannot be updated.')
        super().save(*args, **kwargs)