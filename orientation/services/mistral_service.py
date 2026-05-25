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

    # Physique-Chimie
    "physique": "Physique-Chimie", "chimie": "Physique-Chimie",
    "physique-chimie": "Physique-Chimie", "physique chimie": "Physique-Chimie",
    "pc": "Physique-Chimie", "physique & chimie": "Physique-Chimie",
    "sciences physiques": "Physique-Chimie",

    # SVT
    "svt": "SVT", "sciences de la vie": "SVT",
    "sciences naturelles": "SVT", "biologie": "SVT",
    "sciences de la vie et de la terre": "SVT", "sn": "SVT",

    # Français
    "francais": "Français", "français": "Français",
    "langue française": "Français", "fr": "Français",
    "expression française": "Français", "littérature": "Français",

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
]

def _normaliser_matiere(nom: str) -> str:
    """Normalise un nom de matière vers le nom canonique."""
    if not nom:
        return nom
    cle = nom.strip().lower()

    # 1. Correspondance directe
    if cle in CORRESPONDANCES:
        return CORRESPONDANCES[cle]

    # 2. Tester les variantes prioritaires (longues/spécifiques d'abord)
    for variante in _PRIORITES:
        if variante in cle:
            return CORRESPONDANCES.get(variante, variante.title())

    # 3. Correspondance partielle : variante >= 5 chars contenue dans le nom
    for variante, canonique in CORRESPONDANCES.items():
        if len(variante) >= 5 and variante in cle:
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
    notes = {}
    francais_ecrit = None
    francais_oral  = None

    for item in matieres_brutes:
        nom_brut = item.get("matiere", "")
        if not nom_brut: continue
        nom_lower = nom_brut.lower().strip()
        no  = item.get("note_obtenue")
        co  = item.get("coefficient")
        n20 = item.get("note_sur_20")

        # Detecter Francais Ecrit / Oral
        is_fr_ecrit = any(x in nom_lower for x in ["ecrit", "écrit"])
        is_fr_oral  = any(x in nom_lower for x in ["oral"])
        is_francais = "fran" in nom_lower

        if is_francais and is_fr_ecrit:
            try:
                if n20 is not None and 0 <= float(n20) <= 20:
                    francais_ecrit = ("n20", float(n20))
                elif no is not None and co is not None:
                    francais_ecrit = ("brut", float(no), float(co))
            except: pass
            continue

        if is_francais and is_fr_oral:
            try:
                if n20 is not None and 0 <= float(n20) <= 20:
                    francais_oral = ("n20", float(n20))
                elif no is not None and co is not None:
                    francais_oral = ("brut", float(no), float(co))
                elif no is not None:
                    francais_oral = ("n20", float(no))
            except: pass
            continue

        nom = _normaliser_matiere(nom_brut)
        try:
            if n20 is not None:
                v = float(n20)
                if 0 <= v <= 20:
                    notes[nom] = round(v, 2)
                    continue
            if no is not None and co is not None:
                n, c = float(no), float(co)
                if c > 0:
                    v = round(n / c, 2)
                    if 0 <= v <= 20:
                        notes[nom] = v
                        continue
            if no is not None:
                n = float(no)
                if 0 <= n <= 20:
                    notes[nom] = round(n, 2)
        except: pass

    # Fusionner Francais Ecrit + Oral
    if francais_ecrit or francais_oral:
        try:
            def to_sur_20(t):
                if t[0] == "n20": return t[1]
                _, n, c = t
                return round(n / c, 2) if c > 0 else None
            e20 = to_sur_20(francais_ecrit) if francais_ecrit else None
            o20 = to_sur_20(francais_oral)  if francais_oral  else None
            if e20 is not None and o20 is not None:
                notes["Français"] = round((e20 + o20) / 2, 2)
            elif e20 is not None:
                notes["Français"] = e20
            elif o20 is not None:
                notes["Français"] = o20
        except: pass

    return notes


def _normaliser_notes_bulletin(notes_brutes: dict) -> dict:
    """Normalise les clés d'un dict de notes bulletin vers les noms canoniques."""
    notes_propres = {}
    for matiere_brute, note in notes_brutes.items():
        v = _valider_note(note)
        if v is not None:
            nom_canonique = _normaliser_matiere(matiere_brute)
            notes_propres[nom_canonique] = v
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

Extrais TOUTES les lignes de matières du tableau, ligne par ligne.

════════════════════════════════════════════
RÈGLES DE CALCUL STRICTES — BAC IVOIRIEN
════════════════════════════════════════════

1. RÈGLE GÉNÉRALE : note_sur_20 = note_obtenue ÷ coefficient
   - Mathématiques : 65/100, coeff 5 → 65 ÷ 5 = 13.0
   - SVT : 12/40, coeff 2 → 12 ÷ 2 = 6.0
   - Philosophie : 18/40, coeff 2 → 18 ÷ 2 = 9.0

2. CAS SPÉCIAL — PHYSIQUE-CHIMIE (très important, erreur fréquente) :
   - La note est sur /100, le coefficient est 5
   - Calcul : note_obtenue ÷ 5 = note sur 20
   - Exemple : 50/100, coeff 5 → 50 ÷ 5 = 10.0 (PAS 50÷4, PAS 50÷100×20)
   - Vérification : le résultat DOIT être entre 0 et 20

3. CAS SPÉCIAL — FRANÇAIS (deux lignes à fusionner) :
   - "Français (Écrit)" ou "Français Écrit" : note sur /40, coeff 2
   - "Français (Oral)" ou "Français Oral" : note sur /20, coeff 1
   - Calcul de la note Français sur 20 :
     note_ecrit_sur_20 = note_ecrit ÷ 2
     note_oral_sur_20 = note_oral ÷ 1
     note_francais = (note_ecrit_sur_20 + note_oral_sur_20) ÷ 2
   - Exemple : Écrit=22/40 → 11.0 ; Oral=12/20 → 12.0 ; Français = (11+12)÷2 = 11.5
   - NE PAS créer deux entrées séparées pour oral et écrit — une seule entrée "Français"

4. ANGLAIS ORAL / AUTRES ORAUX :
   - Note directement sur /20, coeff 1 → note_sur_20 = note telle quelle
   - Exemple : Anglais Oral 13/20 → 13.0

5. EPS / ÉDUCATION PHYSIQUE :
   - Souvent noté comme bonus (+05) ou note sur /20
   - Si c'est un bonus (+05), note_sur_20 = 5.0, coefficient = 1
   - Si c'est une note normale sur /20, prendre telle quelle

6. ÉPREUVES FACULTATIVES :
   - Si la note est 00 ou nulle, ignorer cette matière
   - Sinon inclure normalement

════════════════════════════════════════════

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
    {{"matiere": "Mathématiques", "note_obtenue": 65, "coefficient": 5, "note_sur_20": 13.0}},
    {{"matiere": "Physique-Chimie", "note_obtenue": 50, "coefficient": 5, "note_sur_20": 10.0}},
    {{"matiere": "SVT", "note_obtenue": 12, "coefficient": 2, "note_sur_20": 6.0}},
    {{"matiere": "Français", "note_obtenue": null, "coefficient": 3, "note_sur_20": 11.5}},
    {{"matiere": "Philosophie", "note_obtenue": 18, "coefficient": 2, "note_sur_20": 9.0}},
    {{"matiere": "Histoire-Géographie", "note_obtenue": 24, "coefficient": 2, "note_sur_20": 12.0}},
    {{"matiere": "Anglais", "note_obtenue": 13, "coefficient": 1, "note_sur_20": 13.0}}
  ],
  "moyenne_generale": null,
  "mention": null
}}

Règles finales :
- Ajoute le champ "note_sur_20" directement dans chaque matière (tu calcules toi-même)
- note_sur_20 doit TOUJOURS être entre 0 et 20 — si ce n'est pas le cas, tu t'es trompé
- moyenne_generale = la M.G.A. écrite sur le document (sur 20)
- mention = "Passable", "Assez bien", "Bien", "Très bien" ou "Excellent"
- Les coefficients ne doivent PAS avoir de zéro devant (écrire 5, pas 05)
- Ignorer les épreuves facultatives avec note = 00"""

    else:
        labels = {
            'T1': '1er trimestre (Terminale)',
            'T2': '2ème trimestre (Terminale)',
            'T3': '3ème trimestre (Terminale)',
            'bulletin_2nde': 'Seconde',
            'bulletin_1ere': 'Première',
        }
        label = labels.get(type_document, type_document)
        return base + f"""
Document : Bulletin scolaire ivoirien — classe de {label}, série {serie_bac or 'inconnue'}.

Extrais la moyenne de CHAQUE matière visible dans le bulletin.
Utilise une liste, pas un objet fixe — comme ça tu n'oublies rien.

Format de réponse :
{{
  "type": "bulletin",
  "trimestre": "{type_document}",
  "classe": null,
  "etablissement": null,
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
- Ignore : rang, appréciation du prof, absences, conduites
- Les coefficients ne doivent PAS avoir de zéro devant"""


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
            return _analyser_pdf(client, file_obj, prompt, type_document)
        return _analyser_image(client, file_obj, media_type, prompt, type_document)
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
                'etudiant':         {},
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