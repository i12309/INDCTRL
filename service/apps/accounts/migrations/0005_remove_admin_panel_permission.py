# Generated manually for INDCTRL access cleanup.

from django.db import migrations


def remove_admin_panel_permission(apps, _schema_editor):
    """Удалить устаревшее бизнес-право входа в admin.

    Вход в Django admin теперь определяется стандартным `is_staff`, а доступ к
    разделам - стандартными model permissions.
    """

    permission_model = apps.get_model("auth", "Permission")
    permission_model.objects.filter(
        content_type__app_label="accounts",
        codename="use_admin_panel",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_groups_permissions_remove_roles"),
    ]

    operations = [
        migrations.RunPython(remove_admin_panel_permission, migrations.RunPython.noop),
    ]
