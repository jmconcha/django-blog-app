from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [
    path('<str:username>/blogs/', views.user_blogs, name='user_blogs'),
]