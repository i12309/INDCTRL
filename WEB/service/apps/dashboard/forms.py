"""Формы web-интерфейса INDCTRL."""

from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """Форма входа без выбора роли.

    Роль берется из БД после успешной проверки пароля, чтобы пользователь не мог
    влиять на доступ выбором значения в форме.
    """

    def __init__(self, request=None, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
