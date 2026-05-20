"""Регистрация моделей сотрудников в Django admin."""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from apps.accounts.models import User


class UserChangeForm(forms.ModelForm):
    """Edit user data and optionally replace ESP32 PIN."""

    password = ReadOnlyPasswordHashField(label="Пароль")
    pin = forms.CharField(label="ESP32 PIN", required=False, help_text="До 10 цифр. Пусто: не менять PIN.")

    class Meta:
        model = User
        fields = "__all__"

    def clean_pin(self) -> str:
        pin = self.cleaned_data.get("pin", "")
        try:
            User.normalize_pin(pin)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        if pin:
            pin_hash = User.hash_pin(pin)
            if User.objects.exclude(pk=self.instance.pk).filter(pin_hash=pin_hash).exists():
                raise forms.ValidationError("Такой PIN уже используется")
        return pin

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        pin = self.cleaned_data.get("pin", "")
        if pin:
            user.set_pin(pin)
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserCreationForm(forms.ModelForm):
    """Create users with optional admin password and optional ESP32 PIN."""

    password1 = forms.CharField(label="Пароль", required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", required=False, widget=forms.PasswordInput)
    pin = forms.CharField(label="ESP32 PIN", required=False, help_text="До 10 цифр.")

    class Meta:
        model = User
        fields = ("username", "full_name", "is_staff", "is_superuser", "groups")

    def clean_pin(self) -> str:
        pin = self.cleaned_data.get("pin", "")
        try:
            User.normalize_pin(pin)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        if pin and User.objects.filter(pin_hash=User.hash_pin(pin)).exists():
            raise forms.ValidationError("Такой PIN уже используется")
        return pin

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.set_pin(self.cleaned_data.get("pin", ""))
        if commit:
            user.save()
            self.save_m2m()
        return user


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка кастомной модели пользователя."""

    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("id", "username", "full_name", "has_pin", "is_active", "is_staff")
    list_filter = ("groups", "is_active", "is_staff")
    search_fields = ("username", "full_name")
    ordering = ("username",)
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональные данные", {"fields": ("full_name",)}),
        ("ESP32", {"fields": ("pin",)}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "full_name",
                    "pin",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    @admin.display(boolean=True, description="ESP32 PIN")
    def has_pin(self, obj: User) -> bool:
        return bool(obj.pin_hash)
