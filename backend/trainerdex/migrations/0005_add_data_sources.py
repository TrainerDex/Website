from django.db import migrations

def add_data_sources(apps, schema_editor):
    
    DATABASE_SOURCES = (
        ('com.discord', 'Discord'),
        ('com.discord:register', 'Discord (Registration)'),
        ('com.facebook', 'Facebook'),
        ('com.nianticlabs.pokemongo.social', "Niantic Social"),
        ('com.pkmngots:import', "Third Saturday"),
        ('com.pokeassistant.trainerstats', "Poké Assistant"),
        ('com.pokenavbot.profiles', "PokeNav"),
        ('com.tl40data', "TL40 Data Team"),
        ('com.tl40data:legacy', "TL40 Data Team (Legacy)"),
        ('com.trainerdex:web', 'Website'),
        ('com.trainerdex:web:register', 'Registration'),
        ('com.twitter', 'Twitter'),
        ('com.youtube', 'YouTube'),
    )
    
    DataSource = apps.get_model('trainerdex', 'DataSource')
    
    for x,y in DATABASE_SOURCES:
        DataSource.objects.update_or_create(
            slug=x,
            defaults={'verbose_name': y},
        )

class Migration(migrations.Migration):

    dependencies = [
        ('trainerdex', '0004_auto_20200701_0954'),
    ]

    operations = [
        migrations.RunPython(add_data_sources, migrations.RunPython.noop),
    ]
