from django import forms

from .models import Blog, Comment


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('status', 'title', 'body')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.name == 'body':
                visible.field.widget.attrs['class'] = 'textarea'
                visible.field.widget.attrs['rows'] = '10'
            else:
                visible.field.widget.attrs['class'] = 'input'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment_text',)
