import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Favourite, Message, Post, User


class PostsViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_1.jpg',
            content=cls.small_jpg,
            content_type='image/gif'
        )
        cls.jpg_url = 'posts/small_1.jpg'
        cls.user_one = User.objects.create_user(username='UserOne')
        cls.author = User.objects.create_superuser(username='Author')
        cls.post = Post.objects.create(
            title='Статья для теста - заголовок',
            subheader='А это подзаголовок',
            text='Ну и сама статья - она вот такая, короткая.',
        )
        cls.post2 = Post.objects.create(
            title='Статья2 для теста - заголовок',
            subheader='А это подзаголовок2',
            text='Ну и вторая статья - тоже короткая.',
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post2,
            author=cls.user_one,
            comment_text='Небольшой комментарий к статье'
        )
        cls.message = Message.objects.create(
            interlocutor=cls.user_one,
            direction='TO_AUTHOR',
            message_text='Маленькое сообщение автору'
        )
        cls.message_reply = Message.objects.create(
            interlocutor=cls.user_one,
            direction='FROM_AUTHOR',
            message_text='А это ответ на сообщение'
        )
        cls.like = Favourite.objects.create(
            liker=cls.user_one,
            favourite_post=cls.post2
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_one)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = [
            ('posts/index.html', reverse('index')),
            ('posts/post.html', reverse('post_view', args=[self.post.id])),
            ('posts/comments.html', reverse('comments', args=[self.post.id])),
            ('posts/my_comments.html', reverse('my_comments')),
            ('posts/favourite.html', reverse('favourite')),
            ('posts/messages.html', reverse('messages')),
            ('posts/private_cabinet.html', reverse('private_cabinet')),
            ('posts/post_management.html', reverse('post_management')),
            ('posts/new.html', reverse('new_post')),
            ('posts/new.html', reverse('post_update', args=[self.post.id])),
            ('posts/post_delete.html', reverse('post_delete',
                                               args=[self.post.id])),
            ('posts/message_reply.html', reverse('message_reply')),
            ('posts/misc/404.html', reverse('err404')),
            ('posts/misc/500.html', reverse('err500')),
            ('posts/about.html', reverse('about')),
        ]
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        """В шаблон index передан правильный контекст."""
        response = self.guest_client.get(reverse('index'))
        post = response.context.get('page')[0]
        print(post.image)
        self.assertEqual(post.id, self.post2.id)
        self.assertEqual(post.title, self.post2.title)
        self.assertEqual(post.subheader, self.post2.subheader)
        self.assertEqual(post.image, self.jpg_url)
        self.assertEqual(post.comment_count(), self.post2.comment_count())
        self.assertEqual(post.like_count(), self.post2.like_count())
