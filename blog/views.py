from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404

from .models import Blog
from .forms import BlogForm, CommentForm

# Create your views here.
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    comment_form = CommentForm()
    comment_form.fields['comment_text'].widget.attrs['class'] = 'textarea'
    comment_form.fields['comment_text'].widget.attrs['rows'] = '3'
    comment_form.fields['comment_text'].widget.attrs['placeholder'] = 'Write a comment...'
    
    if comment_form['comment_text'].errors:
        comment_form.fields['comment_text'].widget.attrs['class'] += ' is-danger'
    
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'comment_form': comment_form
    })
    
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request['POST'])
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