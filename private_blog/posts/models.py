from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    """Класс Post создает БД SQL для хранения статей."""

    title = models.CharField(
        verbose_name='Заголовок статьи',
        max_length=50
    )
    subheader = models.CharField(
        verbose_name='Подзаголовок статьи',
        max_length=100
    )
    text = models.TextField(
        verbose_name='Текст статьи',
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    modify_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата последних изменений'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    class Meta:
        ordering = ('-pub_date', '-pk')

    def __str__(self):
        return self.title[:25]

    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    def like_count(self):
        return Favourite.objects.filter(favourite_post=self).count()

    def is_liked_by_user(self, user):
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(
            favourite_post=self,
            liker=user
        ).exists()


class Comment(models.Model):
    """Класс Comment создает БД SQL для хранения комментариев к статьям."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    comment_text = models.TextField(
        verbose_name='Текст комментария',
        max_length=450,
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )

    class Meta:
        ordering = ('post', 'created', 'pk')

    def __str__(self):

        return self.comment_text[:25]


class Favourite(models.Model):
    """Класс создает БД SQL для хранения
    информации о лайках к статьям."""

    liker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    favourite_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='favourites'
    )

    class Meta:
        unique_together = ['liker', 'favourite_post']

    def __str__(self):
        liker_str = self.liker.username
        favourite_post_str = self.favourite_post.title
        return liker_str + ' - ' + favourite_post_str


class Message(models.Model):
    """Класс создает БД SQL для хранения переписки с автором."""

    MESSAGE_DIRECTION = (
        ('FROM_AUTHOR', 'From Author'),
        ('TO_AUTHOR', 'To Author'),
    )
    interlocutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message',
    )
    direction = models.CharField(
        max_length=11,
        choices=MESSAGE_DIRECTION,
    )
    message_text = models.TextField(
        verbose_name='Текст комментария',
        max_length=450,
    )
    send_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )

    class Meta:
        ordering = ('interlocutor', 'send_time', 'pk')

    def __str__(self):
        return self.message_text[:30]
