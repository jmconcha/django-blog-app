from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import datetime

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
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()
        
        # format date before store
        date_string = request.POST['birth_date']
        date_format = '%m/%d/%Y'
        temp_datetime = datetime.strptime(date_string, date_format)
        timezone_datetime = timezone.datetime(temp_datetime.year, temp_datetime.month, temp_datetime.day)
        timezone_date = timezone_datetime.date()
        
        user_profile = request.user.rel_profile
        user_profile.birth_date = timezone_date
        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        user_profile.save()
    
        return HttpResponseRedirect(reverse('user:user_profile', args=(request.user.username,)))
    else:
        user_profile = request.user.rel_profile
        user_info = {
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # commented because planning to move this edit email to account view
            # 'email': request.user.email,
            'bio': user_profile.bio,
            'location': user_profile.location,
            'birth_date': user_profile.birth_date,
        }
        
        return render(request, 'user/profile.html', {
            'user_info': user_info,
        })