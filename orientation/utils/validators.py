"""
validators.py — Validation côté serveur pour AIOA
Toutes les fonctions retournent (valeur_nettoyée, erreur_str | None)
"""
from decimal import Decimal, InvalidOperation
import re, unicodedata

# ── Constantes ──────────────────────────────────────────────────────────────
SERIES_VALIDES = {'A1','A2','C','D','E','F1','F2','F3','F4','G1','G2','TI'}
MENTIONS_VALIDES = {'Passable','Assez bien','Bien','Très bien','Excellent',''}
ANNEE_MIN, ANNEE_MAX = 2000, 2030
NOTE_MIN, NOTE_MAX = Decimal('0'), Decimal('20')
MAX_ASPIRATIONS = 1000   # caractères
MAX_ETABLISSEMENT = 200


# ── Helpers internes ────────────────────────────────────────────────────────

def _to_decimal(val: str, label: str):
    """Convertit une chaîne en Decimal dans [0, 20]."""
    try:
        d = Decimal(str(val).replace(',', '.').strip())
    except (InvalidOperation, ValueError):
        return None, f"{label} : valeur non numérique ({val!r})."
    if d < NOTE_MIN or d > NOTE_MAX:
        return None, f"{label} : doit être entre 0 et 20 (reçu : {d})."
    return d, None


def _strip_html(s: str) -> str:
    """Supprime les balises HTML simples (protection XSS)."""
    return re.sub(r'<[^>]+>', '', s or '')


# ── Validateurs publics ─────────────────────────────────────────────────────

def valider_serie(serie: str):
    """Valide la série BAC."""
    s = (serie or '').strip().upper()
    if s not in SERIES_VALIDES:
        return None, f"Série BAC invalide : {serie!r}. Valeurs acceptées : {', '.join(sorted(SERIES_VALIDES))}."
    return s, None


def valider_mention(mention: str):
    """Valide la mention (optionnelle)."""
    m = (mention or '').strip()
    if m not in MENTIONS_VALIDES:
        return None, f"Mention invalide : {mention!r}."
    return m or None, None


def valider_moyenne(moyenne: str):
    """Valide la moyenne générale BAC (0-20)."""
    return _to_decimal(moyenne, "Moyenne BAC")


def valider_annee(annee: str):
    """Valide l'année BAC."""
    try:
        a = int(str(annee).strip())
    except (ValueError, TypeError):
        return None, f"Année BAC invalide : {annee!r}."
    if not (ANNEE_MIN <= a <= ANNEE_MAX):
        return None, f"Année BAC hors plage ({ANNEE_MIN}–{ANNEE_MAX}) : {a}."
    return a, None


def valider_etablissement(etab: str):
    """Nettoie l'établissement (max 200 car., pas de HTML)."""
    s = _strip_html((etab or '').strip())[:MAX_ETABLISSEMENT]
    return s or None, None


def valider_aspirations(texte: str):
    """Nettoie les aspirations (max 1000 car., pas de HTML)."""
    s = _strip_html((texte or '').strip())[:MAX_ASPIRATIONS]
    return s or None, None


def valider_note(val: str, label: str = "Note"):
    """
    Valide une note (trimestrielle ou BAC) :
    - None / '' → retourne (None, None) : champ optionnel non renseigné
    - Sinon vérifie la plage 0-20
    """
    if val is None or str(val).strip() == '':
        return None, None
    return _to_decimal(val, label)


def valider_profil_complet(post: dict) -> tuple[dict, list]:
    """
    Valide tous les champs du formulaire profil.
    Retourne (données_validées, liste_erreurs).
    """
    erreurs = []
    data = {}

    serie, err = valider_serie(post.get('serie_bac', ''))
    if err: erreurs.append(err)
    else: data['serie_bac'] = serie

    mention, err = valider_mention(post.get('mention_bac', ''))
    if err: erreurs.append(err)
    else: data['mention_bac'] = mention

    moyenne, err = valider_moyenne(post.get('moyenne_bac', ''))
    if err: erreurs.append(err)
    else: data['moyenne_bac'] = moyenne

    annee, err = valider_annee(post.get('annee_bac', ''))
    if err: erreurs.append(err)
    else: data['annee_bac'] = annee

    etab, err = valider_etablissement(post.get('etablissement_bac', ''))
    if err: erreurs.append(err)
    else: data['etablissement_bac'] = etab

    asp, err = valider_aspirations(post.get('aspirations_bac', ''))
    if err: erreurs.append(err)
    else: data['aspirations_bac'] = asp

    return data, erreurs


def valider_notes_formulaire(post: dict, matieres_serie: list) -> tuple[dict, list]:
    """
    Valide toutes les notes (T1/T2/T3/bac) pour chaque matière de la série.
    Retourne (notes_validées: dict, erreurs: list).

    notes_validées = {
      nom_matiere: {
        't1': Decimal | None,
        't2': Decimal | None,
        't3': Decimal | None,
        'bac': Decimal | None,
      }
    }
    """
    erreurs = []
    notes = {}

    for nom_mat in matieres_serie:
        entry = {}
        for trim in ('t1', 't2', 't3'):
            val = post.get(f'{trim}_{nom_mat}')
            note, err = valider_note(val, f"{nom_mat} — {trim.upper()}")
            if err:
                erreurs.append(err)
            else:
                entry[trim] = note

        bac_val = post.get(f'bac_{nom_mat}')
        bac_note, err = valider_note(bac_val, f"{nom_mat} — note BAC")
        if err:
            erreurs.append(err)
        else:
            entry['bac'] = bac_note

        notes[nom_mat] = entry

    return notes, erreurs


def valider_bulletins_formulaire(post: dict, matieres: list) -> tuple[dict, list]:
    """
    Valide les moyennes de bulletins 2nde / 1ère.
    Retourne (bulletins: dict, erreurs: list).

    bulletins = {
      (classe, trim, nom_mat): Decimal
    }
    """
    erreurs = []
    bulletins = {}

    for nom_mat in matieres:
        for classe in ('2nde', '1ere'):
            for trim in ('T1', 'T2', 'T3'):
                val = post.get(f'bulletin_{classe}_{trim}_{nom_mat}')
                note, err = valider_note(val, f"{nom_mat} — {classe} {trim}")
                if err:
                    erreurs.append(err)
                elif note is not None:
                    bulletins[(classe, trim, nom_mat)] = note

    return bulletins, erreurs