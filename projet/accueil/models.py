from django.db import models


class Classe(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    niveau = models.CharField(max_length=30)

    class Meta:
        db_table = 'classes'

    def __str__(self):
        return self.nom


class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=False)

    class Meta:
        db_table = 'annees_scolaires'

    def __str__(self):
        return self.libelle


class Eleve(models.Model):
    matricule = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(
        max_length=1,
        choices=[('M', 'Masculin'), ('F', 'Féminin')]
    )
    date_naissance = models.DateField(null=True, blank=True)
    classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, db_column='classe_id'
    )
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.PROTECT, db_column='annee_scolaire_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'eleves'

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Matiere(models.Model):
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)
    coefficient = models.DecimalField(max_digits=4, decimal_places=2)
    classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, db_column='classe_id'
    )

    class Meta:
        db_table = 'matieres'

    def __str__(self):
        return self.nom


class Note(models.Model):
    eleve = models.ForeignKey(
        Eleve, on_delete=models.CASCADE, db_column='eleve_id'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.CASCADE, db_column='matiere_id'
    )
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.PROTECT, db_column='annee_scolaire_id'
    )
    trimestre = models.SmallIntegerField()
    note = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes'
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'matiere', 'annee_scolaire', 'trimestre'],
                name='unique_note'
            )
        ]

    def __str__(self):
        return f"{self.eleve} - {self.matiere} - {self.note}"


class Utilisateur(models.Model):
    nom_utilisateur = models.CharField(max_length=50, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    nom_complet = models.CharField(max_length=150, blank=True, default='')
    contact = models.CharField(max_length=100, blank=True, default='')
    role = models.CharField(max_length=30, default='administrateur')

    class Meta:
        db_table = 'utilisateurs'

    def __str__(self):
        return self.nom_utilisateur


class Etablissement(models.Model):
    """Informations de l'établissement (une seule ligne)"""
    nom = models.CharField(max_length=200, default='Lycée')
    adresse = models.CharField(max_length=255, blank=True, default='')
    telephone = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    devise = models.CharField(max_length=150, blank=True, default='')

    class Meta:
        db_table = 'etablissement'

    def __str__(self):
        return self.nom
