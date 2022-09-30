from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, UserUpdateForm

User = get_user_model()


class SignUp(CreateView):
    """Класс обрабатывает данные из формы регистрации пользователя,
    возвращает страницу с формой для регистрации,
    после регистрации перенаправляет на страницу входа"""

    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = "users/signup.html"


@login_required
def user_update(request):
    """Функция генерит форму для изменения данных пользователя,
    получает данные из формы и сохраняет в базе данных."""
    if request.method != 'POST':
        form = UserUpdateForm(instance=request.user)
        return render(request, 'users/user_update.html', {'form': form})
    form = UserUpdateForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('private_cabinet')
    return render(request, 'users/user_update.html', {'form': form})
