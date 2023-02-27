from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from blog.models import Blog
from .utils import check_is_empty

# Create your views here.

def front_page(request):
    blogs = Blog.objects.filter(status=Blog.ACTIVE).order_by('-created_at')[:10]
    
    return render(request, 'core/front_page.html', {
        'blogs': blogs,
    })
    
def login_user(request):
    errors = {}
    
    if request.method == 'POST':
        next = request.POST.get('next')
        username = request.POST['username']
        password = request.POST['password']
        
        # validate fields
        required_fields = {
            'username': username,
            'password': password,
        }
        errors = check_is_empty(required_fields)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = next if next else reverse('core:front_page')
            return redirect(next_url)
        else:
            messages.add_message(request, messages.WARNING, "Your username and password didn't match. Please try again.")
    else:
        next = request.GET.get('next')
        
    return render(request, 'core/login.html', {
        'next': next,
        'errors': errors,
    })

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    
    return redirect(reverse('core:front_page'))

def register_user(request):
    errors = {}
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', '')
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        
        required_fields = {
            'username': username,
            'password': password,
            'confirm_password': confirm_password,
        }
        
        errors = check_is_empty(required_fields)
        
        # checks if username is available
        try:
            User.objects.get(username=username)
            errors['username'] = 'Username is not available'
        except User.DoesNotExist:
            pass
        
        # validate input
        if password != confirm_password:
            errors['password'] = 'Password must match'
            errors['confirm_password'] = 'Password must match'
        
        if not errors:
            user = User.objects.create_user(username, email, password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'You are now successfully registered')
            
            return redirect(reverse('core:front_page'))
            
    return render(request, 'core/register.html', {
        'errors': errors,
    })