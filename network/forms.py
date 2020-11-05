from django import forms

class NewPostForm(forms.Form):
    newPostContent = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'newPost',
            'class': 'form-control',
            'cols': 20,
            'rows': 4
        }),
        label='New Post'
    )
