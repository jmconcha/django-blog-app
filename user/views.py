from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from blog.models import Blog
from .models import UserProfile

# Create your views here.
def user_blogs(request, username):
    author = User.objects.filter(username=username).first()
    if author == None:
        messages.add_message(request, messages.INFO, "Blogger don't exist")
        return redirect(reverse('core:front_page'))
    else:
        author_blogs = Blog.objects.filter(author__username=username)
        displayable_blogs = author_blogs
        is_visitor_author = author.username == request.user.username
        if not is_visitor_author:
            displayable_blogs = author_blogs.filter(status=Blog.ACTIVE)
        displayable_blogs = displayable_blogs.order_by('-created_at')[:10]
        
        return render(request, 'user/user_blogs.html', {
            'blogs': displayable_blogs,
            'author': author,
            'is_visitor_author': is_visitor_author,
            'BLOG_STATUS': {
              'DRAFT': Blog.DRAFT,
              'ACTIVE': Blog.ACTIVE,
            },
        })

@login_required(login_url=reverse_lazy('core:login'))
def user_profile(request, username):
    if request.user.username != username:
        raise PermissionDenied
    
    user_profile = request.user.rel_profile
    user_info = {
        'username': request.user.username,
        'firstname': request.user.first_name,
        'lastname': request.user.last_name,
        'email': request.user.email,
        'bio': user_profile.bio,
        'location': user_profile.location,
        'birth_date': user_profile.birth_date,
    }
    
    print(user_info)
    
    if request.method == 'POST':
        pass
    else:
        return render(request, 'user/profile.html', {
            'user_info': user_info,
        })