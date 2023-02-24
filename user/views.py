from django.shortcuts import render

from blog.models import Blog

# Create your views here.
def user_blogs(request, username):
    user_blogs = Blog.objects.filter(author__username=username)
    active_blogs = user_blogs.filter(status=Blog.ACTIVE).order_by('-created_at')[:10]
    
    return render(request, 'core/front_page.html', {
        'blogs': active_blogs,
    })
