from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
]