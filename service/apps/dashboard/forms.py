"""Формы web-интерфейса INDCTRL."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.accounts.models import Role


class RoleLoginForm(AuthenticationForm):
    """Форма входа с выбором роли пользователя."""

    role = forms.ChoiceField(label="Роль")

    def __init__(self, request=None, *args, **kwargs) -> None:
        """Заполнить список активных ролей из справочника."""

        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"
        self.fields["role"].choices = [
            (role.code, role.name) for role in Role.objects.filter(is_active=True).order_by("code")
        ]
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def confirm_login_allowed(self, user) -> None:
        """Проверить активность пользователя и совпадение выбранной роли."""

        super().confirm_login_allowed(user)
        selected_role = self.cleaned_data.get("role")
        actual_role = getattr(getattr(user, "role", None), "code", None)
        if not user.is_superuser and actual_role != selected_role:
            raise forms.ValidationError("Выбранная роль не соответствует пользователю.")
