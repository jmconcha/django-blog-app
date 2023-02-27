from django.contrib.auth.models import User

def create_user(username, password, **kwargs):
    return User.objects.create_user(username=username, password=password, **kwargs)