from django.contrib import admin
from .models import (
    Utilisateur, ProfilBachelier, Matiere,
    NoteBachelier, NoteTrimestrielle, MoyenneBulletin,
    FiliereOrientation, PonderationMatiere, Recommandation,
    Concours, RecommandationConcours
)


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_util', 'prenom_util', 'email_util', 'username', 'est_actif', 'date_inscription']
    search_fields = ['nom_util', 'prenom_util', 'email_util', 'username']
    list_filter = ['est_actif']


@admin.register(ProfilBachelier)
class ProfilBachelierAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'serie_bac', 'mention_bac', 'moyenne_bac', 'annee_bac']
    search_fields = ['utilisateur__nom_util', 'utilisateur__email_util']
    list_filter = ['serie_bac', 'mention_bac']


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_matiere', 'categorie_matiere', 'coeff_default']
    search_fields = ['nom_matiere']
    list_filter = ['categorie_matiere']


@admin.register(NoteBachelier)
class NoteBachelierAdmin(admin.ModelAdmin):
    list_display = ['id', 'profil_bachelier', 'matiere', 'note_bac', 'coefficient_bac']
    list_filter = ['matiere']


@admin.register(NoteTrimestrielle)
class NoteTrimestrielleAdmin(admin.ModelAdmin):
    list_display = ['id', 'profil_bachelier', 'matiere', 'trimestre', 'note']
    list_filter = ['trimestre', 'matiere']


@admin.register(MoyenneBulletin)
class MoyenneBulletinAdmin(admin.ModelAdmin):
    list_display = ['id', 'profil_bachelier', 'classe', 'matiere', 'moyenne']
    list_filter = ['classe', 'matiere']


@admin.register(FiliereOrientation)
class FiliereOrientationAdmin(admin.ModelAdmin):
    list_display = ['id', 'code_filiere', 'nom_filiere', 'type_profil_filiere', 'actif_filiere']
    search_fields = ['code_filiere', 'nom_filiere']
    list_filter = ['actif_filiere', 'type_profil_filiere']


@admin.register(PonderationMatiere)
class PonderationMatiereAdmin(admin.ModelAdmin):
    list_display = ['id', 'filiere', 'matiere', 'coeff_importance']
    list_filter = ['filiere', 'matiere']


@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'filiere', 'score_compatibilite', 'niveau_reco', 'est_consultee', 'date_reco']
    list_filter = ['niveau_reco', 'est_consultee']
    search_fields = ['utilisateur__nom_util']


@admin.register(Concours)
class ConcoursAdmin(admin.ModelAdmin):
    list_display = ['id', 'code_concours', 'nom_concours', 'etablissement', 'type_acces', 'moyenne_min', 'actif']
    list_filter = ['etablissement', 'type_acces', 'actif']
    search_fields = ['nom_concours', 'code_concours']


@admin.register(RecommandationConcours)
class RecommandationConcoursAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'concours', 'score_admission', 'niveau_chance']
    list_filter = ['niveau_chance']