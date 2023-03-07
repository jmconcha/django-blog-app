from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib import messages

from blog.models import Blog

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
