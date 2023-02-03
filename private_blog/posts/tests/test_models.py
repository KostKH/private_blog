from django.test import TestCase
from posts.models import Comment, Favourite, Message, Post, User


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_one = User.objects.create(username='UserOne')
        cls.author = User.objects.create_superuser(username='Author')
        cls.post = Post.objects.create(
            title='Статья для теста - заголовок',
            subheader='А это подзаголовок',
            text='Ну и сама статья - она вот такая, короткая.'
        )
        cls.post2 = Post.objects.create(
            title='Статья2 для теста - заголовок',
            subheader='А это подзаголовок2',
            text='Ну и вторая статья - тоже короткая.'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_one,
            comment_text='Небольшой комментарий к статье'
        )
        cls.comment2 = Comment.objects.create(
            post=cls.post,
            author=cls.user_one,
            comment_text='Второй комментарий к статье'
        )
        cls.message = Message.objects.create(
            interlocutor=cls.user_one,
            direction='TO_AUTHOR',
            message_text='Маленькое сообщение автору'
        )
        cls.like = Favourite.objects.create(
            liker=cls.author,
            favourite_post=cls.post
        )
        cls.like = Favourite.objects.create(
            liker=cls.user_one,
            favourite_post=cls.post
        )

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        field_verboses = [
            (self.post, 'title', 'Заголовок статьи'),
            (self.post, 'subheader', 'Подзаголовок статьи'),
            (self.post, 'text', 'Текст статьи'),
            (self.post, 'pub_date', 'Дата публикации'),
            (self.post, 'modify_date', 'Дата последних изменений'),
            (self.post, 'image', 'Изображение'),
            (self.comment, 'comment_text', 'Текст комментария'),
            (self.comment, 'created', 'Дата комментария'),
            (self.message, 'message_text', 'Текст комментария'),
            (self.message, 'send_time', 'Дата комментария'),
        ]
        for item, field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    item._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_count_for_post(self):
        """Проверяем, что кол-во комментариев к посту правильно считается."""
        self.assertEqual(self.post.comment_count(), 2)
        self.assertEqual(self.post2.comment_count(), 0)

    def test_like_count_for_post(self):
        """Проверяем, что кол-во лайков к посту правильно считается."""
        self.assertEqual(self.post.like_count(), 2)
        self.assertEqual(self.post2.like_count(), 0)

    def test_is_liked_by_user_for_post(self):
        """Проверяем, что правильно определяется, лайкал юзер пост или нет."""
        self.assertEqual(self.post.is_liked_by_user(self.user_one), True)
        self.assertEqual(self.post.is_liked_by_user(self.author), True)
        self.assertEqual(self.post2.is_liked_by_user(self.user_one), False)
