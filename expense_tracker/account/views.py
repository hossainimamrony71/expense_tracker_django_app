# yourapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import UserForm
from .models import User

@login_required
def user_list(request):
    # Only admin users can view the list
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("You are not allowed to view this page.")
    users = User.objects.all()
    return render(request, 'userlists.html', {'users': users})

@login_required
def user_create(request):
    # Only admin users can create new users
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("You are not allowed to create users.")
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'newuser.html', {'form': form, 'action': 'Create'})

@login_required
def user_update(request, pk):
    # Only admin users can update user information
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("You are not allowed to update users.")
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user_obj)
    return render(request, 'newuser.html', {'form': form, 'action': 'Update'})




# yourapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index_view(request):
    # Process the login form if submitted.
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
        else:
            messages.error(request, 'Invalid username or password.')
        return redirect('dashboard')
    else:
        # Otherwise, show the login form.
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')
