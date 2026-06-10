from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.profil, name='profil'),
    path('concours/', views.concours, name='concours'),
    path('resultats/', views.resultats, name='resultats'),
    path('filiere/<int:filiere_id>/', views.detail_filiere, name='detail_filiere'),
    path('analyser-bulletin/', views.analyser_bulletin, name='analyser_bulletin'),
    path('fiche/', views.telecharger_fiche, name='telecharger_fiche'),
    path('choisir/<int:reco_id>/', views.choisir_filiere, name='choisir_filiere'),
    path('choix-final/', views.telecharger_choix_final, name='telecharger_choix_final'),
]