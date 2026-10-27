from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Accueil
    path('', views.index, name='index'),

    # Élèves
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    path('eleves/ajouter/', views.ajouter_eleves, name='ajouter_eleves'),
    path('eleves/<int:id>/', views.detail_eleve, name='detail_eleve'),
    path('eleves/<int:id>/modifier/', views.modifier_eleve, name='modifier_eleve'),
    path('eleves/<int:id>/supprimer/', views.supprimer_eleve, name='supprimer_eleve'),
    path('eleves/<int:id>/bulletin/', views.bulletin_pdf, name='bulletin_pdf'),

    # Matières
    path('matieres/', views.Liste_matieres, name='liste_matieres'),
    path('matieres/ajouter/', views.ajouter_matieres, name='ajouter_matieres'),
    path('matieres/<int:id>/', views.detail_matiere, name='detail_matiere'),
    path('matieres/<int:id>/modifier/', views.modifier_matiere, name='modifier_matiere'),
    path('matieres/<int:id>/supprimer/', views.supprimer_matiere, name='supprimer_matiere'),

    # Notes
    path('notes/', views.liste_notes, name='liste_notes'),
    path('notes/ajouter/', views.ajouter_note, name='ajouter_note'),

    # Résultats
    path('resultats/', views.resultats, name='resultats'),

    # Paramètres
    path('parametres/', views.parametres, name='parametres'),
]
