import shutil

from django import forms
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
        cls.user_one = User.objects.create_user(
            username='UserOne',
            first_name='ТестИмя',
            last_name='ТестФамилия',
            email='user_one@test.test',
        )
        cls.user_two = User.objects.create_user(
            username='UserTwo',
            email='user_two@test.test',
        )
        cls.author = User.objects.create_superuser(
            username='Author',
            email='author@test.test',
        )
        cls.post = []
        for number in range(20):
            post = Post.objects.create(
                title=f'Статья {number} для теста - заголовок',
                subheader=f'А это подзаголовок статьи {number}',
                text=f'Ну и сама статья {number} - она вот такая, короткая.',
                image=cls.uploaded if number == 19 else None
            )
            cls.post.append(post)

        cls.comment = Comment.objects.create(
            post=cls.post[-1],
            author=cls.user_one,
            comment_text='Небольшой комментарий к статье'
        )
        cls.comment2 = Comment.objects.create(
            post=cls.post[-1],
            author=cls.user_two,
            comment_text='Комментарий к статье от 2-го юзера'
        )
        cls.message = Message.objects.create(
            interlocutor=cls.user_one,
            direction='TO_AUTHOR',
            message_text='Маленькое сообщение автору'
        )
        cls.message2 = Message.objects.create(
            interlocutor=cls.user_two,
            direction='TO_AUTHOR',
            message_text='Сообщение от 2-го юзера'
        )
        cls.message_reply = Message.objects.create(
            interlocutor=cls.user_one,
            direction='FROM_AUTHOR',
            message_text='А это ответ на сообщение'
        )
        cls.like = Favourite.objects.create(
            liker=cls.user_one,
            favourite_post=cls.post[-1]
        )
        cls.like2 = Favourite.objects.create(
            liker=cls.user_one,
            favourite_post=cls.post[0]
        )
        cls.like3 = Favourite.objects.create(
            liker=cls.user_two,
            favourite_post=cls.post[-1]
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
        post = self.post[-1]
        templates_pages_names = [
            ('posts/index.html', reverse('index')),
            ('posts/post.html', reverse('post_view', args=[post.id])),
            ('posts/comments.html', reverse('comments', args=[post.id])),
            ('posts/my_comments.html', reverse('my_comments')),
            ('posts/favourite.html', reverse('favourite')),
            ('posts/messages.html', reverse('messages')),
            ('posts/private_cabinet.html', reverse('private_cabinet')),
            ('posts/post_management.html', reverse('post_management')),
            ('posts/new.html', reverse('new_post')),
            ('posts/new.html', reverse('post_update', args=[post.id])),
            ('posts/post_delete.html',
             reverse('post_delete', args=[post.id])),
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
        expected_post = self.post[-1]
        self.assertEqual(post.id, expected_post.id)
        self.assertEqual(post.title, expected_post.title)
        self.assertEqual(post.subheader, expected_post.subheader)
        self.assertEqual(post.image, self.jpg_url)
        self.assertEqual(post.comment_count(), expected_post.comment_count())
        self.assertEqual(post.like_count(), expected_post.like_count())

    def test_post_shows_correct_context(self):
        """В шаблон post передан правильный контекст."""
        expected_post = self.post[-1]
        response = self.guest_client.get(
            reverse('post_view', args=[expected_post.id]))
        post = response.context.get('post')
        also_list = response.context.get('also_list')
        self.assertEqual(post.id, expected_post.id)
        self.assertEqual(post.title, expected_post.title)
        self.assertEqual(post.subheader, expected_post.subheader)
        self.assertEqual(post.text, expected_post.text)
        self.assertEqual(post.image, self.jpg_url)
        self.assertEqual(post.pub_date, expected_post.pub_date)
        self.assertEqual(post.comment_count(), expected_post.comment_count())
        self.assertEqual(post.like_count(), expected_post.like_count())
        self.assertEqual(len(also_list), 3)
        self.assertNotIn(expected_post, also_list)
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)

    def test_comments_shows_correct_context(self):
        """В шаблон comments передан правильный контекст."""
        expected_post = self.post[-1]
        response = self.authorized_client.get(
            reverse('comments', args=[expected_post.id]))
        comment = response.context.get('page')[0]
        post = response.context.get('post')
        also_list = response.context.get('also_list')
        form_field = response.context.get('form').fields.get('comment_text')
        self.assertEqual(post, expected_post)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.created, self.comment.created)
        self.assertEqual(comment.comment_text, self.comment.comment_text)
        self.assertEqual(len(also_list), 3)
        self.assertNotIn(expected_post, also_list)
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
        self.assertIsInstance(form_field, forms.CharField)

    def test_private_cabinet_shows_correct_context(self):
        """В шаблон private-cabinet  передан правильный контекст."""
        response = self.authorized_client.get(reverse('private_cabinet'))
        user = response.context.get('user')
        also_list = response.context.get('also_list')
        self.assertEqual(user.first_name, self.user_one.first_name)
        self.assertEqual(user.last_name, self.user_one.last_name)
        self.assertEqual(user.username, self.user_one.username)
        self.assertEqual(user.email, self.user_one.email)
        self.assertEqual(len(also_list), 3)
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)

    def test_my_comments_shows_correct_context(self):
        """В шаблон my_comments  передан правильный контекст."""
        response = self.authorized_client.get(reverse('my_comments'))
        page = response.context.get('page')
        comment = page[0]
        also_list = response.context.get('also_list')
        expected_post = self.post[-1]
        self.assertEqual(len(page), 1)
        self.assertEqual(comment.post.id, expected_post.id)
        self.assertEqual(comment.post.title, expected_post.title)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.created, self.comment.created)
        self.assertEqual(comment.comment_text, self.comment.comment_text)
        self.assertEqual(len(also_list), 3)
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)

    def test_messages_shows_correct_context(self):
        """В шаблон messages передан правильный контекст."""
        response = self.authorized_client.get(reverse('messages'))
        page = response.context.get('page')
        message = page[0]
        also_list = response.context.get('also_list')
        form_field = response.context.get('form').fields.get('message_text')
        self.assertEqual(len(page), 2)
        self.assertNotIn(self.message2, page)
        self.assertEqual(message.direction, self.message.direction)
        self.assertEqual(message.message_text, self.message.message_text)
        self.assertEqual(message.send_time, self.message.send_time)
        self.assertEqual(len(also_list), 3)
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
        self.assertIsInstance(form_field, forms.CharField)

    def test_new_shows_correct_context(self):
        """В шаблон new передан правильный контекст."""
        response = self.author_client.get(reverse('new_post'))
        form_fields = response.context.get('form').fields
        fields_should_be = {
            'title': forms.CharField,
            'subheader': forms.CharField,
            'text': forms.CharField,
            'image': forms.ImageField,
        }
        for field, expected in fields_should_be.items():
            with self.subTest(field=field):
                self.assertIsInstance(form_fields.get(field), expected)

    def test_post_management_shows_correct_context(self):
        """В шаблон post_management передан правильный контекст."""
        response = self.author_client.get(reverse('post_management'))
        post = response.context.get('page')[0]
        expected_post = self.post[-1]
        also_list = response.context.get('also_list')
        self.assertEqual(post.id, expected_post.id)
        self.assertEqual(post.title, expected_post.title)
        self.assertEqual(post.subheader, expected_post.subheader)
        self.assertEqual(post.image, self.jpg_url)
        self.assertEqual(post.comment_count(), expected_post.comment_count())
        self.assertEqual(post.like_count(), expected_post.like_count())
        for post in also_list:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)

    def test_message_reply_shows_correct_context(self):
        """В шаблон message_reply передан правильный контекст."""
        response = self.author_client.get(reverse('message_reply'))
        dialogs = response.context.get('interlocutors')
        self.assertEqual(dialogs, [self.user_one, self.user_two])

    def test_post_index_cache_works(self):
        """Проверяем работу кэша"""
        cache.clear()
        post = Post.objects.create(
            title='Статья для тестирования кэша',
            subheader='А это подзаголовок статьи',
            text='Ну и сама статья.',
        )
        response1 = str(
            self.author_client.get(reverse('index')).content
        )
        post.delete()
        response2 = str(
            self.author_client.get(reverse('index')).content
        )
        self.assertEqual(response1, response2)
        cache.clear()
        response3 = str(
            self.author_client.get(reverse('index')).content
        )
        self.assertNotEqual(response1, response3)
