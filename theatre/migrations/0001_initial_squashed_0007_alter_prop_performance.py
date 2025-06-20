# Generated by Django 4.2.9 on 2024-11-27 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import theatre.models


class Migration(migrations.Migration):

    replaces = [('theatre', '0001_initial'), ('theatre', '0002_initial'), ('theatre', '0003_rename_genre_play_genres'), ('theatre', '0004_alter_performance_show_time'), ('theatre', '0005_alter_ticket_performance_alter_ticket_reservaion'), ('theatre', '0006_rename_reservaion_ticket_reservation'), ('theatre', '0007_alter_prop_performance')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TheatreHall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rows', models.IntegerField()),
                ('seats_in_row', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(null=True, upload_to=theatre.models.play_image_file_path)),
                ('actors', models.ManyToManyField(blank=True, to='theatre.actor')),
                ('genres', models.ManyToManyField(blank=True, to='theatre.genre')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_time', models.DateTimeField()),
                ('play', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theatre.play')),
                ('theatre_hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theatre.theatrehall')),
            ],
            options={
                'ordering': ['-show_time'],
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField()),
                ('seat', models.IntegerField()),
                ('performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='theatre.performance')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='theatre.reservation')),
            ],
            options={
                'ordering': ['row', 'seat'],
                'unique_together': {('row', 'seat', 'performance')},
            },
        ),
        migrations.CreateModel(
            name='Prop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('performance', models.ManyToManyField(blank=True, related_name='props', to='theatre.performance')),
            ],
        ),
    ]
