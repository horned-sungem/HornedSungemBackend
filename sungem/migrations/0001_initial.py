# Generated by Django 3.1.1 on 2020-09-30 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('nr', models.CharField(max_length=20)),
                ('cp', models.SmallIntegerField()),
                ('workload', models.SmallIntegerField()),
                ('self_study', models.SmallIntegerField()),
                ('duration', models.SmallIntegerField()),
                ('wise', models.BooleanField()),
                ('sose', models.BooleanField()),
                ('language', models.CharField(max_length=30)),
                ('learning_content', models.TextField(max_length=5000)),
                ('qualification', models.TextField(max_length=5000)),
                ('requirements', models.TextField(max_length=5000)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.SmallIntegerField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sungem.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('user', 'module'), name='unique_vote'),
        ),
    ]
