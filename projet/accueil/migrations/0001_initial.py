# Generated manually to match current models

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnneeScolaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=20, unique=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'annees_scolaires',
            },
        ),
        migrations.CreateModel(
            name='Classe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True)),
                ('niveau', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'classes',
            },
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_utilisateur', models.CharField(max_length=50, unique=True)),
                ('mot_de_passe', models.CharField(max_length=255)),
                ('role', models.CharField(default='administrateur', max_length=30)),
            ],
            options={
                'db_table': 'utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='Eleve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricule', models.CharField(max_length=30, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('sexe', models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin')], max_length=1)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('annee_scolaire', models.ForeignKey(db_column='annee_scolaire_id', on_delete=django.db.models.deletion.PROTECT, to='accueil.anneescolaire')),
                ('classe', models.ForeignKey(db_column='classe_id', on_delete=django.db.models.deletion.PROTECT, to='accueil.classe')),
            ],
            options={
                'db_table': 'eleves',
            },
        ),
        migrations.CreateModel(
            name='Matiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('coefficient', models.DecimalField(decimal_places=2, max_digits=4)),
                ('classe', models.ForeignKey(db_column='classe_id', on_delete=django.db.models.deletion.PROTECT, to='accueil.classe')),
            ],
            options={
                'db_table': 'matieres',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trimestre', models.SmallIntegerField()),
                ('note', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('annee_scolaire', models.ForeignKey(db_column='annee_scolaire_id', on_delete=django.db.models.deletion.PROTECT, to='accueil.anneescolaire')),
                ('eleve', models.ForeignKey(db_column='eleve_id', on_delete=django.db.models.deletion.CASCADE, to='accueil.eleve')),
                ('matiere', models.ForeignKey(db_column='matiere_id', on_delete=django.db.models.deletion.CASCADE, to='accueil.matiere')),
            ],
            options={
                'db_table': 'notes',
                'constraints': [
                    models.UniqueConstraint(fields=('eleve', 'matiere', 'annee_scolaire', 'trimestre'), name='unique_note'),
                ],
            },
        ),
    ]
