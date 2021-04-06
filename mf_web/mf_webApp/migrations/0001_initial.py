# Generated by Django 3.1.7 on 2021-04-01 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient', models.CharField(max_length=50)),
                ('study_desc', models.CharField(max_length=50)),
                ('series_desc', models.CharField(max_length=50)),
                ('series_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Curve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone', models.CharField(max_length=12)),
                ('area_rest', models.FloatField()),
                ('peak_rest', models.FloatField()),
                ('slope_rest', models.FloatField()),
                ('area_stress', models.FloatField()),
                ('peak_stress', models.FloatField()),
                ('slope_stress', models.FloatField()),
                ('coefficent', models.FloatField()),
                ('id_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mf_webApp.patient')),
            ],
        ),
    ]
