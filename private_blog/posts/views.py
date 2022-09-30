from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, MessageForm, PostForm
from .models import Comment, Favourite, Message, Post
from .utilities import get_also_list, is_staff_check

User = get_user_model()


@cache_page(5)
def index(request):
    """Функция возвращает объект класса BaseManager (результат SQL-запроса)
    со статьями из БД Posts и возвращает сгенерированную страницу."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def post_view(request, post_id):
    """Функция отбирает нужную статью из базы и
     возвращает сгенерированную страницу."""
    post = get_object_or_404(Post, id=post_id)
    also_list = get_also_list(post_id)
    context = {
        'post': post,
        'also_list': also_list
    }
    return render(request, 'posts/post.html', context)


def comments(request, post_id):
    """Функция отбирает из базы комментарии к статье
     и возвращает сгенерированную страницу."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comment_list = Comment.objects.filter(post=post)
    paginator = Paginator(comment_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    also_list = get_also_list(post_id)
    context = {
        'post': post,
        'page': page,
        'form': form,
        'also_list': also_list,
    }
    return render(request, 'posts/comments.html', context)


@login_required
def my_comments(request):
    """Функция отбирает все комментарии пользователя из базы
     и возвращает сгенерированную страницу."""
    comment_list = Comment.objects.filter(
        author=request.user,
    ).order_by('-post', 'id')
    paginator = Paginator(comment_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    also_list = get_also_list()
    context = {
        'page': page,
        'also_list': also_list,
    }
    return render(request, 'posts/my_comments.html', context)


@login_required
def add_comment(request, post_id):
    """Функция генерит форму для создания нового комментария,
    получает данные из формы и сохраняет в базе данных."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comm = form.save(commit=False)
        comm.author = request.user
        comm.post = post
        comm.save()
    return redirect('comments', post_id)


@login_required
def like(request, post_id):
    """Функция добавляет/удаляет в базе данных
    лайк от пользователя к конкретной статье"""
    liker = request.user
    post = get_object_or_404(Post, id=post_id)
    if Favourite.objects.filter(liker=liker, favourite_post=post).exists():
        post_like = get_object_or_404(
            Favourite,
            liker=liker,
            favourite_post=post,
        )
        post_like.delete()
    else:
        Favourite.objects.create(liker=liker, favourite_post=post)
    return redirect('post_view', post_id=post.id)


@login_required
def favourite(request):
    """Функция отбирает в БД все статьи, которые лайкнул данный
    пользователь, и возвращает сгенерированную страницу."""
    post_list = Post.objects.filter(favourites__liker=request.user)
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    also_list = Post.objects.exclude(favourites__liker=request.user)[:3]
    context = {
        'page': page,
        'also_list': also_list
    }
    return render(request, 'posts/favourite.html', context)


@login_required
def messages(request):
    """Функция отбирает из базы все сообщения из диалога пользователя
     с автором и возвращает сгенерированную страницу."""
    form = MessageForm(request.POST or None)
    message_list = Message.objects.filter(interlocutor=request.user)
    paginator = Paginator(message_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    also_list = get_also_list()
    context = {
        'page': page,
        'form': form,
        'also_list': also_list,
        'other_side': 'FROM_AUTHOR',
    }
    return render(request, 'posts/messages.html', context)


@login_required
def add_message(request):
    """Функция генерит форму для создания нового сообщения,
    получает данные из формы и сохраняет в базе данных."""
    form = MessageForm(request.POST or None)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.interlocutor = request.user
        msg.direction = 'TO_AUTHOR'
        msg.save()
    return redirect('messages')


@login_required
def private_cabinet(request):
    """Функция возвращает сгенерированную страницу
    личного кабинета (раздел 'Учетные данные')."""
    also_list = get_also_list()
    context = {
        'also_list': also_list,
    }
    return render(request, 'posts/private_cabinet.html', context)


@user_passes_test(is_staff_check)
def post_management(request):
    """Функция отбирает все статьи из базы и
    возвращает страницу управления статьями
    (изменение, добавление, удаление статей)"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    also_list = get_also_list()
    context = {
        'page': page,
        'also_list': also_list
    }
    return render(request, 'posts/post_management.html', context)


@user_passes_test(is_staff_check)
def new_post(request):
    """Функция генерит форму для создания новой статьи,
    получает данные из формы и сохраняет в базе данных."""
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/new.html', {'form': form})
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('post_management')
    return render(request, 'posts/new.html', {'form': form})


@user_passes_test(is_staff_check)
def post_update(request, post_id):
    """Функция генерит форму для изменения статьи,
    получает данные из формы и сохраняет в базе данных."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        updated_post = form.save()
        updated_post.modify_date = datetime.now().date()
        updated_post.save()
        return redirect('post_management')
    context = {
        'form': form,
        'edit': True,
    }
    return render(request, 'posts/new.html', context)


@user_passes_test(is_staff_check)
def post_delete(request, post_id):
    """Функция обрабатывает запрос на удаление статьи из базы."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('post_management')
    return render(request, 'posts/post_delete.html', {'post': post, })


@user_passes_test(is_staff_check)
def message_reply(request, chosen_user_id=None):
    """Функция отбирает всех пользователей, писавших автору,
    по выбранному пользователю отбирает сообщения и
    и возвращает сгенерированную страницу."""
    form = MessageForm(request.POST or None)
    interlocutors = []
    message_list = []
    also_list = get_also_list()
    messages = Message.objects.all()
    if messages:
        interlocutor_ids = messages.order_by().values(
            'interlocutor'
        ).distinct()
        for item in interlocutor_ids:
            interlocutor = User.objects.get(id=item['interlocutor'])
            interlocutors.append(interlocutor)
        if chosen_user_id:
            chosen_user = get_object_or_404(User, id=chosen_user_id)
            message_list = Message.objects.filter(interlocutor=chosen_user)
    paginator = Paginator(message_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'form': form,
        'interlocutors': interlocutors,
        'also_list': also_list,
        'other_side': 'TO_AUTHOR',
    }
    if chosen_user_id:
        context['chosen_user'] = chosen_user
    return render(request, 'posts/message_reply.html', context)


@user_passes_test(is_staff_check)
def add_reply(request, chosen_user_id):
    """Функция генерит форму для создания ответа пользователю от автора,
    получает данные из формы и сохраняет в базе данных."""
    form = MessageForm(request.POST or None)
    chosen_user = get_object_or_404(User, id=chosen_user_id)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.interlocutor = chosen_user
        msg.direction = 'FROM_AUTHOR'
        msg.save()
    return redirect('message_reply_id', chosen_user_id)


def page_not_found(request, exception=None):
    """Функция возвращает сгенерированную страницу для ошибки 404."""
    return render(
        request,
        "posts/misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Функция возвращает сгенерированную страницу для ошибки 500."""
    return render(request, "posts/misc/500.html", status=500)
