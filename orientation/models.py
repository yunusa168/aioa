from django.db import models


class Utilisateur(models.Model):
    email_util = models.EmailField(max_length=150, unique=True)
    username = models.CharField(max_length=150, unique=True)
    pwd_util = models.CharField(max_length=255)
    nom_util = models.CharField(max_length=100)
    prenom_util = models.CharField(max_length=100)
    tel_util = models.CharField(max_length=20, blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'utilisateur'

    def __str__(self):
        return f"{self.prenom_util} {self.nom_util} ({self.email_util})"


class ProfilBachelier(models.Model):
    SERIES_BAC = [
        ('A1','A1'),('A2','A2'),('C','C'),('D','D'),('E','E'),
        ('F1','F1'),('F2','F2'),('F3','F3'),('F4','F4'),
        ('G1','G1'),('G2','G2'),('TI','TI'),
    ]
    MENTIONS = [
        ('Passable','Passable'),('Assez bien','Assez bien'),
        ('Bien','Bien'),('Très bien','Très bien'),('Excellent','Excellent'),
    ]

    utilisateur = models.OneToOneField(
        Utilisateur, on_delete=models.CASCADE,
        related_name='profil_bachelier'
    )
    serie_bac = models.CharField(max_length=5, choices=SERIES_BAC)
    mention_bac = models.CharField(max_length=15, choices=MENTIONS, blank=True, null=True)
    moyenne_bac = models.DecimalField(max_digits=4, decimal_places=2)
    annee_bac = models.PositiveIntegerField()
    etablissement_bac = models.CharField(max_length=200, blank=True, null=True)
    aspirations_bac = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profil_bachelier'

    def __str__(self):
        return f"Profil {self.utilisateur} - BAC {self.serie_bac}"


class Matiere(models.Model):
    CATEGORIES = [
        ('litteraire','Littéraire'),('scientifique','Scientifique'),
        ('linguistique','Linguistique'),('artistique','Artistique'),
        ('sportive','Sportive'),('generale','Générale'),
    ]
    nom_matiere = models.CharField(max_length=100, unique=True)
    categorie_matiere = models.CharField(max_length=20, choices=CATEGORIES)
    coeff_default = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)

    class Meta:
        db_table = 'matiere'

    def __str__(self):
        return self.nom_matiere


class NoteBachelier(models.Model):
    profil_bachelier = models.ForeignKey(
        ProfilBachelier, on_delete=models.CASCADE,
        related_name='notes'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.PROTECT,
        related_name='notes'
    )
    note_bac = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    coefficient_bac = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        db_table = 'notes_bachelier'
        unique_together = ('profil_bachelier', 'matiere')

    def __str__(self):
        return f"{self.profil_bachelier} - {self.matiere} : {self.note_bac}/20"


class NoteTrimestrielle(models.Model):
    TRIMESTRES = [
        ('T1','Trimestre 1'),
        ('T2','Trimestre 2'),
        ('T3','Trimestre 3'),
    ]
    profil_bachelier = models.ForeignKey(
        ProfilBachelier, on_delete=models.CASCADE,
        related_name='notes_trimestrielles'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.PROTECT,
        related_name='notes_trimestrielles'
    )
    trimestre = models.CharField(max_length=2, choices=TRIMESTRES)
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'note_trimestrielle'
        unique_together = ('profil_bachelier', 'matiere', 'trimestre')

    def __str__(self):
        return f"{self.profil_bachelier} - {self.matiere} {self.trimestre} : {self.note}/20"


class FiliereOrientation(models.Model):
    TYPE_PROFIL = [('bachelier','Bachelier'),('tous','Tous')]
    code_filiere = models.CharField(max_length=20, unique=True)
    nom_filiere = models.CharField(max_length=200)
    type_profil_filiere = models.CharField(max_length=15, choices=TYPE_PROFIL, default='bachelier')
    niveau_minimum = models.CharField(max_length=50, blank=True, null=True)
    duree_etudes = models.CharField(max_length=100, blank=True, null=True)
    description_filiere = models.TextField(blank=True, null=True)
    debouches = models.TextField(blank=True, null=True)
    conditions_acces = models.TextField(blank=True, null=True)
    competences_requises = models.TextField(blank=True, null=True)
    actif_filiere = models.BooleanField(default=True)

    class Meta:
        db_table = 'filiere_orientation'

    def __str__(self):
        return f"{self.code_filiere} - {self.nom_filiere}"


class PonderationMatiere(models.Model):
    filiere = models.ForeignKey(
        FiliereOrientation, on_delete=models.CASCADE,
        related_name='ponderations'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.PROTECT,
        related_name='ponderations'
    )
    coeff_importance = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = 'ponderation_matiere'
        unique_together = ('filiere', 'matiere')

    def __str__(self):
        return f"{self.filiere} - {self.matiere} : {self.coeff_importance}"


class Recommandation(models.Model):
    NIVEAUX = [
        ('Faible','Faible'),('Moyenne','Moyenne'),
        ('Bonne','Bonne'),('Excellente','Excellente'),
    ]
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE,
        related_name='recommandations'
    )
    filiere = models.ForeignKey(
        FiliereOrientation, on_delete=models.CASCADE,
        related_name='recommandations'
    )
    score_compatibilite = models.DecimalField(max_digits=5, decimal_places=2)
    niveau_reco = models.CharField(max_length=10, choices=NIVEAUX)
    details_analyse = models.JSONField(blank=True, null=True)
    date_reco = models.DateTimeField(auto_now_add=True)
    est_consultee = models.BooleanField(default=False)

    class Meta:
        db_table = 'recommandation'

    def __str__(self):
        return f"Reco {self.utilisateur} → {self.filiere} ({self.score_compatibilite}%)"

# ============================================================
# TABLE 9 : CONCOURS
# ============================================================
class Concours(models.Model):
    TYPE_ACCES = [
        ('ecrit', 'Concours écrit'),
        ('dossier', 'Étude de dossier'),
        ('mixte', 'Écrit + Dossier'),
    ]
    ETABLISSEMENTS = [
    ('INPHB', 'INP-HB Yamoussoukro'),
    ('ESATIC', 'ESATIC Abidjan'),
    ('ETAT', 'Fonction Publique — État de Côte d\'Ivoire'),
]
    code_concours = models.CharField(max_length=30, unique=True)
    nom_concours = models.CharField(max_length=200)
    etablissement = models.CharField(max_length=10, choices=ETABLISSEMENTS)
    ecole = models.CharField(max_length=100, blank=True, null=True)
    filiere_cible = models.CharField(max_length=200)
    type_acces = models.CharField(max_length=10, choices=TYPE_ACCES)
    duree_formation = models.CharField(max_length=200, blank=True, null=True)
    series_requises = models.CharField(max_length=200)
    moyenne_min = models.DecimalField(max_digits=4, decimal_places=2, default=10.0)
    note_maths_min = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    note_physique_min = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    duree_formation = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    debouches = models.TextField(blank=True, null=True)
    documents_requis = models.TextField(blank=True, null=True)
    frais_inscription = models.CharField(max_length=200, blank=True, null=True)
    age_max = models.IntegerField(default=25)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'concours'

    def __str__(self):
        return f"{self.etablissement} — {self.nom_concours}"


# ============================================================
# TABLE 10 : MOYENNE_BULLETIN (2nde + 1ère)
# ============================================================
class MoyenneBulletin(models.Model):
    CLASSES = [
        ('2nde', 'Seconde'),
        ('1ere', 'Première'),
    ]
    TRIMESTRES = [
        ('T1', 'Trimestre 1'),
        ('T2', 'Trimestre 2'),
        ('T3', 'Trimestre 3'),
    ]

    profil_bachelier = models.ForeignKey(
        ProfilBachelier, on_delete=models.CASCADE,
        related_name='bulletins'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.PROTECT,
        related_name='bulletins'
    )
    classe = models.CharField(max_length=5, choices=CLASSES)
    trimestre = models.CharField(max_length=2, choices=TRIMESTRES, null=True, blank=True)
    moyenne = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        db_table = 'moyenne_bulletin'
        unique_together = ('profil_bachelier', 'matiere', 'classe', 'trimestre')

    def __str__(self):
        return f"{self.profil_bachelier} — {self.classe} — {self.matiere} : {self.moyenne}/20"


# ============================================================
# TABLE 11 : RECOMMANDATION_CONCOURS
# ============================================================
class RecommandationConcours(models.Model):
    NIVEAUX = [
        ('Faible', 'Faible'),
        ('Possible', 'Possible'),
        ('Bonne', 'Bonne'),
        ('Excellente', 'Excellente'),
    ]

    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE,
        related_name='recommandations_concours'
    )
    concours = models.ForeignKey(
        Concours, on_delete=models.CASCADE,
        related_name='recommandations'
    )
    score_admission = models.DecimalField(max_digits=5, decimal_places=2)
    niveau_chance = models.CharField(max_length=10, choices=NIVEAUX)
    details = models.JSONField(blank=True, null=True)
    date_reco = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommandation_concours'

    def __str__(self):
        return f"{self.utilisateur} → {self.concours} ({self.score_admission}%)"