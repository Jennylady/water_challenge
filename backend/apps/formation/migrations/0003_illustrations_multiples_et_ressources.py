from django.db import migrations, models
import django.db.models.deletion
import uuid


def migrer_images_existantes(apps, schema_editor):
    Illustration = apps.get_model('formation', 'IllustrationModule')
    ImageIllustration = apps.get_model('formation', 'ImageIllustrationModule')
    for illustration in Illustration.objects.exclude(image=''):
        if illustration.image:
            ImageIllustration.objects.create(
                illustration_id=illustration.pk,
                image=illustration.image,
                ordre=1,
            )


class Migration(migrations.Migration):
    dependencies = [('formation', '0002_alter_progressionmodule_est_termine')]

    operations = [
        migrations.AddField(
            model_name='illustrationmodule',
            name='titre',
            field=models.CharField(default='Illustration', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='illustrationmodule',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ImageIllustrationModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('image', models.FileField(help_text="Image appartenant à l'illustration", upload_to='formation/modules/illustrations/')),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('illustration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='formation.illustrationmodule')),
            ],
            options={
                'verbose_name': "Image d'illustration",
                'verbose_name_plural': "Images d'illustration",
                'db_table': 'formation_image_illustration_module',
                'ordering': ['ordre', 'id'],
            },
        ),
        migrations.CreateModel(
            name='RessourceModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='formation/modules/ressources/')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ressources', to='formation.module')),
            ],
            options={
                'verbose_name': 'Ressource de module',
                'verbose_name_plural': 'Ressources de module',
                'db_table': 'formation_ressource_module',
            },
        ),
        migrations.RunPython(migrer_images_existantes, migrations.RunPython.noop),
        migrations.RemoveField(model_name='illustrationmodule', name='image'),
        migrations.RemoveField(model_name='illustrationmodule', name='legende'),
        migrations.AlterModelOptions(
            name='illustrationmodule',
            options={'ordering': ['ordre', 'id'], 'verbose_name': 'Illustration de module', 'verbose_name_plural': 'Illustrations de module'},
        ),
    ]
