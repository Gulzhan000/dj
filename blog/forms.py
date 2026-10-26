from django import forms

from .models import Blog


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'description', 'author']
        labels = {'title': 'Заголовок', 'description': 'Описание', 'author': 'Автор'}
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}
