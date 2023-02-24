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
        next = request.POST.get('next')
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            next_url = next if next else reverse('core:front_page')
            return redirect(next_url)
        else:
            messages.add_message(request, messages.WARNING, "Your username and password didn't match. Please try again.")
    else:
        next = request.GET.get('next')
        
    return render(request, 'core/login.html', {
        'next': next,
    })

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    
    return redirect(reverse('core:front_page'))