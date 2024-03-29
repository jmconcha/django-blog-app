from django.contrib.auth.models import User

from django.db import models

# Create your models here.


class Blog(models.Model):
    DRAFT = 'draft'
    ACTIVE = 'active'
    CHOICE_STATUS = (
        (DRAFT, 'Draft'),
        (ACTIVE, 'Active'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=CHOICE_STATUS, default=DRAFT)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(
        Blog, related_name='rel_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='rel_comments', on_delete=models.CASCADE)
    slug = models.SlugField()
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text[:100]
