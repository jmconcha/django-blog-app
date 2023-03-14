from django.contrib import admin

from .models import Blog, Comment
from .utils import title_as_slug


class BlogAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_filter = ('status',)
    list_display = ('author', 'title', 'body', 'created_at')
    search_fields = ('title__icontains',
                     'body__icontains', 'author__username__iexact', 'author__first_name__icontains', 'author__last_name__icontains')

    def save_model(self, request, obj, form, change):
        obj.slug = title_as_slug(obj.title)
        super().save_model(request, obj, form, change)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'comment_text', 'created_at')


# Register your models here.
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
