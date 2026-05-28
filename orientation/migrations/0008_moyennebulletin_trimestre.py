from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orientation', '0007_alter_concours_etablissement'),
    ]

    operations = [
        migrations.AddField(
            model_name='moyennebulletin',
            name='trimestre',
            field=models.CharField(
                max_length=2,
                choices=[('T1', 'Trimestre 1'), ('T2', 'Trimestre 2'), ('T3', 'Trimestre 3')],
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='moyennebulletin',
            unique_together={('profil_bachelier', 'matiere', 'classe', 'trimestre')},
        ),
    ]