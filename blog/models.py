from django.db import models

# Create your models here.
class Blog(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)