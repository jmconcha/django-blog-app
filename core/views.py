from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from blog.models import Blog

# Create your views here.

def front_page(request):
    blogs = Blog.objects.order_by('-created_at')[:10]
    
    return render(request, 'core/front_page.html', {
        'blogs': blogs,
    })
    
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user == None:
            messages.add_message(request, messages.WARNING, "Your username and password didn't match. Please try again.")
        else:
            login(request, user)
            return redirect(reverse('core:front_page'))
        
    return render(request, 'core/login.html')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    
    return redirect(reverse('core:front_page'))