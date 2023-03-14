from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name='rel_profile', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    picture = models.CharField(
        max_length=100,  blank=True, default='/media/thumbnails/default.png')

    def __str__(self):
        return self.user.username
