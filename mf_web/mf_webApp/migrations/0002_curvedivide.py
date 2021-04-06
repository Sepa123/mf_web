# Generated by Django 3.1.7 on 2021-04-03 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mf_webApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurveDivide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone', models.CharField(max_length=12)),
                ('partition', models.IntegerField()),
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
