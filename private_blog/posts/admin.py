from django.contrib import admin

from .models import Comment, Favourite, Message, Post


class PostAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по публикациям."""

    list_display = (
        'pk',
        'pub_date',
        'modify_date',
        'title',
        'subheader',
        'text',
    )
    search_fields = ('title', 'subheader', 'text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по комментариям."""

    list_display = (
        'pk',
        'post',
        'author',
        'comment_text',
        'created',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class FavouriteAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по лайкам."""

    list_display = (
        'pk',
        'liker',
        'favourite_post',
    )
    list_filter = ('liker', 'favourite_post',)
    empty_value_display = '-пусто-'


class MessageAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по сообщениям."""

    list_display = (
        'pk',
        'send_time',
        'interlocutor',
        'direction',
        'message_text',
    )
    list_filter = ('interlocutor', 'direction',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Comment, CommentAdmin)
