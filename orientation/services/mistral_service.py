import base64
import io
import json
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# TABLE DE CORRESPONDANCE : variantes → nom canonique
# ─────────────────────────────────────────────────────────────
CORRESPONDANCES = {
    # Mathématiques
    "maths": "Mathématiques", "math": "Mathématiques",
    "mathematiques": "Mathématiques", "mathématiques": "Mathématiques",
    "mathématique": "Mathématiques", "mathematique": "Mathématiques",

    # Physique-Chimie (association explicite des deux mots)
    "physique-chimie": "Physique-Chimie", "physique chimie": "Physique-Chimie",
    "physique & chimie": "Physique-Chimie", "physique et chimie": "Physique-Chimie",
    "pc": "Physique-Chimie", "sciences physiques": "Physique-Chimie",
    "chimie": "Physique-Chimie",

    # Physique seul (séries F1, F2, F3, F4, TI)
    # NB : "physique" seul est géré spécialement dans _normaliser_matiere
    # pour distinguer selon le contexte. On le laisse ici mais la logique
    # dans _normaliser_matiere le court-circuite si "chimie" est absent.
    "physique": "Physique-Chimie",  # sera court-circuité si chimie absent

    # SVT
    "svt": "SVT", "sciences de la vie": "SVT",
    "sciences naturelles": "SVT", "biologie": "SVT",
    "sciences de la vie et de la terre": "SVT", "sn": "SVT",

    # Français
    "francais": "Français", "français": "Français",
    "langue française": "Français", "fr": "Français",
    "expression française": "Français", "littérature": "Français",
    "composition français": "Français", "composition francais": "Français",
    "composition de français": "Français", "composition de francais": "Français",
    "rédaction": "Français", "redaction": "Français",

    # Philosophie
    "philosophie": "Philosophie", "philo": "Philosophie",

    # Histoire-Géographie
    "histoire": "Histoire-Géographie", "géographie": "Histoire-Géographie",
    "geographie": "Histoire-Géographie",
    "histoire-géographie": "Histoire-Géographie",
    "histoire géographie": "Histoire-Géographie",
    "hg": "Histoire-Géographie", "hist-geo": "Histoire-Géographie",
    "histoire & géographie": "Histoire-Géographie",
    "histoire et géographie": "Histoire-Géographie",
    "histoire et géographie": "Histoire-Géographie",

    # Anglais
    "anglais": "Anglais", "english": "Anglais", "ang": "Anglais",
    "langue anglaise": "Anglais",

    # Espagnol
    "espagnol": "Espagnol", "esp": "Espagnol",

    # Allemand
    "allemand": "Allemand", "all": "Allemand",

    # Informatique
    "informatique": "Informatique", "info": "Informatique",
    "tic": "Informatique", "ti": "Informatique",
    "technologies de l'information": "Informatique",
    "traitement de l'information": "Informatique",

    # Économie-Gestion
    "economie": "Économie-Gestion", "économie": "Économie-Gestion",
    "eco": "Économie-Gestion", "éco": "Économie-Gestion",
    "économie-gestion": "Économie-Gestion", "economie-gestion": "Économie-Gestion",
    "économie gestion": "Économie-Gestion", "gestion": "Économie-Gestion",
    "sciences économiques": "Économie-Gestion",

    # Comptabilité
    "comptabilite": "Comptabilité", "comptabilité": "Comptabilité",
    "compta": "Comptabilité",

    # Gestion Commerciale
    "gestion commerciale": "Gestion Commerciale",
    "commerce": "Gestion Commerciale",

    # Sciences Industrielles
    "sciences industrielles": "Sciences Industrielles",
    "si": "Sciences Industrielles", "technologie": "Sciences Industrielles",

    # Dessin Technique
    "dessin technique": "Dessin Technique", "dessin": "Dessin Technique",
    "dt": "Dessin Technique",

    # Électronique
    "electronique": "Électronique", "électronique": "Électronique",
    "elec": "Électronique",

    # Électrotechnique
    "electrotechnique": "Électrotechnique", "électrotechnique": "Électrotechnique",

    # Génie Civil
    "genie civil": "Génie Civil", "génie civil": "Génie Civil",
    "gc": "Génie Civil",

    # Topographie
    "topographie": "Topographie", "topo": "Topographie",

    # Construction Mécanique
    "construction mecanique": "Construction Mécanique",
    "construction mécanique": "Construction Mécanique",
    "mecanique": "Construction Mécanique", "mécanique": "Construction Mécanique",

    # EPS — doit être AVANT "physique" pour éviter les conflits
    "eps": "EPS", "éducation physique": "EPS",
    "education physique": "EPS", "sport": "EPS",
    "education physique et sportive": "EPS",
    "éducation physique et sportive": "EPS",
    "éducation physique & sportive": "EPS",
    "ep&s": "EPS", "eps/sport": "EPS",

    # Culture Manuelle
    "culture manuelle": "Culture Manuelle", "cm": "Culture Manuelle",
    "travaux manuels": "Culture Manuelle", "travail manuel": "Culture Manuelle",
    "tech manuelle": "Culture Manuelle", "technique manuelle": "Culture Manuelle",

    # Conduite (matière apparaissant dans certains bulletins ivoiriens)
    "conduite": "Conduite", "discipline": "Conduite",
    "conduite et discipline": "Conduite",

    # Arts
    "arts plastiques": "Arts Plastiques", "arts": "Arts Plastiques",
    "musique": "Musique",
}


# Matières qui doivent être testées en priorité (les plus spécifiques en premier)
_PRIORITES = [
    "education physique et sportive", "éducation physique et sportive",
    "éducation physique", "education physique",
    "physique-chimie", "physique chimie", "sciences physiques",
    "physique – chimie", "physique - chimie",
    "sciences de la vie et de la terre", "sciences de la vie",
    "histoire-géographie", "histoire et géographie", "histoire géographie",
    "gestion commerciale", "économie-gestion", "economie-gestion",
    "construction mécanique", "construction mecanique",
    "dessin technique", "sciences industrielles",
    "génie civil", "genie civil",
    "culture manuelle", "travaux manuels",
    "composition français", "composition francais",
    "composition de français", "composition de francais",
    "conduite et discipline",
]

def _normaliser_matiere(nom: str) -> str:
    """Normalise un nom de matière vers le nom canonique."""
    if not nom:
        return nom
    cle = nom.strip().lower()
    # Normaliser les tirets/espaces variantes autour de "physique-chimie"
    cle = re.sub(r'physique\s*[–—-]\s*chimie', 'physique-chimie', cle)
    cle = re.sub(r'physique\s*&\s*chimie', 'physique-chimie', cle)
    cle = re.sub(r'physique\s+et\s+chimie', 'physique-chimie', cle)

    # ── Cas spécial : "physique" seul (sans chimie) → "Physique" (séries F/TI)
    if cle == "physique" or (cle.startswith("physique") and "chimie" not in cle and len(cle) <= 10):
        return "Physique"

    # 1. Correspondance directe
    if cle in CORRESPONDANCES:
        return CORRESPONDANCES[cle]

    # 2. Tester les variantes prioritaires (longues/spécifiques d'abord)
    for variante in _PRIORITES:
        if variante in cle:
            return CORRESPONDANCES.get(variante, variante.title())

    # 3. Correspondance partielle : variante >= 5 chars contenue dans le nom
    #    IMPORTANT : "physique" seul sans "chimie" → on NE mappe PAS vers "Physique-Chimie"
    for variante, canonique in CORRESPONDANCES.items():
        if len(variante) >= 5 and variante in cle:
            # Éviter que "physique" seul (sans chimie) soit mappé vers Physique-Chimie
            if variante == "physique" and "chimie" not in cle:
                continue
            return canonique

    # 4. Retourner tel quel
    return nom.strip().title()


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _get_client():
    from mistralai import Mistral
    return Mistral(api_key=settings.MISTRAL_API_KEY)


def _encode_image_b64(file_obj) -> str:
    file_obj.seek(0)
    return base64.standard_b64encode(file_obj.read()).decode('utf-8')


def _get_media_type(file_obj) -> str:
    name = getattr(file_obj, 'name', '').lower()
    if name.endswith('.png'):  return 'image/png'
    if name.endswith('.webp'): return 'image/webp'
    if name.endswith('.pdf'):  return 'application/pdf'
    return 'image/jpeg'


def _parse_float(val):
    if val is None: return None
    try:    return round(float(val), 2)
    except: return None


def _nettoyer_json(raw: str) -> str:
    raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*$',   '', raw, flags=re.MULTILINE)
    raw = raw.strip()
    # Corriger les nombres avec zéro devant (ex: 05 → 5)
    raw = re.sub(r':\s*0+([1-9]\d*)', r': \1', raw)
    raw = re.sub(r',\s*0+([1-9]\d*)', r', \1', raw)
    # Supprimer les virgules finales
    raw = re.sub(r',\s*([\]}])', r'\1', raw)
    return raw


def _valider_note(note) -> float | None:
    if note is None: return None
    try:
        v = float(note)
        if 0 <= v <= 20: return round(v, 2)
    except: pass
    return None


def _calculer_notes_bac(matieres_brutes: list) -> dict:
    """
    Calcule toutes les notes sur 20 à partir des données brutes fournies par Mistral.
    Mistral fournit uniquement note_obtenue + coefficient, Python fait tous les calculs.

    Règle générale : note_sur_20 = note_obtenue ÷ coefficient
    Règle Français : écrit_sur_20 = note_ecrit ÷ coeff_ecrit
                     oral_sur_20  = note_oral  ÷ coeff_oral
                     Français     = (écrit_sur_20 + oral_sur_20) ÷ 2
    """
    notes = {}
    francais_ecrit_sur_20 = None
    francais_oral_sur_20  = None

    for item in matieres_brutes:
        nom_brut = item.get("matiere", "")
        if not nom_brut: continue
        nom_lower = nom_brut.lower().strip()

        no = item.get("note_obtenue")
        co = item.get("coefficient")

        if no is None or co is None:
            continue
        try:
            no_f = float(no)
            co_f = float(co)
            if co_f <= 0:
                continue
            sur_20 = round(no_f / co_f, 2)
            if not (0 <= sur_20 <= 20):
                continue
        except:
            continue

        is_francais = "fran" in nom_lower
        is_ecrit    = any(x in nom_lower for x in ["ecrit", "écrit"])
        is_oral     = "oral" in nom_lower

        if is_francais and is_ecrit:
            francais_ecrit_sur_20 = sur_20
            continue

        if is_francais and is_oral:
            francais_oral_sur_20 = sur_20
            continue

        nom = _normaliser_matiere(nom_brut)
        notes[nom] = sur_20

    # Fusionner Français Écrit + Oral
    # Formule : (écrit_sur_20 + oral_sur_20) ÷ 2
    if francais_ecrit_sur_20 is not None and francais_oral_sur_20 is not None:
        notes["Français"] = round((francais_ecrit_sur_20 + francais_oral_sur_20) / 2, 2)
    elif francais_ecrit_sur_20 is not None:
        notes["Français"] = francais_ecrit_sur_20
    elif francais_oral_sur_20 is not None:
        notes["Français"] = francais_oral_sur_20

    return notes


def _normaliser_notes_bulletin(notes_brutes: dict) -> dict:
    """Normalise les clés d'un dict de notes bulletin vers les noms canoniques.
    
    Gère le cas spécial du Français qui peut apparaître en deux lignes
    distinctes dans les bulletins : "Français Écrit" et "Français Oral".
    Dans ce cas on calcule la moyenne des deux pour obtenir une seule note.
    """
    notes_propres = {}
    francais_ecrit = None
    francais_oral  = None

    for matiere_brute, note in notes_brutes.items():
        v = _valider_note(note)
        if v is None:
            continue
        nom_lower = matiere_brute.strip().lower()
        is_francais = "fran" in nom_lower
        is_ecrit    = any(x in nom_lower for x in ["ecrit", "écrit"])
        is_oral     = "oral" in nom_lower

        if is_francais and is_ecrit:
            francais_ecrit = v
            continue
        if is_francais and is_oral:
            francais_oral = v
            continue

        nom_canonique = _normaliser_matiere(matiere_brute)
        notes_propres[nom_canonique] = v

    # Fusionner Français Écrit + Oral :
    #   Les notes sont ramenées sur 20 (note / coeff), puis moyenne des deux
    if francais_ecrit is not None and francais_oral is not None:
        notes_propres["Français"] = round((francais_ecrit + francais_oral) / 2, 2)
    elif francais_ecrit is not None:
        notes_propres["Français"] = francais_ecrit
    elif francais_oral is not None:
        notes_propres["Français"] = francais_oral

    return notes_propres


def _pdf_vers_images_b64(file_content: bytes) -> list:
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(file_content, dpi=250, fmt='PNG', first_page=1, last_page=4)
        result = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            result.append(base64.standard_b64encode(buf.getvalue()).decode('utf-8'))
        logger.info(f"PDF converti : {len(result)} page(s)")
        return result
    except Exception as e:
        logger.error(f"Conversion PDF échouée : {e}")
        return []


# ─────────────────────────────────────────────────────────────
# PROMPTS — format liste libre pour tous les types
# ─────────────────────────────────────────────────────────────

def _build_prompt(type_document: str, serie_bac: str) -> str:
    base = (
        "Tu es un expert en lecture de bulletins scolaires ivoiriens.\n"
        "Analyse TOUT le document de haut en bas et extrais TOUTES les matières visibles.\n"
        "Réponds EXCLUSIVEMENT en JSON valide, sans texte avant ni après, sans balises markdown.\n"
        "IMPORTANT : Inclure ABSOLUMENT toutes les matières avec une note, même si tu n'es pas sûr du nom.\n"
    )

    if type_document == 'bac':
        return base + f"""
Document : Relevé de notes du BAC ivoirien — série {serie_bac or 'inconnue'}.

TON RÔLE : lire et extraire les données brutes uniquement. NE CALCULE RIEN.
Le système Python se charge de tous les calculs.

════════════════════════════════════════════
RÈGLES DE LECTURE
════════════════════════════════════════════

1. RÈGLE GÉNÉRALE :
   Extrais le nom de la matière, la note_obtenue et le coefficient exactement tels qu'écrits.
   Ne calcule PAS de note sur 20. Pas de champ "note_sur_20".

2. PHYSIQUE-CHIMIE vs PHYSIQUE SEUL :
   - Document écrit "Physique-Chimie", "Physique & Chimie", "Sciences Physiques" → nom = "Physique-Chimie"
   - Document écrit uniquement "Physique" sans "Chimie" → nom = "Physique"
   - Série déclarée : {serie_bac or 'inconnue'} — utilise-la pour lever le doute si besoin.

3. FRANÇAIS (deux lignes séparées obligatoires) :
   - Retourne TOUJOURS deux entrées distinctes : "Français Écrit" et "Français Oral"
   - Chacune avec sa propre note_obtenue et son coefficient
   - NE fusionne PAS, NE calcule PAS de moyenne — Python s'en charge
   - Exemple :
     {{"matiere": "Français Écrit", "note_obtenue": 22, "coefficient": 2}},
     {{"matiere": "Français Oral",  "note_obtenue": 12, "coefficient": 1}}

4. ÉPREUVES FACULTATIVES :
   - Si la note est 00 ou nulle, ignorer cette matière.

════════════════════════════════════════════

IMPORTANT — LECTURE DE LA SÉRIE :
Le champ etudiant.serie DOIT contenir la série BAC exactement telle qu'elle est écrite sur le document
(ex: "D", "C", "A1", "G2", "TI"). Ne laisse JAMAIS ce champ à null si la série est lisible sur le document.

Format de réponse JSON :
{{
  "type": "bac",
  "etudiant": {{
    "nom": null,
    "prenoms": null,
    "serie": null,
    "etablissement": null,
    "annee": null
  }},
  "matieres": [
    {{"matiere": "Mathématiques",       "note_obtenue": 65, "coefficient": 5}},
    {{"matiere": "Physique-Chimie",     "note_obtenue": 50, "coefficient": 5}},
    {{"matiere": "SVT",                 "note_obtenue": 12, "coefficient": 2}},
    {{"matiere": "Français Écrit",      "note_obtenue": 22, "coefficient": 2}},
    {{"matiere": "Français Oral",       "note_obtenue": 12, "coefficient": 1}},
    {{"matiere": "Philosophie",         "note_obtenue": 18, "coefficient": 2}},
    {{"matiere": "Histoire-Géographie", "note_obtenue": 24, "coefficient": 2}},
    {{"matiere": "Anglais",             "note_obtenue": 13, "coefficient": 1}}
  ],
  "moyenne_generale": null,
  "mention": null
}}

Règles finales :
- PAS de champ "note_sur_20" — Python calcule tout
- moyenne_generale = la M.G.A. écrite sur le document (sur 20), telle quelle
- mention = "Passable", "Assez bien", "Bien", "Très bien" ou "Excellent"
- Les coefficients ne doivent PAS avoir de zéro devant (écrire 5, pas 05)
- Ignorer les épreuves facultatives avec note = 00"""

    else:
        # Correspondance série BAC → classe précédente réelle
        SERIE_VERS_2NDE = {
            'A1':'2nde A1','A2':'2nde A2',
            'C':'2nde C','D':'2nde C','E':'2nde E',
            'F1':'2nde F1','F2':'2nde F2','F3':'2nde F3','F4':'2nde F4',
            'G1':'2nde G1','G2':'2nde G2','TI':'2nde TI',
        }
        SERIE_VERS_1ERE = {
            'A1':'1ère A1','A2':'1ère A2',
            'C':'1ère C','D':'1ère D','E':'1ère E',
            'F1':'1ère F1','F2':'1ère F2','F3':'1ère F3','F4':'1ère F4',
            'G1':'1ère G1','G2':'1ère G2','TI':'1ère TI',
        }
        if type_document in ('T1','T2','T3'):
            label = f'{type_document} — Terminale {serie_bac or ""}'
        elif type_document.startswith('bulletin_2nde'):
            trim = type_document.replace('bulletin_2nde_','')
            classe_reelle = SERIE_VERS_2NDE.get(serie_bac, f'2nde')
            label = f'Trimestre {trim} — {classe_reelle}'
        elif type_document.startswith('bulletin_1ere'):
            trim = type_document.replace('bulletin_1ere_','')
            classe_reelle = SERIE_VERS_1ERE.get(serie_bac, f'1ère')
            label = f'Trimestre {trim} — {classe_reelle}'
        else:
            label = type_document

        return base + f"""
Document : Bulletin scolaire ivoirien — {label}, série BAC visée : {serie_bac or 'inconnue'}.
IMPORTANT : Ce bulletin doit correspondre à la classe indiquée ci-dessus. Si tu détectes que la classe sur le document ne correspond PAS ({label}), signale-le dans un champ "avertissement" dans ta réponse JSON.

Extrais la moyenne de CHAQUE matière visible dans le bulletin.
Utilise une liste, pas un objet fixe — comme ça tu n'oublies rien.

Format de réponse :
{{
  "type": "bulletin",
  "trimestre": "{type_document}",
  "classe": null,
  "etablissement": null,
  "etudiant": {{
    "nom": null,
    "prenoms": null
  }},
  "matieres": [
    {{"matiere": "Mathématiques", "moyenne": 14.5}},
    {{"matiere": "Physique-Chimie", "moyenne": 12.0}},
    {{"matiere": "Français", "moyenne": 11.5}},
    ... (TOUTES les matières avec une note)
  ],
  "moyenne_generale": null
}}

Règles STRICTES :
- Parcours le document ligne par ligne, ne saute AUCUNE matière
- moyenne = la moyenne trimestrielle ou annuelle sur 20
- N'invente PAS de notes, extrais uniquement ce qui est écrit
- Si une matière a plusieurs notes (interros, exam...), prends la MOYENNE finale
- Inclure TOUTES les matières : EPS, Culture Manuelle (CM), Conduite, Arts Plastiques, Musique, etc.
- Les coefficients ne doivent PAS avoir de zéro devant

CAS SPÉCIAL — FRANÇAIS (oral et écrit séparés) :
- Si le bulletin présente deux lignes distinctes "Français Écrit" et "Français Oral" (ou "Composition Français" et "Oral Français"), retourne-les comme deux entrées séparées :
  {{"matiere": "Français Écrit", "moyenne": 12.0}},
  {{"matiere": "Français Oral", "moyenne": 13.0}}
- Si une seule ligne "Français" ou "Composition Français" existe, retourne-la telle quelle :
  {{"matiere": "Français", "moyenne": 12.5}}
- Ne fusionne JAMAIS toi-même oral et écrit : laisse le système calculer la moyenne."""


# ─────────────────────────────────────────────────────────────
# VALIDATION DE SÉRIE
# ─────────────────────────────────────────────────────────────

# Séries valides du BAC ivoirien
_SERIES_VALIDES = {'A1', 'A2', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'TI'}

# Matières caractéristiques de chaque série (pour détecter une incohérence)
_MATIERES_SERIE = {
    'A1': {'Français', 'Philosophie', 'Histoire-Géographie', 'Anglais'},
    'A2': {'Français', 'Philosophie', 'Histoire-Géographie', 'Anglais'},
    'C':  {'Mathématiques', 'Physique-Chimie', 'SVT'},
    'D':  {'Mathématiques', 'Physique-Chimie', 'SVT'},
    'E':  {'Mathématiques', 'Physique-Chimie', 'Sciences Industrielles'},
    'F1': {'Mathématiques', 'Physique', 'Dessin Technique', 'Construction Mécanique'},
    'F2': {'Mathématiques', 'Physique', 'Électronique', 'Électrotechnique'},
    'F3': {'Mathématiques', 'Physique', 'Génie Civil', 'Dessin Technique'},
    'F4': {'Mathématiques', 'Physique', 'Topographie'},
    'G1': {'Comptabilité', 'Économie-Gestion'},
    'G2': {'Économie-Gestion', 'Gestion Commerciale'},
    'TI': {'Informatique', 'Mathématiques', 'Physique'},
}

# Matières qui, si présentes, excluent certaines séries
_MATIERES_EXCLUSIVES = {
    'Physique-Chimie':       {'A1', 'A2', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'TI'},  # séries sans PC
    'SVT':                   {'A1', 'A2', 'E', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'TI'},
    'Sciences Industrielles': {'A1', 'A2', 'C', 'D', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'TI'},
    'Comptabilité':          {'A1', 'A2', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G2', 'TI'},
    'Gestion Commerciale':   {'A1', 'A2', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G1', 'TI'},
    'Informatique':          {'A1', 'A2', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2'},
}


def _valider_serie_document(notes_extraites: dict, serie_declaree: str) -> dict | None:
    """
    Vérifie si les matières extraites sont cohérentes avec la série déclarée.
    Retourne None si OK, sinon un dict d'erreur.
    """
    if not serie_declaree or serie_declaree not in _SERIES_VALIDES:
        return None  # Pas de série déclarée → on ne bloque pas

    serie = serie_declaree.upper()
    matieres_doc = set(notes_extraites.keys())

    # Vérifier les matières exclusives : une matière présente dans le doc
    # qui est incompatible avec la série déclarée → incohérence forte
    for matiere, series_incompatibles in _MATIERES_EXCLUSIVES.items():
        if matiere in matieres_doc and serie in series_incompatibles:
            return {
                'success': False,
                'error': (
                    f"❌ Ce document ne correspond pas à votre série {serie}. "
                    f"La matière « {matiere} » n'appartient pas à la série {serie}. "
                    f"Veuillez importer le bon document (série {serie})."
                ),
                'serie_conflict': True,
            }

    return None  # Tout est cohérent


# ─────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────

def analyser_document_mistral(file_obj, type_document: str, serie_bac: str = '') -> dict:
    if not settings.MISTRAL_API_KEY:
        return {'success': False, 'error': 'Clé API Mistral non configurée.'}

    client = _get_client()
    media_type = _get_media_type(file_obj)
    prompt = _build_prompt(type_document, serie_bac)

    try:
        if media_type == 'application/pdf':
            resultat = _analyser_pdf(client, file_obj, prompt, type_document)
        else:
            resultat = _analyser_image(client, file_obj, media_type, prompt, type_document)

        # ── Validation de cohérence série ──────────────────────────────
        if resultat.get('success') and serie_bac:

            # Pour le relevé BAC : comparer la série écrite sur le document
            # avec la série déclarée par l'étudiant — c'est la vérif la plus fiable
            if type_document == 'bac':
                serie_doc = ''
                etudiant = resultat.get('etudiant') or {}
                if etudiant:
                    serie_doc = (etudiant.get('serie') or '').strip().upper()

                if serie_doc and serie_doc != serie_bac.upper():
                    return {
                        'success': False,
                        'error': (
                            f"❌ Ce relevé de BAC est de série {serie_doc}, "
                            f"mais vous avez déclaré la série {serie_bac.upper()}. "
                            f"Veuillez importer le relevé correspondant à votre série {serie_bac.upper()}."
                        ),
                        'serie_conflict': True,
                    }

            # Pour tous les types : vérification par les matières présentes
            if resultat.get('notes'):
                erreur_serie = _valider_serie_document(resultat['notes'], serie_bac)
                if erreur_serie:
                    return erreur_serie

        # ──────────────────────────────────────────────────────────────

        return resultat

    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return {'success': False, 'error': f"Erreur lors de l'analyse : {str(e)}"}


def _appel_pixtral(client, data_url: str, prompt: str) -> str:
    response = client.chat.complete(
        model='pixtral-12b-2409',
        messages=[{'role': 'user', 'content': [
            {'type': 'image_url', 'image_url': {'url': data_url}},
            {'type': 'text', 'text': prompt},
        ]}],
        max_tokens=3000,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def _analyser_image(client, file_obj, media_type, prompt, type_document) -> dict:
    b64 = _encode_image_b64(file_obj)
    data_url = f"data:{media_type};base64,{b64}"
    raw = _appel_pixtral(client, data_url, prompt)
    logger.info(f"Pixtral image ({type_document}): {raw[:300]}")
    return _parser_reponse(raw, type_document)


def _analyser_pdf(client, file_obj, prompt, type_document) -> dict:
    file_obj.seek(0)
    file_content = file_obj.read()

    pages_b64 = _pdf_vers_images_b64(file_content)
    if not pages_b64:
        return {
            'success': False,
            'error': 'Impossible de lire ce PDF. Essayez une photo JPG/PNG du document.'
        }

    logger.info(f"Analyse PDF : {len(pages_b64)} page(s)")

    resultats = []
    for i, img_b64 in enumerate(pages_b64):
        data_url = f"data:image/png;base64,{img_b64}"
        try:
            raw = _appel_pixtral(client, data_url, prompt)
            logger.info(f"Page {i+1} raw: {raw[:300]}")
            r = _parser_reponse(raw, type_document)
            if r.get('success') and r.get('notes'):
                resultats.append(r)
        except Exception as e:
            logger.warning(f"Erreur page {i+1}: {e}")

    if not resultats:
        return {'success': False, 'error': 'Aucune note détectée dans le PDF.'}

    # Fusionner toutes les pages : prendre le plus complet + compléter
    meilleur = max(resultats, key=lambda r: len(r.get('notes', {})))
    for r in resultats:
        if r is meilleur: continue
        for mat, note in r.get('notes', {}).items():
            if mat not in meilleur['notes']:
                meilleur['notes'][mat] = note
        if not meilleur.get('moyenne_generale') and r.get('moyenne_generale'):
            meilleur['moyenne_generale'] = r['moyenne_generale']
        if not meilleur.get('mention') and r.get('mention'):
            meilleur['mention'] = r['mention']

    return meilleur


# ─────────────────────────────────────────────────────────────
# PARSER — gère les deux formats (liste et dict)
# ─────────────────────────────────────────────────────────────

def _parser_reponse(raw: str, type_document: str) -> dict:
    try:
        data = json.loads(_nettoyer_json(raw))

        if type_document == 'bac':
            matieres_brutes = data.get('matieres', [])
            notes_calculees = _calculer_notes_bac(matieres_brutes)

            details = []
            for item in matieres_brutes:
                nom_brut = item.get('matiere')
                if not nom_brut: continue
                nom = _normaliser_matiere(nom_brut)
                no = item.get('note_obtenue')
                co = item.get('coefficient')
                details.append({
                    'matiere':      nom,
                    'note_obtenue': no,
                    'coefficient':  co,
                    'note_sur_20':  notes_calculees.get(nom),
                })

            result = {
                'success':          True,
                'type':             'bac',
                'notes':            notes_calculees,
                'details_matieres': details,
                'moyenne_generale': _parse_float(data.get('moyenne_generale')),
                'mention':          data.get('mention'),
                'etudiant':         data.get('etudiant', {}),
                'trimestre':        None,
            }

        else:
            # Nouveau format : liste de {matiere, moyenne}
            matieres_liste = data.get('matieres', [])
            notes_brutes = {}

            if matieres_liste:
                # Format liste libre (nouveau prompt)
                for item in matieres_liste:
                    nom = item.get('matiere') or item.get('nom') or item.get('name')
                    note = item.get('moyenne') or item.get('note') or item.get('moy')
                    if nom and note is not None:
                        notes_brutes[nom] = note
            else:
                # Fallback : ancien format dict
                notes_brutes = data.get('notes', {})

            notes_propres = _normaliser_notes_bulletin(notes_brutes)

            result = {
                'success':          True,
                'type':             'bulletin',
                'notes':            notes_propres,
                'details_matieres': [],
                'trimestre':        data.get('trimestre', type_document),
                'moyenne_generale': _parse_float(data.get('moyenne_generale')),
                'mention':          None,
                'etudiant':         data.get('etudiant', {}),
            }

        nb_notes = len(result.get('notes', {}))
        logger.info(f"Parser OK — {nb_notes} notes extraites pour {type_document}")

        if not result['notes']:
            result['warning'] = "Aucune note lisible. Essayez une image plus nette."

        return result

    except json.JSONDecodeError as e:
        cleaned = _nettoyer_json(raw)
        logger.error(f"JSON parse error: {e}\nCleaned: {cleaned[:600]}")
        return {
            'success': False,
            'error':   "L'IA n'a pas pu structurer les données. Essayez une image plus nette.",
        }