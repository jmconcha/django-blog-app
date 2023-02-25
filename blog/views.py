from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Blog
from .forms import BlogForm, CommentForm
from .utils import title_as_slug

# Create your views here.
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.rel_comments.order_by('-created_at')
    
    comment_form = CommentForm()
    comment_form.fields['comment_text'].widget.attrs['class'] = 'textarea'
    comment_form.fields['comment_text'].widget.attrs['rows'] = '3'
    comment_form.fields['comment_text'].widget.attrs['placeholder'] = 'Write a comment...'
    
    if comment_form['comment_text'].errors:
        comment_form.fields['comment_text'].widget.attrs['class'] += ' is-danger'
    
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form
    })
    
@login_required(login_url=reverse_lazy('core:login'))
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            title_random_slug = title_as_slug(blog.title)
            blog.slug = title_random_slug
            blog.author = request.user
            blog.save()
            
            return redirect(reverse('core:front_page'))
    else:
        form = BlogForm()
    
    for formField in form:
        if formField.errors:
            formField.field.widget.attrs['class'] += ' is-danger'
    
    return render(request, 'blog/create_blog.html', {
        'form': form,
    })
    
def comment_on_blog(request, blog_slug):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=blog_slug)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.save()
            
            return redirect(reverse('blog:blog_detail', args=(blog_slug,)))
    
    return render(request, 'blog/blog_detail', {
        'blog': blog,
        'comment_form': CommentForm(),
    })
    
def search_blog(request):
    query = request.GET.get('query', '')
    blogs = Blog.objects.filter(Q(title__icontains=query) | Q(body__icontains=query))
    
    if blogs.count() == 0:
        messages.add_message(request, messages.INFO, "There's no blog that match your query")
        return redirect(reverse('core:front_page'))
    
    recent_to_oldest_blogs = blogs.order_by('-created_at')
    return render(request, 'core/front_page.html', {
        'blogs': recent_to_oldest_blogs,
    })
    