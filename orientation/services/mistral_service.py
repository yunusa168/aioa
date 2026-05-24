import base64
import json
import logging
import re

from mistralai import Mistral
from django.conf import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────

def _encode_image_b64(file_obj) -> str:
    file_obj.seek(0)
    return base64.standard_b64encode(file_obj.read()).decode('utf-8')


def _get_media_type(file_obj) -> str:
    name = getattr(file_obj, 'name', '').lower()
    if name.endswith('.png'):
        return 'image/png'
    if name.endswith('.webp'):
        return 'image/webp'
    if name.endswith('.pdf'):
        return 'application/pdf'
    return 'image/jpeg'


def _parse_float(val):
    if val is None:
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None


def _nettoyer_json(raw: str) -> str:
    raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*$', '', raw, flags=re.MULTILINE)
    return raw.strip()


def _valider_notes(notes_brutes: dict) -> dict:
    """Valide les notes entre 0 et 20."""
    notes_propres = {}
    for matiere, note in notes_brutes.items():
        if note is not None:
            try:
                valeur = float(note)
                if 0 <= valeur <= 20:
                    notes_propres[matiere] = round(valeur, 2)
            except (ValueError, TypeError):
                pass
    return notes_propres


def _calculer_notes_bac(matieres_brutes: list) -> dict:
    """
    Pour chaque matière du relevé BAC :
    - Lit la note obtenue et le coefficient
    - Calcule : note_sur_20 = note_obtenue / coefficient
    - Retourne un dict {nom_matiere: note_sur_20}
    """
    notes_calculees = {}
    for item in matieres_brutes:
        nom = item.get('matiere')
        note_obtenue = item.get('note_obtenue')
        coefficient = item.get('coefficient')

        if not nom:
            continue

        if note_obtenue is not None and coefficient is not None:
            try:
                n = float(note_obtenue)
                c = float(coefficient)
                if c > 0:
                    note_sur_20 = round(n / c, 2)
                    # S'assurer que le résultat est bien entre 0 et 20
                    if 0 <= note_sur_20 <= 20:
                        notes_calculees[nom] = note_sur_20
            except (ValueError, TypeError):
                pass
        elif note_obtenue is not None:
            # Si pas de coefficient, on prend la note directement
            try:
                n = float(note_obtenue)
                if 0 <= n <= 20:
                    notes_calculees[nom] = round(n, 2)
            except (ValueError, TypeError):
                pass

    return notes_calculees


# ──────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────

def _build_prompt(type_document: str, serie_bac: str) -> str:
    base = """Tu es un expert en lecture de bulletins scolaires ivoiriens.
Analyse ce document et extrais UNIQUEMENT les données demandées.
Réponds EXCLUSIVEMENT en JSON valide, sans texte avant ni après, sans balises markdown.
Si une valeur est illisible ou absente, mets null.
"""

    if type_document == 'bac':
        return base + f"""
Document : Relevé de notes du BAC ivoirien — série {serie_bac or 'inconnue'}.

IMPORTANT : Pour chaque matière, tu dois extraire :
- La NOTE OBTENUE (points bruts, ex: 42, 56, 28...)
- Le COEFFICIENT de la matière (ex: 4, 3, 2...)
- NE PAS calculer toi-même — extrais les valeurs brutes du document

Extrais exactement ce JSON :
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
    {{
      "matiere": "Nom de la matière",
      "note_obtenue": null,
      "coefficient": null
    }}
  ],
  "moyenne_generale": null,
  "mention": null
}}

Règles strictes :
- matieres : liste de TOUTES les matières visibles dans le document
- note_obtenue : la note brute (sur coefficient×20, ex: 42/80, 28/60...)
- coefficient : le coefficient officiel de la matière
- moyenne_generale : la moyenne finale sur 20
- mention : "Passable", "Assez bien", "Bien", "Très bien" ou "Excellent" uniquement
- Si la note est déjà sur 20, mets coefficient: 1 et note_obtenue = la note"""

 # Dans _build_prompt, remplace le bloc "else" final par :
    else:
        trim_label = {
            'T1': '1er trimestre — Terminale',
            'T2': '2ème trimestre — Terminale',
            'T3': '3ème trimestre — Terminale',
            'bulletin_2nde': 'bulletin annuel de Seconde',
            'bulletin_1ere': 'bulletin annuel de Première',
        }.get(type_document, '1er trimestre')

        trimestre_val = type_document if type_document in ['T1','T2','T3'] else type_document

        return base + f"""
Document : Bulletin scolaire ivoirien — {trim_label}, série {serie_bac or 'inconnue'}.

Extrais exactement ce JSON :
{{
  "type": "bulletin",
  "trimestre": "{trimestre_val}",
  "classe": null,
  "etablissement": null,
  "notes": {{
    "Mathématiques": null,
    "Physique-Chimie": null,
    "SVT": null,
    "Français": null,
    "Philosophie": null,
    "Histoire-Géographie": null,
    "Anglais": null,
    "Espagnol": null,
    "Allemand": null,
    "Informatique": null,
    "Économie-Gestion": null,
    "Comptabilité": null,
    "Gestion Commerciale": null,
    "Sciences Industrielles": null,
    "Dessin Technique": null,
    "Électronique": null,
    "Électrotechnique": null,
    "Génie Civil": null,
    "Topographie": null,
    "Construction Mécanique": null
  }},
  "moyenne_generale": null
}}

Règles strictes :
- notes : la MOYENNE annuelle ou trimestrielle de chaque matière (sur 20)
- Inclure seulement les matières visibles avec une note réelle
- Ignorer rang, appréciation, coefficient"""

# ──────────────────────────────────────────
# FONCTION PRINCIPALE
# ──────────────────────────────────────────

def analyser_document_mistral(file_obj, type_document: str, serie_bac: str = '') -> dict:
    if not settings.MISTRAL_API_KEY:
        return {'success': False, 'error': 'Clé API Mistral non configurée.'}

    client = Mistral(api_key=settings.MISTRAL_API_KEY)
    media_type = _get_media_type(file_obj)
    prompt = _build_prompt(type_document, serie_bac)

    try:
        if media_type == 'application/pdf':
            return _analyser_pdf_mistral(client, file_obj, prompt, type_document)
        return _analyser_image_mistral(client, file_obj, media_type, prompt, type_document)

    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return {'success': False, 'error': f"Erreur lors de l'analyse : {str(e)}"}


# ──────────────────────────────────────────
# ANALYSE IMAGE
# ──────────────────────────────────────────

def _analyser_image_mistral(client, file_obj, media_type, prompt, type_document) -> dict:
    image_b64 = _encode_image_b64(file_obj)
    data_url = f"data:{media_type};base64,{image_b64}"

    response = client.chat.complete(
        model='pixtral-12b-2409',
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'image_url', 'image_url': {'url': data_url}},
                    {'type': 'text', 'text': prompt},
                ],
            }
        ],
        max_tokens=2000,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    logger.info(f"Mistral Vision raw ({type_document}): {raw[:300]}")
    return _parser_reponse(raw, type_document)


# ──────────────────────────────────────────
# ANALYSE PDF
# ──────────────────────────────────────────

def _analyser_pdf_mistral(client, file_obj, prompt, type_document) -> dict:

    file_obj.seek(0)
    upload_response = client.files.upload(
        file={
            'file_name': getattr(file_obj, 'name', 'bulletin.pdf'),
            'content': file_obj.read(),
        },
        purpose='ocr',
    )
    file_id = upload_response.id
    logger.info(f"PDF uploadé, file_id: {file_id}")

    try:
        ocr_response = client.ocr.process(
            model='mistral-ocr-latest',
            document={
                'type': 'document_url',
                'document_url': f'https://api.mistral.ai/v1/files/{file_id}/content',
            },
        )
        texte_extrait = '\n\n'.join(page.markdown for page in ocr_response.pages)
        logger.info(f"OCR extrait: {len(texte_extrait)} chars")

        chat_response = client.chat.complete(
            model='mistral-small-latest',
            messages=[
                {
                    'role': 'user',
                    'content': f"{prompt}\n\nTexte extrait :\n\n{texte_extrait}",
                }
            ],
            max_tokens=2000,
            temperature=0,
        )

        raw = chat_response.choices[0].message.content.strip()
        return _parser_reponse(raw, type_document)

    finally:
        try:
            client.files.delete(file_id=file_id)
        except Exception as e:
            logger.warning(f"Impossible de supprimer fichier {file_id}: {e}")


# ──────────────────────────────────────────
# PARSER
# ──────────────────────────────────────────

def _parser_reponse(raw: str, type_document: str) -> dict:
    try:
        data = json.loads(_nettoyer_json(raw))

        if type_document == 'bac':
            # Calculer note/coefficient pour chaque matière
            matieres_brutes = data.get('matieres', [])
            notes_calculees = _calculer_notes_bac(matieres_brutes)

            # Aussi inclure les détails bruts pour debug
            details_matieres = []
            for item in matieres_brutes:
                nom = item.get('matiere')
                note_obtenue = item.get('note_obtenue')
                coeff = item.get('coefficient')
                note_sur_20 = notes_calculees.get(nom)
                if nom:
                    details_matieres.append({
                        'matiere': nom,
                        'note_obtenue': note_obtenue,
                        'coefficient': coeff,
                        'note_sur_20': note_sur_20,
                    })

            result = {
                'success': True,
                'type': 'bac',
                'notes': notes_calculees,
                'details_matieres': details_matieres,
                'moyenne_generale': _parse_float(data.get('moyenne_generale')),
                'mention': data.get('mention'),
                'etudiant': data.get('etudiant', {}),
                'trimestre': None,
            }

        else:
            # Bulletin trimestriel — notes déjà sur 20
            notes_propres = _valider_notes(data.get('notes', {}))
            result = {
                'success': True,
                'type': 'bulletin',
                'notes': notes_propres,
                'details_matieres': [],
                'trimestre': data.get('trimestre', type_document),
                'moyenne_generale': _parse_float(data.get('moyenne_generale')),
                'mention': None,
                'etudiant': {},
            }

        if not result['notes']:
            result['warning'] = "Aucune note lisible. Essayez une image plus nette."

        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e} | Raw: {raw[:500]}")
        return {
            'success': False,
            'error': "L'IA n'a pas pu structurer les données. Essayez une image plus nette.",
        }