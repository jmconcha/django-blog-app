from django.shortcuts import render

from blog.models import Blog

# Create your views here.

def front_page(request):
    blogs = Blog.objects.order_by('-created_at')[:10]
    
    return render(request, 'core/front_page.html', {
        'blogs': blogs,
    })