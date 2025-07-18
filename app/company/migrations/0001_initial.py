# Generated by Django 5.2.3 on 2025-06-30 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=100)),
                ('industry', models.CharField(max_length=100)),
                ('founded_year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_type', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=100)),
                ('ceo_name', models.CharField(max_length=255)),
                ('headquarters', models.CharField(max_length=255)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='company.company')),
            ],
        ),
        migrations.CreateModel(
            name='FinancialData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('revenue', models.BigIntegerField()),
                ('net_income', models.BigIntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financials', to='company.company')),
            ],
        ),
    ]
