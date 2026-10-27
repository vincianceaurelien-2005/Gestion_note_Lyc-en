"""
Créer le premier utilisateur administrateur.
Usage:
    python manage.py shell < create_user.py
"""
from django.contrib.auth.hashers import make_password
from accueil.models import Utilisateur

username = 'admin'
password = 'admin123'

if Utilisateur.objects.filter(nom_utilisateur=username).exists():
    print(f"L'utilisateur '{username}' existe déjà.")
else:
    Utilisateur.objects.create(
        nom_utilisateur=username,
        mot_de_passe=make_password(password),
        nom_complet='Administrateur',
        contact='',
        role='administrateur',
    )
    print(f"Utilisateur créé : {username} / {password}")
    print("Changez le mot de passe dans Paramètres après connexion.")
