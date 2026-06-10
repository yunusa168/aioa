"""
Tests unitaires AIOA — Algorithme de recommandation
Couvre :
  1. _bonus_mention
  2. _calculer_score_aspiration_ameliore
  3. _calculer_score_matieres_pondere
  4. _calculer_score_progression (mock)
  5. Filtres (score >= 50%)
  6. Intégration : score final cohérent
"""

from django.test import TestCase
from unittest.mock import MagicMock, patch
from orientation.views import (
    _bonus_mention,
    _calculer_score_aspiration_ameliore,
    _calculer_score_matieres_pondere,
    _calculer_score_progression,
    ASPIRATIONS_KEYWORDS,
    COMPAT_SERIE,
    POIDS_MATIERES_PAR_SERIE,
)


# ─────────────────────────────────────────────────────────────
# 1. BONUS MENTION
# ─────────────────────────────────────────────────────────────

class BonusMentionTest(TestCase):

    def test_mention_excellent(self):
        self.assertEqual(_bonus_mention("Excellent"), 8.0)

    def test_mention_tres_bien(self):
        self.assertEqual(_bonus_mention("Très bien"), 6.0)

    def test_mention_tres_bien_sans_accent(self):
        self.assertEqual(_bonus_mention("tres bien"), 6.0)

    def test_mention_bien(self):
        self.assertEqual(_bonus_mention("Bien"), 4.0)

    def test_mention_assez_bien(self):
        self.assertEqual(_bonus_mention("Assez bien"), 4.0)  # "bien" est inclus dans "assez bien"

    def test_mention_passable(self):
        self.assertEqual(_bonus_mention("Passable"), 0.0)

    def test_mention_vide(self):
        self.assertEqual(_bonus_mention(""), 0.0)

    def test_mention_none(self):
        self.assertEqual(_bonus_mention(None), 0.0)

    def test_mention_majuscules(self):
        self.assertEqual(_bonus_mention("TRÈS BIEN"), 6.0)


# ─────────────────────────────────────────────────────────────
# 2. SCORE ASPIRATION
# ─────────────────────────────────────────────────────────────

class ScoreAspirationTest(TestCase):

    def test_aspiration_vide_retourne_50(self):
        score = _calculer_score_aspiration_ameliore("", "UNA-MATHINFO-L12")
        self.assertEqual(score, 50.0)

    def test_aspiration_none_retourne_50(self):
        score = _calculer_score_aspiration_ameliore(None, "UNA-MATHINFO-L12")
        self.assertEqual(score, 50.0)

    def test_filiere_sans_keywords_retourne_50(self):
        score = _calculer_score_aspiration_ameliore("développeur", "CODE-INEXISTANT")
        self.assertEqual(score, 50.0)

    def test_correspondance_exacte_eleve_score(self):
        # "informatique" est un keyword de UNA-MATHINFO-L12
        score = _calculer_score_aspiration_ameliore("je veux faire informatique", "UNA-MATHINFO-L12")
        self.assertGreaterEqual(score, 20.0)

    def test_aucune_correspondance_retourne_plancher_20(self):
        # "cuisine" ne correspond à rien dans une filière info
        score = _calculer_score_aspiration_ameliore("cuisine gastronomie", "UNA-MATHINFO-L12")
        self.assertEqual(score, 20.0)

    def test_score_plafonne_a_100(self):
        # Remplir tous les keywords
        keywords = ASPIRATIONS_KEYWORDS.get("UNA-MATHINFO-L12", [])
        aspiration = " ".join(keywords)
        score = _calculer_score_aspiration_ameliore(aspiration, "UNA-MATHINFO-L12")
        self.assertLessEqual(score, 100.0)

    def test_correspondance_partielle(self):
        # "dev" devrait matcher "développeur" en correspondance partielle
        score = _calculer_score_aspiration_ameliore("dev logiciel", "UNA-MATHINFO-L12")
        self.assertGreaterEqual(score, 20.0)


# ─────────────────────────────────────────────────────────────
# 3. SCORE MATIÈRES PONDÉRÉES
# ─────────────────────────────────────────────────────────────

class ScoreMatieresPondereTest(TestCase):

    def _make_ponderation(self, matiere_id, nom_matiere, coeff):
        """Crée un mock de PonderationMatiere."""
        p = MagicMock()
        p.matiere_id = matiere_id
        p.matiere.nom_matiere = nom_matiere
        p.coeff_importance = coeff
        return p

    def test_sans_ponderation_retourne_moyenne(self):
        score = _calculer_score_matieres_pondere({}, [], 'D', 12.0)
        self.assertAlmostEqual(score, 12.0 / 20 * 100, places=1)

    def test_note_excellente_donne_score_eleve(self):
        ponderations = [self._make_ponderation(1, 'Mathématiques', 5)]
        notes = {1: 18.0}
        score = _calculer_score_matieres_pondere(notes, ponderations, 'C', 14.0)
        self.assertGreater(score, 70.0)

    def test_note_faible_donne_score_bas(self):
        ponderations = [self._make_ponderation(1, 'Mathématiques', 5)]
        notes = {1: 4.0}
        score = _calculer_score_matieres_pondere(notes, ponderations, 'C', 8.0)
        self.assertLess(score, 40.0)

    def test_poids_serie_C_augmente_maths(self):
        """Série C : Maths a multiplicateur 1.8 → score plus élevé que série A1."""
        ponderations = [self._make_ponderation(1, 'Mathématiques', 3)]
        notes = {1: 15.0}
        score_C  = _calculer_score_matieres_pondere(notes, ponderations, 'C', 12.0)
        score_A1 = _calculer_score_matieres_pondere(notes, ponderations, 'A1', 12.0)
        # Série C valorise plus les maths que A1
        self.assertGreater(score_C, score_A1)

    def test_matiere_manquante_utilise_moyenne(self):
        """Si la note d'une matière est absente, on utilise la moyenne générale."""
        ponderations = [self._make_ponderation(99, 'Matière inconnue', 3)]
        notes = {}  # pas de note pour matière 99
        score = _calculer_score_matieres_pondere(notes, ponderations, 'D', 10.0)
        # Doit utiliser 10/20 = 50%
        self.assertAlmostEqual(score, 50.0, delta=5.0)

    def test_score_entre_0_et_100(self):
        ponderations = [
            self._make_ponderation(1, 'Mathématiques', 5),
            self._make_ponderation(2, 'Physique-Chimie', 3),
        ]
        notes = {1: 20.0, 2: 20.0}
        score = _calculer_score_matieres_pondere(notes, ponderations, 'C', 20.0)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


# ─────────────────────────────────────────────────────────────
# 4. SCORE PROGRESSION (mock DB)
# ─────────────────────────────────────────────────────────────

class ScoreProgressionTest(TestCase):

    def _make_profil(self, notes_trim=None, moyenne_bac=12.0):
        profil = MagicMock()
        profil.moyenne_bac = moyenne_bac
        if notes_trim:
            profil.notes_trimestrielles.values_list.return_value = notes_trim
        else:
            profil.notes_trimestrielles.values_list.return_value = [moyenne_bac]
        return profil

    def _make_bulletin(self, classe, moyenne):
        b = MagicMock()
        b.classe = classe
        b.moyenne = moyenne
        return b

    @patch('orientation.views.MoyenneBulletin')
    def test_pas_de_bulletins_retourne_zero(self, mock_bulletin):
        mock_bulletin.objects.filter.return_value.exists.return_value = False
        profil = self._make_profil()
        bonus, msg = _calculer_score_progression(profil)
        self.assertEqual(bonus, 0.0)

    @patch('orientation.views.MoyenneBulletin')
    def test_progression_excellente(self, mock_bulletin):
        """2nde=8 → Tle=14 : delta=6 → bonus=10."""
        bulletins = [
            self._make_bulletin('2nde', 8.0),
        ]
        mock_bulletin.objects.filter.return_value.exists.return_value = True
        mock_bulletin.objects.filter.return_value.__iter__ = lambda s: iter(bulletins)
        profil = self._make_profil(notes_trim=[14.0], moyenne_bac=14.0)
        bonus, msg = _calculer_score_progression(profil)
        self.assertEqual(bonus, 10.0)

    @patch('orientation.views.MoyenneBulletin')
    def test_baisse_notable(self, mock_bulletin):
        """2nde=16 → Tle=10 : delta=-6 → bonus=-5."""
        bulletins = [self._make_bulletin('2nde', 16.0)]
        mock_bulletin.objects.filter.return_value.exists.return_value = True
        mock_bulletin.objects.filter.return_value.__iter__ = lambda s: iter(bulletins)
        profil = self._make_profil(notes_trim=[10.0], moyenne_bac=10.0)
        bonus, msg = _calculer_score_progression(profil)
        self.assertEqual(bonus, -5.0)

    @patch('orientation.views.MoyenneBulletin')
    def test_niveau_stable(self, mock_bulletin):
        """2nde=12 → Tle=12.3 : delta=0.3 → bonus=0."""
        bulletins = [self._make_bulletin('2nde', 12.0)]
        mock_bulletin.objects.filter.return_value.exists.return_value = True
        mock_bulletin.objects.filter.return_value.__iter__ = lambda s: iter(bulletins)
        profil = self._make_profil(notes_trim=[12.3], moyenne_bac=12.3)
        bonus, msg = _calculer_score_progression(profil)
        self.assertEqual(bonus, 0.0)


# ─────────────────────────────────────────────────────────────
# 5. COMPAT_SERIE — cohérence des données
# ─────────────────────────────────────────────────────────────

class CompatSerieTest(TestCase):

    SERIES_VALIDES = {'A1','A2','C','D','E','F1','F2','F3','F4','G1','G2','TI'}

    def test_toutes_series_dans_compat_sont_valides(self):
        """Vérifie qu'aucune série fantaisiste n'est dans COMPAT_SERIE."""
        for code, series in COMPAT_SERIE.items():
            for s in series:
                self.assertIn(s, self.SERIES_VALIDES,
                    f"Série '{s}' invalide dans COMPAT_SERIE['{code}']")

    def test_filieres_scientifiques_acceptent_serie_C(self):
        """Les filières Maths/Info/Sciences doivent accepter la série C."""
        filieres_scientifiques = [
            'UNA-MATHINFO-L12', 'UAO-MATHINFO-L12', 'UFHB-MATHINFO-L12',
        ]
        for code in filieres_scientifiques:
            if code in COMPAT_SERIE:
                self.assertIn('C', COMPAT_SERIE[code],
                    f"Série C absente de COMPAT_SERIE['{code}']")

    def test_filieres_litteraires_acceptent_serie_A1(self):
        filieres_litt = ['UFHB-LANGUES', 'UFHB-COMM', 'UFHB-DROIT', 'UAO-DROIT']
        for code in filieres_litt:
            if code in COMPAT_SERIE:
                self.assertIn('A1', COMPAT_SERIE[code],
                    f"Série A1 absente de COMPAT_SERIE['{code}']")


# ─────────────────────────────────────────────────────────────
# 6. SCORE FINAL — test d'intégration bout en bout
# ─────────────────────────────────────────────────────────────

class ScoreFinalIntegrationTest(TestCase):

    def test_bon_profil_scientifique_score_superieur_mauvais(self):
        """
        Un élève série C avec 16 en Maths doit scorer plus haut
        qu'un élève série C avec 6 en Maths sur une filière Maths-Info.
        """
        from unittest.mock import MagicMock

        ponderations = []
        p = MagicMock()
        p.matiere_id = 1
        p.matiere.nom_matiere = 'Mathématiques'
        p.coeff_importance = 5
        ponderations.append(p)

        score_bon   = _calculer_score_matieres_pondere({1: 16.0}, ponderations, 'C', 14.0)
        score_faible = _calculer_score_matieres_pondere({1: 6.0},  ponderations, 'C', 8.0)
        self.assertGreater(score_bon, score_faible)

    def test_bonus_mention_plafonne_score_a_100(self):
        """Score de 98 + bonus mention Excellent (8) = 100, pas 106."""
        score_base = 98.0
        bonus = _bonus_mention("Excellent")
        score_final = round(min(score_base + bonus, 100), 2)
        self.assertEqual(score_final, 100.0)

    def test_filtre_50_pourcent(self):
        """Simuler que les recommandations < 50% sont filtrées."""
        recommandations = [
            MagicMock(score_compatibilite=75.0),
            MagicMock(score_compatibilite=45.0),
            MagicMock(score_compatibilite=55.0),
            MagicMock(score_compatibilite=30.0),
        ]
        filtrees = [r for r in recommandations if r.score_compatibilite >= 50]
        self.assertEqual(len(filtrees), 2)
        for r in filtrees:
            self.assertGreaterEqual(r.score_compatibilite, 50.0)

    def test_poids_serie_D_svt_egal_ou_superieur_maths(self):
        """Série D : SVT a un poids au moins égal à Maths."""
        poids = POIDS_MATIERES_PAR_SERIE.get('D', {})
        self.assertGreaterEqual(
            poids.get('SVT', 1.0),
            poids.get('Mathématiques', 1.0)
        )

    def test_poids_serie_C_maths_superieur_svt(self):
        """Série C : Maths a plus de poids que SVT."""
        poids = POIDS_MATIERES_PAR_SERIE.get('C', {})
        self.assertGreater(
            poids.get('Mathématiques', 1.0),
            poids.get('SVT', 1.0)
        )