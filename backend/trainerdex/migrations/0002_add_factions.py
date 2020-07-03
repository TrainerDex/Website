from django.db import migrations

def add_factions(apps, schema_editor):
    Faction = apps.get_model('trainerdex', 'Faction')
    Faction.objects.bulk_create([Faction(id=i) for i in range(0,4)], ignore_conflicts=True)

class Migration(migrations.Migration):

    dependencies = [
        ('trainerdex', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_factions, migrations.RunPython.noop),
    ]
