# yourapp/forms.py
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    # Extra fields for password and confirmation. They are not saved directly on the model.
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'pass-input'}),
        required=False,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'pass-inputs'}),
        required=False,
        label="Confirm Password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'mobile', 'user_type', 'profile_picture', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile'}),
            'user_type': forms.Select(attrs={'class': 'select'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        # Only check if at least one password field is filled (for creation or if updating the password)
        if password or confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
