"""
Script pour initialiser des données de base.
Exécuter après migrate :
    python manage.py shell < seed_data.py
ou :
    python manage.py shell
    puis coller le contenu
"""
from accueil.models import Classe, AnneeScolaire, Eleve, Matiere

# Année scolaire active
annee, _ = AnneeScolaire.objects.get_or_create(
    libelle="2025-2026",
    defaults={"active": True}
)
AnneeScolaire.objects.exclude(id=annee.id).update(active=False)
annee.active = True
annee.save()
print(f"Année: {annee}")

# Classes
classes_data = [
    ("6ème A", "6ème"),
    ("5ème A", "5ème"),
    ("4ème A", "4ème"),
    ("3ème A", "3ème"),
    ("Terminale A", "Terminale"),
]
for nom, niveau in classes_data:
    c, created = Classe.objects.get_or_create(nom=nom, defaults={"niveau": niveau})
    print(f"Classe: {c.nom} {'(créée)' if created else '(existe)'}")

# Quelques matières pour Terminale A
term = Classe.objects.get(nom="Terminale A")
matieres_data = [
    ("MATH", "Mathématiques", 4),
    ("PHYS", "Physique-Chimie", 3),
    ("FRAN", "Français", 3),
    ("ANG", "Anglais", 2),
    ("HIST", "Histoire-Géo", 2),
]
for code, nom, coef in matieres_data:
    m, created = Matiere.objects.get_or_create(
        code=code,
        defaults={"nom": nom, "coefficient": coef, "classe": term}
    )
    print(f"Matière: {m.code} {'(créée)' if created else '(existe)'}")

print("\nDonnées de base OK. Tu peux maintenant ajouter des élèves.")
