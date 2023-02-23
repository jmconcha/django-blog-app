from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('blog/create/', views.create_blog, name='create_blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]