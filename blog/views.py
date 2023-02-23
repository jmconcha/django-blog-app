from django.shortcuts import render, redirect, reverse, get_object_or_404

from .models import Blog
from .forms import BlogForm

# Create your views here.
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
    })
    
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect(reverse('core:front_page'))
    else:
        form = BlogForm()
    
    for formField in form:
        if formField.errors:
            formField.field.widget.attrs['class'] += ' is-danger'
    
    return render(request, 'blog/create_blog.html', {
        'form': form,
    })