from django.forms import ModelForm

from .models import Comment, Message, Post


class PostForm(ModelForm):
    """Класс генерит форму для создания/изменения статей."""

    class Meta:
        model = Post
        fields = [
            'title',
            'subheader',
            'text',
            'image',
        ]
        required = {
            'title': True,
            'subheader': True,
            'text': True,
            'image': True,
        }
        help_texts = {
            'title': 'Введите заголовок',
            'subheader': 'Введите подзаголовок',
            'text': 'Введите текст статьи',
            'image': 'Прикрепите изображение',
        }


class CommentForm(ModelForm):
    """Класс генерирует форму для написания комментариев."""

    class Meta:
        model = Comment
        fields = ['comment_text', ]
        required = {'comment_text': True}


class MessageForm(ModelForm):
    """Класс генерирует форму для написания сообщений."""

    class Meta:
        model = Message
        fields = ['message_text', ]
        required = {'message_text': True}
