# Generated manually for INDCTRL quality percent migration.

from django.db import migrations, models
from django.db.models import Q


def migrate_detail_quality(apps, _schema_editor):
    """Перенести старые состояния деталей в процент качества."""

    detail_model = apps.get_model("production", "Detail")
    detail_model.objects.filter(detail_state__code="working").update(quality_percent=100)
    detail_model.objects.filter(detail_state__code="defect").update(quality_percent=0)
    detail_model.objects.filter(detail_state__code="undefined").update(quality_percent=0)


class Migration(migrations.Migration):
    """Заменить справочник состояний детали числовым процентом качества."""

    dependencies = [
        ("production", "0002_seed_detail_states"),
    ]

    operations = [
        migrations.AddField(
            model_name="detail",
            name="quality_percent",
            field=models.PositiveSmallIntegerField(default=100, verbose_name="качество, %"),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_detail_quality, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="detail",
            name="detail_state",
        ),
        migrations.DeleteModel(
            name="DetailState",
        ),
        migrations.AddConstraint(
            model_name="detail",
            constraint=models.CheckConstraint(
                check=Q(quality_percent__gte=0) & Q(quality_percent__lte=100),
                name="detail_quality_percent_between_0_and_100",
            ),
        ),
    ]
