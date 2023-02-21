from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta():
        model = Post

        fields = (
            'text',
            'group',
            'image',
        )

    def clean_text(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError('Пожалуйста, заполните поле')

        return data


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment

        fields = (
            'text',
        )
