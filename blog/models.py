from django.db import models

# Create your models here.
class Blog(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='rel_comment', on_delete=models.CASCADE)
    slug = models.SlugField()
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.comment_text[:100]