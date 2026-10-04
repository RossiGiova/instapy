from django import forms

from core.forms import BootstrapFormMixin

from .models import Comment, Post


class PostForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ("image", "description")
        widgets = {
            "image": forms.FileInput(attrs={"accept": "image/png,image/jpeg"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class PostDescriptionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ("description",)
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
