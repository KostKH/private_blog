from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Comment, Favourite, Message, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_one = User.objects.create_user(username='UserOne')
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
            favourite_post=cls.post
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_one)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_urls_are_available_for_guest(self):
        """Проверка доступности страниц из списка
        неавторизованному пользователю."""
        urls_for_guest = [
            ('/', 200),
            ('/about/', 200),
            ('/auth/login/', 200),
            ('/auth/signup/', 200),
            (f'/{self.post.id}/', 200),
            (f'/{self.post.id}/comments/', 200),
            (f'/{self.post.id}/comments/add_comment/', 302),
            (f'/{self.post.id}/like/', 302),
            ('/private-cabinet/', 302),
            ('/favourite/', 302),
            ('/my-comments/', 302),
            ('/messages/', 302),
            ('/messages/add_message/', 302),
            ('/post-management/', 302),
            ('/new/', 302),
            (f'/post-management/{self.post.id}/delete/', 302),
            (f'/post-management/{self.post.id}/update/', 302),
            ('/message-reply/', 302),
            (f'/message-reply/{self.user_one.id}/', 302),
            ('/post-management/', 302),
        ]
        for each_url, code in urls_for_guest:
            with self.subTest(each_url=each_url):
                response = self.guest_client.get(each_url)
                self.assertEqual(response.status_code, code,
                                 f'проверьте {each_url}')

    def test_urls_for_authorized_are_available(self):
        """Проверка доступности страниц из
        списка авторизованному пользователю."""
        urls_for_authorized = [
            (f'/{self.post.id}/comments/add_comment/', 302),
            (f'/{self.post.id}/like/', 302),
            ('/private-cabinet/', 200),
            ('/favourite/', 200),
            ('/my-comments/', 200),
            ('/messages/', 200),
            ('/messages/add_message/', 302),
            ('/post-management/', 302),
            ('/new/', 302),
            (f'/post-management/{self.post.id}/delete/', 302),
            (f'/post-management/{self.post.id}/update/', 302),
            ('/message-reply/', 302),
            (f'/message-reply/{self.user_one.id}/', 302),
            ('/post-management/', 302),
        ]
        for each_url, code in urls_for_authorized:
            with self.subTest(each_url=each_url):
                response = self.authorized_client.get(each_url)
                self.assertEqual(response.status_code, code,
                                 f'проверьте {each_url}')

    def test_urls_for_author_are_available(self):
        """Проверка доступности страниц из списка автору."""
        urls_for_author = [
            ('/post-management/', 200),
            ('/new/', 200),
            (f'/post-management/{self.post.id}/delete/', 200),
            (f'/post-management/{self.post.id}/update/', 200),
            ('/message-reply/', 200),
            (f'/message-reply/{self.user_one.id}/', 200),
            ('/post-management/', 200),
        ]
        for each_url, code in urls_for_author:
            with self.subTest(each_url=each_url):
                response = self.author_client.get(each_url)
                self.assertEqual(response.status_code, code,
                                 f'проверьте {each_url}')

    def test_urls_use_correct_template_for_guest(self):
        """Проверка на правильность используемого шаблона
        для страниц из словаря, когда к ним обращается
        неавторизованный пользователь."""
        templates_url_names = [
            ('/', 'posts/index.html'),
            ('/about/', 'posts/about.html'),
            ('/auth/login/', 'users/login.html'),
            ('/auth/signup/', 'users/signup.html'),
            (f'/{self.post.id}/', 'posts/post.html'),
            (f'/{self.post.id}/comments/', 'posts/comments.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                cache.clear()
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_use_correct_template_for_authorized(self):
        """Проверка на правильность используемого шаблона
        для страниц из словаря, когда к ним обращается
        авторизованный пользователь."""
        templates_url_names = [
            ('/private-cabinet/', 'posts/private_cabinet.html'),
            ('/favourite/', 'posts/favourite.html'),
            ('/my-comments/', 'posts/my_comments.html'),
            ('/messages/', 'posts/messages.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_use_correct_template_for_author(self):
        """Проверка на правильность используемого шаблона
        для страниц из словаря, когда к ним обращается
        автор."""
        templates_url_names = [
            ('/post-management/', 'posts/post_management.html'),
            (f'/post-management/{self.post.id}/delete/',
             'posts/post_delete.html'),
            ('/my-comments/', 'posts/my_comments.html'),
            ('/messages/', 'posts/messages.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_guest_correctly(self):
        """Проверяем для страниц из словаря, что неавторизованный
        пользователь переадресуется на нужную страницу."""
        url_redirects = [
            ('/private-cabinet/', '/auth/login/?next=/private-cabinet/'),
            ('/favourite/', '/auth/login/?next=/favourite/'),
            ('/my-comments/', '/auth/login/?next=/my-comments/'),
            ('/messages/', '/auth/login/?next=/messages/'),
            ('/new/', '/auth/login/?next=/new/'),
            ('/post-management/', '/auth/login/?next=/post-management/'),
            ('/message-reply/', '/auth/login/?next=/message-reply/'),
            (f'/message-reply/{self.user_one.id}/',
             f'/auth/login/?next=/message-reply/{self.user_one.id}/'),
            ('/admin/', '/admin/login/?next=/admin/'),
            (f'/{self.post.id}/like/',
             f'/auth/login/?next=/{self.post.id}/like/')
        ]
        for address, redir in url_redirects:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redir)

    def test_urls_redirect_athorized_correctly(self):
        """Проверяем что авторизованный пользователь
        переадресуется на нужную страницу."""
        url_redirects = [
            (f'/{self.post.id}/like/', f'/{self.post.id}/'),
            (f'/{self.post.id}/comments/add_comment/',
             f'/{self.post.id}/comments/'),
            ('/messages/add_message/', '/messages/'),
        ]
        for address, redir in url_redirects:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(response, redir)

    def test_urls_redirect_author_correctly(self):
        """Проверяем что автор переадресуется на нужную страницу."""
        url_redirects = [
            (f'/message-reply/{self.user_one.id}/add_reply/',
             f'/message-reply/{self.user_one.id}/')
        ]
        for address, redir in url_redirects:
            with self.subTest(address=address):
                response = self.author_client.get(address, follow=True)
                self.assertRedirects(response, redir)
