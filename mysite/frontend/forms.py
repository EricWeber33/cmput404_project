from django import forms
from django import forms

class PostForm(forms.Form):
    title = forms.CharField(label='Title:')
    description = forms.CharField(label='Description:')
    content = forms.CharField(label='Content:')
    content_type = forms.ChoiceField(choices=[('text/plain', 'text'), ('text/markdown', 'Markdown')])
    visibility = forms.ChoiceField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends only')])