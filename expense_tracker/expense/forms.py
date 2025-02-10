from django import forms
from .models import ExpenseCategory,Transaction
from django import forms
from .models import Transaction
from django import forms
from .models import MoneyAllocation
from account.models import User


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name',  'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['ammount',  'category', 'source']




from django import forms
from .models import MoneyAllocation
from account.models import User

class MoneyAllocationForm(forms.ModelForm):
    class Meta:
        model = MoneyAllocation
        fields = ['allocated_to', 'amount', 'source']
        widgets = {
            'allocated_to': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter Amount'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Expect the view to pass the request object.
        self.request = kwargs.pop('request', None)
        super(MoneyAllocationForm, self).__init__(*args, **kwargs)
        # Restrict recipients to allowed user types.
        allowed_types = ['admin', 'ted', 's2l']
        self.fields['allocated_to'].queryset = User.objects.filter(user_type__in=allowed_types)

    def clean(self):
        cleaned_data = super().clean()
        # Ensure that only an admin can allocate money.
        if self.request and self.request.user.user_type != 'admin':
            raise forms.ValidationError("Only an admin can allocate money.")
        return cleaned_data



# forms.py
from django import forms
from .models import LoanRequest, User

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['to_department', 'amount']
        widgets = {
            'to_department': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter Amount'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Pop the current user from the keyword arguments.
        self.user = kwargs.pop('user', None)
        super(LoanRequestForm, self).__init__(*args, **kwargs)
        if self.user:
            # If the user is from TED, they can only request from S2L (and vice versa).
            if self.user.user_type == 'ted':
                self.fields['to_department'].choices = [('s2l', 'S2L Department')]
            elif self.user.user_type == 's2l':
                self.fields['to_department'].choices = [('ted', 'TED Department')]
            else:
                # For admin (or any other type) you could either disable this form or allow both.
                self.fields['to_department'].choices = [choice for choice in User.CHOICES_USER_TYPE if choice[0] in ['ted', 's2l']]
