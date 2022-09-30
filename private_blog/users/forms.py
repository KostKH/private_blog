from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Класс генерит форму регистрации нового пользователя."""

    class Meta(UserCreationForm.Meta):

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class UserUpdateForm(UserChangeForm):
    """Класс генерит форму для изменения данных пользователя."""

    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email']
