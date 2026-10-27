from django.contrib import admin
from .models import (
    Classe, AnneeScolaire, Eleve, Matiere, Note,
    Utilisateur, Etablissement,
)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'niveau')
    search_fields = ('nom',)


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'active')
    list_filter = ('active',)


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'sexe', 'classe', 'annee_scolaire')
    list_filter = ('sexe', 'classe', 'annee_scolaire')
    search_fields = ('matricule', 'nom', 'prenom')


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'coefficient', 'classe')
    list_filter = ('classe',)
    search_fields = ('code', 'nom')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'matiere', 'trimestre', 'note', 'annee_scolaire')
    list_filter = ('trimestre', 'annee_scolaire')
    search_fields = ('eleve__nom', 'eleve__prenom')


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom_utilisateur', 'nom_complet', 'contact', 'role')
    search_fields = ('nom_utilisateur', 'nom_complet')


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
