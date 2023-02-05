import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import CommentForm, MessageForm, PostForm
from posts.models import Comment, Message, Post, User


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.post_form = PostForm()
        cls.comment_form = CommentForm()
        cls.comment_form = MessageForm()
        cls.small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=cls.small_jpg,
            content_type='image/gif'
        )
        cls.img_url = 'posts/small.jpg'

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
        cls.post = Post.objects.create(
            title='Статья для теста - заголовок',
            subheader='А это подзаголовок статьи',
            text='Ну и сама статья - она вот такая, короткая.',
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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_one)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'title': 'Новый заголовок',
            'subheader': 'Новый подзаголовок',
            'text': 'Новый текст',
            'image': self.uploaded,
        }
        response = self.author_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post_management'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.filter(
            title=form_data['title'],
            subheader=form_data['subheader'],
            text=form_data['text'],
        ).order_by('-id').first()
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.title, form_data['title'])
        self.assertEqual(new_post.subheader, form_data['subheader'])
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.image, self.img_url)

    def test_edit_post(self):
        """Проверяем, что при редактировании пост изменился."""
        post_id = self.post.id
        form_data = {
            'title': 'Измененный заголовок',
            'subheader': 'Измененный подзаголовок',
            'text': 'Измененный текст статьи'
        }
        self.author_client.post(
            reverse('post_update', args=[post_id]),
            data=form_data,
            follow=True
        )
        modified_post = Post.objects.filter(id=post_id).first()
        self.assertEqual(modified_post.title, form_data['title'])
        self.assertEqual(modified_post.subheader, form_data['subheader'])
        self.assertEqual(modified_post.text, form_data['text'])

    def test_non_author_cannot_create_post(self):
        """Не-автор не может создать пост."""
        post_count = Post.objects.count()
        redir = reverse('login') + '?next=' + reverse('new_post')
        form_data = {
            'title': 'Новый заголовок',
            'subheader': 'Новый подзаголовок',
            'text': 'Новый текст',
        }
        response_guest = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        response_authorized = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_guest, redir)
        self.assertRedirects(response_authorized, redir)
        self.assertEqual(Post.objects.count(), post_count)

    def test_non_author_cannot_edit_post(self):
        """Не-автор не может редактировать пост."""
        redir = (reverse('login') + '?next=' + reverse('post_update',
                 args=[self.post.id]))
        post_id = self.post.id
        form_data = {
            'title': 'Измененный не-автором заголовок',
            'subheader': 'Измененный не-автором подзаголовок',
            'text': 'Измененный не-автором текст статьи'
        }
        response_guest = self.guest_client.post(
            reverse('post_update', args=[post_id]),
            data=form_data,
            follow=True
        )
        response_authorized = self.guest_client.post(
            reverse('post_update', args=[post_id]),
            data=form_data,
            follow=True
        )
        check_post = Post.objects.filter(id=post_id).first()
        self.assertRedirects(response_guest, redir)
        self.assertRedirects(response_authorized, redir)
        self.assertNotEqual(check_post.title, form_data['title'])
        self.assertNotEqual(check_post.subheader, form_data['subheader'])
        self.assertNotEqual(check_post.text, form_data['text'])

    def test_create_comment(self):
        """Авторизованный пользователь
        может создать комментарий."""
        comm_count = Comment.objects.count()
        post_id = self.post.id
        form_data = {'comment_text': 'Текст нового комментария'}
        response = self.authorized_client.post(
            reverse('add_comment', args=[post_id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('comments', args=[post_id]))
        self.assertEqual(Comment.objects.count(), comm_count + 1)
        new_comm = Comment.objects.filter(
            comment_text=form_data['comment_text'],
            author=self.user_one,
            post=self.post
        ).order_by('-id').first()
        self.assertIsNotNone(new_comm)
        self.assertEqual(new_comm.comment_text, form_data['comment_text'])
        self.assertEqual(new_comm.author, self.user_one)
        self.assertEqual(new_comm.post, self.post)

    def test_guest_cannot_post_comment(self):
        """Гость не может создавать комментарии."""
        post_id = self.post.id
        comm_count = Comment.objects.count()
        redir = (reverse('login') + '?next=' + reverse('add_comment',
                 args=[post_id]))
        form_data = {'comment_text': 'комментарий от гостя'}
        response = self.guest_client.post(
            reverse('add_comment', args=[post_id]),
            data=form_data,
            follow=True
        )
        check_existance = Comment.objects.filter(
            comment_text=form_data['comment_text'],
            post=PostsFormTests.post
        ).exists()
        self.assertEqual(Comment.objects.count(), comm_count)
        self.assertFalse(check_existance)
        self.assertRedirects(response, redir)

    def test_create_message(self):
        """Авторизованный пользователь
        может написать сообщение автору."""
        msg_count = Message.objects.count()
        form_data = {'message_text': 'Текст нового сообщения'}
        response = self.authorized_client.post(
            reverse('add_message'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('messages'))
        self.assertEqual(Message.objects.count(), msg_count + 1)
        new_msg = Message.objects.filter(
            message_text=form_data['message_text'],
            interlocutor=self.user_one,
        ).order_by('-id').first()
        self.assertIsNotNone(new_msg)
        self.assertEqual(new_msg.message_text, form_data['message_text'])
        self.assertEqual(new_msg.interlocutor, self.user_one)
        self.assertEqual(new_msg.direction, 'TO_AUTHOR')

    def test_guest_cannot_post_comment(self):
        """Гость не может создавать комментарии."""
        msg_count = Comment.objects.count()
        redir = (reverse('login') + '?next=' + reverse('add_message'))
        form_data = {'message_text': 'сообщение от гостя'}
        response = self.guest_client.post(
            reverse('add_message'),
            data=form_data,
            follow=True
        )
        check_existance = Message.objects.filter(
            message_text=form_data['message_text'],
        ).exists()
        self.assertEqual(Message.objects.count(), msg_count)
        self.assertFalse(check_existance)
        self.assertRedirects(response, redir)
