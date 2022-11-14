from django import forms
from posts.models import Post

class PostForm(forms.Form):
    title = forms.CharField(label='Title:')
    description = forms.CharField(label='Description:')
    content = forms.CharField(label='Content:', required=False)
    content_type = forms.ChoiceField(choices=Post.CONTENT_TYPES)
    visibility = forms.ChoiceField(choices=Post.VISIBILITY_CHOICES)

    image = forms.ImageField(required=False)