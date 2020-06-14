from django.apps import apps
from django.db import migrations, models


def add_factions(apps, schema_editor):
    Faction = apps.get_model('trainerdex', 'Faction')
    for i in range(1,4):
        Faction.objects.get_or_create(id=i)

class Migration(migrations.Migration):

    dependencies = [
        ('trainerdex', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainer',
            name='id',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='(Deprecated) ID'),
        ),
        migrations.RunPython(add_factions, migrations.RunPython.noop),
    ]
