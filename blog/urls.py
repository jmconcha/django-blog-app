from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('search/', views.search_blog, name="search_blog"),
    path('blog/create/', views.create_blog, name='create_blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:blog_slug>/comment/', views.comment_on_blog, name='comment_on_blog'),
]