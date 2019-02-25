# Generated by Django 2.1 on 2018-08-15 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('doi', models.CharField(max_length=80, primary_key=True, serialize=False)),
                ('cid', models.CharField(default='', max_length=80, unique=True)),
                ('keywords', models.TextField(default='', null=True)),
                ('venue', models.CharField(default='', max_length=512, null=True)),
                ('title', models.TextField(default='', null=True)),
                ('author', models.TextField(null=True)),
                ('abstract', models.TextField(null=True)),
                ('keyphrases', models.TextField(null=True)),
                ('crawl_cite_state', models.CharField(default=0, max_length=2, null=True)),
                ('crawl_cited_state', models.CharField(default=0, max_length=2, null=True)),
                ('self_cite_num', models.CharField(max_length=10, null=True)),
                ('cited_num', models.CharField(max_length=10, null=True)),
                ('download_state', models.CharField(default=0, max_length=2, null=True)),
                ('pdf_save_path', models.TextField(default='', null=True)),
            ],
            options={
                'db_table': 'papers',
            },
        ),
        migrations.CreateModel(
            name='Cite',
            fields=[
                ('doi', models.ForeignKey(max_length=80, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='+', serialize=False, to='simranking.Paper')),
            ],
            options={
                'db_table': 'cite',
            },
        ),
        migrations.AlterUniqueTogether(
            name='paper',
            unique_together={('doi', 'cid')},
        ),
        migrations.AddField(
            model_name='cite',
            name='cid',
            field=models.ForeignKey(max_length=80, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='simranking.Paper', to_field='cid'),
        ),
    ]
