from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .models import Blog
from .forms import BlogForm, CommentForm
from .utils import title_as_slug

# Create your views here.


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.rel_comments.order_by('created_at')

    comment_form = CommentForm()
    comment_form.fields['comment_text'].widget.attrs['class'] = 'textarea'
    comment_form.fields['comment_text'].widget.attrs['rows'] = '3'
    comment_form.fields['comment_text'].widget.attrs['placeholder'] = 'Write a comment...'

    if comment_form['comment_text'].errors:
        comment_form.fields['comment_text'].widget.attrs['class'] += ' is-danger'

    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
        'BLOG_STATUS': {
            'DRAFT': Blog.DRAFT,
            'ACTIVE': Blog.ACTIVE,
        },
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
            for formField in form:
                if formField.errors:
                    formField.field.widget.attrs['class'] += ' is-danger'
    else:
        form = BlogForm()

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
            comment.user = request.user
            comment.save()

            return redirect(reverse('blog:blog_detail', args=(blog_slug,)))

    return render(request, 'blog/blog_detail', {
        'blog': blog,
        'comment_form': CommentForm(),
    })


def search_blog(request):
    query = request.GET.get('query', '')
    result = None

    active_blogs = Blog.objects.filter(status=Blog.ACTIVE)
    if active_blogs.count() > 0:
        blogs_match = active_blogs.filter(
            Q(title__icontains=query) | Q(body__icontains=query))
        if blogs_match.count() == 0:
            messages.add_message(request, messages.INFO,
                                 "There's no blog that match your query")
            # display recent blogs instead
            result = active_blogs
        else:
            result = blogs_match

    result = result.order_by('-created_at')[:10] if result else []
    return render(request, 'core/front_page.html', {
        'blogs': result,
    })


@login_required(login_url=reverse_lazy('core:login'))
def update_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.user.username != blog.author.username:
        raise PermissionDenied

    if blog.status == Blog.ACTIVE:
        return redirect(reverse('blog:blog_detail', args=(blog.slug,)))

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            updated_blog = form.save(commit=False)
            title_random_slug = title_as_slug(updated_blog.title)
            updated_blog.slug = title_random_slug
            updated_blog.save()

            messages.add_message(request, messages.SUCCESS,
                                 'Your blog has been updated.')

            return redirect(reverse('blog:blog_detail', args=(updated_blog.slug,)))
        else:
            for formField in form:
                if formField.errors:
                    formField.field.widget.attrs['class'] += ' is-danger'
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog/update_blog.html', {
        'form': form,
        'blog_slug': blog.slug,
    })
