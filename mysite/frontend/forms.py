from django import forms
from posts.models import Post

class PostForm(forms.Form):
    title = forms.CharField(label='Title:')
    description = forms.CharField(label='Description:')
    content = forms.CharField(label='', required=False, 
            widget=forms.Textarea(attrs={'placeholder': 'Enter content here (ignored for images)'}))
    content_type = forms.ChoiceField(choices=Post.CONTENT_TYPES)
    visibility = forms.ChoiceField(choices=Post.VISIBILITY_CHOICES)

    image = forms.ImageField(required=False)

class profileUpdateForm(forms.Form):
	github = forms.CharField(label='New Github Profile Link:', required=False)
	profileImage = forms.CharField(label='New Profile Image Link:', required=False)