from django.contrib import admin

from .models import Blog, Comment
from .utils import title_as_slug


class BlogAdmin(admin.ModelAdmin):
    exclude = ('slug',)

    def save_model(self, request, obj, form, change):
        obj.slug = title_as_slug(obj.title)
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)
