# birthday/forms.py
from django import forms

from django.core.exceptions import ValidationError
# Импортируем класс модели Birthday.
from .models import Post, Comment, User

from django.core.mail import send_mail

# Для использования формы с моделями меняем класс на forms.ModelForm.
class PostForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', )

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',) 
