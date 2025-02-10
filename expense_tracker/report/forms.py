# forms.py
from django import forms

class ReportForm(forms.Form):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('ted', 'TED'),
        ('s2l', 'S2L'),
    )
    DATA_TYPE_CHOICES = (
        ('allocations', 'Money Allocations'),
        ('expenses', 'Expenses'),
        ('loans', 'Loans'),
    )

    user_types = forms.MultipleChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    data_types = forms.MultipleChoiceField(
        choices=DATA_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )