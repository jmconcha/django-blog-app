from django import forms

from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('slug', 'title', 'body')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            if visible.name == 'body':
                visible.field.widget.attrs['class'] = 'textarea'
                visible.field.widget.attrs['rows'] = '3'
            else:
                visible.field.widget.attrs['class'] = 'input'