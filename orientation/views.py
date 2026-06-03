from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .models import (
    Utilisateur, ProfilBachelier, Matiere,
    NoteBachelier, NoteTrimestrielle, MoyenneBulletin,
    FiliereOrientation, PonderationMatiere, Recommandation,
    Concours, RecommandationConcours
)
import json
from decimal import Decimal
from django.http import HttpResponse
# Ajouter ces imports en haut de views.py
from .services.mistral_service import analyser_document_mistral
import magic
from django.http import JsonResponse
from django.views.decorators.http import require_POST



MATIERES_PAR_SERIE = {
    "A1": ["Français","Philosophie","Histoire-Géographie","Anglais","Espagnol","Allemand","Mathématiques"],
    "A2": ["Français","Philosophie","Histoire-Géographie","Anglais","Espagnol","Mathématiques"],
    "C":  ["Mathématiques","Physique-Chimie","SVT","Français","Philosophie","Histoire-Géographie"],
    "D":  ["Mathématiques","Physique-Chimie","SVT","Français","Philosophie","Histoire-Géographie"],
    "E":  ["Mathématiques","Physique-Chimie","Sciences Industrielles","Français","Philosophie","Histoire-Géographie"],
    "F1": ["Mathématiques","Physique","Dessin Technique","Construction Mécanique","Français","Philosophie"],
    "F2": ["Mathématiques","Physique","Électronique","Électrotechnique","Français","Philosophie"],
    "F3": ["Mathématiques","Physique","Génie Civil","Dessin Technique","Français","Philosophie"],
    "F4": ["Mathématiques","Physique","Topographie","Construction","Français","Philosophie"],
    "G1": ["Comptabilité","Économie","Mathématiques","Français","Philosophie","Anglais"],
    "G2": ["Économie","Gestion Commerciale","Mathématiques","Français","Philosophie","Anglais"],
    "TI": ["Informatique","Mathématiques","Physique","Français","Philosophie"],
}

ASPIRATIONS_KEYWORDS = {
    # Filières génériques
    'MED-001':  ['médecin','médecine','chirurgie','santé','hôpital','docteur','pédiatre'],
    'PHAR-001': ['pharmacie','pharmacien','médicament','laboratoire','pharma'],
    'INFO-001': ['informatique','développeur','programmeur','code','logiciel','data','ia','tech','numérique'],
    'DROIT-001':['droit','avocat','juriste','justice','loi','notaire','magistrat'],
    'ECO-001':  ['économie','finance','banque','économiste','analyste','investissement'],
    'GEST-001': ['gestion','management','manager','entreprise','marketing','rh','commerce','entrepreneur'],
    # UNA
    'UNA-BIO':      ['biologie','biologiste','sciences naturelles','laboratoire','recherche','SVT'],
    'UNA-BIOCHIM':  ['biochimie','biochimiste','laboratoire','chimie','analyse','pharmacie'],
    'UNA-BOTANIQUE':['botanique','plantes','agriculture','agronomie','végétaux','nature','CNRA'],
    'UNA-ZOOLOGIE': ['zoologie','animaux','élevage','production animale','vétérinaire'],
    'UNA-ENVIR':    ['environnement','écologie','développement durable','nature','ressources naturelles'],
    'UNA-INFO':     ['informatique','développeur','code','tech','numérique','réseau','IA'],
    'UNA-MIAGE':    ['informatique','gestion','systèmes information','ERP','développement','MIAGE'],
    'UNA-MATHS':    ['mathématiques','maths','calcul','statistiques','analyse','actuariat'],
    'UNA-PHYSIQUE': ['physique','sciences','recherche','ingénieur','technologie'],
    'UNA-CHIMIE':   ['chimie','laboratoire','chimiste','analyse chimique','industrie'],
    'UNA-STA':      ['alimentation','agroalimentaire','nutrition','qualité','technologie alimentaire'],
    'UNA-EPSS':     ['médecine','pharmacie','santé','chirurgie','santé publique','EPSS'],
    # UFHB
    'UFHB-MEDECINE':['médecin','médecine','chirurgie','santé','hôpital','docteur','chirurgien'],
    'UFHB-PHARMA':  ['pharmacie','pharmacien','médicament','pharma','laboratoire'],
    'UFHB-ODONTO':  ['dentiste','odontologie','chirurgie dentaire','dents','orthodontie'],
    'UFHB-MATHS':   ['mathématiques','maths','calcul','statistiques','actuariat','analyse'],
    'UFHB-INFO':    ['informatique','développeur','réseau','tech','numérique','IA','data'],
    'UFHB-PHYSIQUE':['physique','sciences','ingénieur','recherche','technologie'],
    'UFHB-CHIMIE':  ['chimie','laboratoire','chimiste','industrie','analyse'],
    'UFHB-GEO':     ['géologie','mines','minéraux','pétrole','ressources minières','géologue'],
    'UFHB-BIOSCI':  ['biologie','microbiologie','biotechnologie','laboratoire','recherche'],
    'UFHB-ECO':     ['économie','finance','comptabilité','banque','gestion','marketing','commerce'],
    'UFHB-DROIT':   ['droit','avocat','juriste','justice','loi','notaire','magistrat','tribunal'],
    'UFHB-SCIPO':   ['sciences politiques','diplomatie','politique','relations internationales','ONU'],
    'UFHB-LETTRES': ['lettres','littérature','français','auteur','enseignement','culture'],
    'UFHB-LANGUES': ['langues','traduction','interprète','anglais','espagnol','allemand','linguistique'],
    'UFHB-COMM':    ['communication','journalisme','médias','publicité','presse','relations publiques'],
    'UFHB-PSYCHO':  ['psychologie','psychologue','sociologie','conseil','accompagnement','social'],
    'UFHB-CRIMI':   ['criminologie','crime','justice','victime','réinsertion','sécurité'],
    # UIB
    'UIB-INFO':     ['informatique','développeur','réseau','télécoms','logiciel','tech'],
    'UIB-FINANCE':  ['finance','comptabilité','banque','audit','gestion','économie'],
    'UIB-GESTION':  ['gestion','management','marketing','RH','ressources humaines','entreprise'],
    'UIB-DROIT':    ['droit','avocat','juriste','loi','justice','administration'],
    # Pigier
    'PIGIER-COMPTA':  ['comptabilité','finance','audit','gestion','fiscalité','expert-comptable'],
    'PIGIER-MARKET':  ['marketing','communication','publicité','commerce','vente','digital'],
    'PIGIER-RH':      ['ressources humaines','RH','management','assistanat','gestion','direction'],
    'PIGIER-INFO':    ['informatique','développeur','réseau','web','logiciel','tech'],
    'PIGIER-TOURISME':['tourisme','hôtellerie','voyage','accueil','hôtel','restauration'],
    # IIPEA
    'IIPEA-INFO':      ['informatique','IA','intelligence artificielle','cybersécurité','réseau','développeur'],
    'IIPEA-GESTION':   ['gestion','comptabilité','finance','marketing','ressources humaines','entreprise'],
    'IIPEA-DROIT':     ['droit','administration','juriste','loi','fonctionnaire','justice'],
    'IIPEA-LOGISTIQUE':['logistique','supply chain','commerce international','douane','transport','import'],
}

COMPAT_SERIE = {
    # ── Filières génériques ──
    'MED-001':  ['C','D'],
    'PHAR-001': ['C','D'],
    'INFO-001': ['C','D','G1','G2','TI','E'],
    'DROIT-001':['A1','A2','G1','G2'],
    'ECO-001':  ['C','D','G1','G2'],
    'GEST-001': ['G1','G2','A2','C','D'],
    'INPHB-INFO':       ['C','D','E','TI'],
    'INPHB-GENIE-CIVIL':['C','D','E','F3'],
    'INPHB-AGRO':       ['C','D'],
    'INPHB-ELECTRO':    ['C','D','E','F2'],
    'UFHB-MEDECINE':    ['C','D'],
    'UFHB-DROIT':       ['A1','A2','C','D','G1','G2'],
    'UFHB-PHARMA':      ['C','D'],
    'UVCI-INFO':        ['C','D','G1','G2','TI'],
    'BTS-COMPTA':   ['G1','G2','A2','C','D'],
    'BTS-INFO':     ['C','D','G1','G2','TI'],
    'BTS-COMMERCE': ['G2','A2','C','D'],
    'BTS-TELECOM':  ['C','D','E','F2','TI'],
    'BTS-BANK':     ['G1','G2','C','D'],
    'ESC-ABIDJAN':  ['G1','G2','A2','C','D'],
    'INFAS':        ['C','D'],
    # ── UNA — Université Nangui Abrogoua ──
    'UNA-BIO':      ['C','D'],
    'UNA-BIOCHIM':  ['C','D'],
    'UNA-BOTANIQUE':['C','D'],
    'UNA-ZOOLOGIE': ['C','D'],
    'UNA-ENVIR':    ['C','D','E'],
    'UNA-INFO':     ['C','D','E'],
    'UNA-MIAGE':    ['C','D','E','G1','G2'],
    'UNA-MATHS':    ['C','D','E'],
    'UNA-PHYSIQUE': ['C','D','E'],
    'UNA-CHIMIE':   ['C','D'],
    'UNA-STA':      ['C','D'],
    'UNA-EPSS':     ['C','D'],
    # ── UFHB — Université Félix Houphouët-Boigny ──
    'UFHB-MEDECINE':['C','D'],
    'UFHB-PHARMA':  ['C','D'],
    'UFHB-ODONTO':  ['C','D'],
    'UFHB-MATHS':   ['C','D','E'],
    'UFHB-INFO':    ['C','D','E'],
    'UFHB-PHYSIQUE':['C','D','E'],
    'UFHB-CHIMIE':  ['C','D'],
    'UFHB-GEO':     ['C','D'],
    'UFHB-BIOSCI':  ['C','D'],
    'UFHB-ECO':     ['A1','C','D','G1','G2'],
    'UFHB-DROIT':   ['A1','A2'],
    'UFHB-SCIPO':   ['A1','A2'],
    'UFHB-LETTRES': ['A1','A2'],
    'UFHB-LANGUES': ['A1','A2'],
    'UFHB-COMM':    ['A1','A2'],
    'UFHB-PSYCHO':  ['A1','A2'],
    'UFHB-CRIMI':   ['A1','A2'],
    # ── UIB — Université Internationale de Bouaké ──
    'UIB-INFO':     ['A1','A2','C','D','G1','G2'],
    'UIB-FINANCE':  ['A1','A2','C','D','G1','G2'],
    'UIB-GESTION':  ['A1','A2','C','D','G1','G2'],
    'UIB-DROIT':    ['A1','A2','C','D','G1','G2'],
    # ── Pigier Côte d'Ivoire ──
    'PIGIER-COMPTA':  ['A1','A2','C','D','G1','G2','F1','F2','F3'],
    'PIGIER-MARKET':  ['A1','A2','C','D','G1','G2'],
    'PIGIER-RH':      ['A1','A2','C','D','G1','G2'],
    'PIGIER-INFO':    ['A1','A2','C','D','G1','G2','F1','F2'],
    'PIGIER-TOURISME':['A1','A2','C','D','G1','G2'],
    # ── IIPEA ──
    'IIPEA-INFO':      ['A1','A2','C','D','E','F1','F2','G1','G2'],
    'IIPEA-GESTION':   ['A1','A2','C','D','G1','G2'],
    'IIPEA-DROIT':     ['A1','A2','C','D','G1','G2'],
    'IIPEA-LOGISTIQUE':['A1','A2','C','D','G1','G2'],
}

# Familles

# Familles de séries — définies une seule fois
SERIES_SCIENTIFIQUES = ['C','D','E','F1','F2','F3','F4']
SERIES_LITTERAIRES   = ['A1','A2']
SERIES_COMMERCIALES  = ['G1','G2']
SERIES_TECH_INFO     = ['TI']


def accueil(request):
    return render(request, 'orientation/accueil.html')


def inscription(request):
    if request.method == 'POST':
        nom      = request.POST.get('nom','').strip()
        prenom   = request.POST.get('prenom','').strip()
        username = request.POST.get('username','').strip()
        email    = request.POST.get('email','').strip()
        pwd      = request.POST.get('password','')
        pwd_confirm = request.POST.get('password_confirm','')

        erreurs = []
        if not nom or not prenom or not username or not email:
            erreurs.append("Tous les champs obligatoires doivent être remplis.")
        if len(pwd) < 8:
            erreurs.append("Le mot de passe doit contenir au moins 8 caractères.")
        if pwd != pwd_confirm:
            erreurs.append("Les mots de passe ne correspondent pas.")
        if Utilisateur.objects.filter(email_util=email).exists():
            erreurs.append("Cet email est déjà utilisé.")
        if Utilisateur.objects.filter(username=username).exists():
            erreurs.append("Ce nom d'utilisateur est déjà pris.")

        if erreurs:
            for e in erreurs:
                messages.error(request, e)
            return render(request, 'orientation/inscription.html', {
                'nom': nom, 'prenom': prenom,
                'username': username, 'email': email
            })

        utilisateur = Utilisateur.objects.create(
            email_util=email, username=username,
            nom_util=nom, prenom_util=prenom,
            pwd_util=make_password(pwd),
        )
        request.session['user_id'] = utilisateur.id
        messages.success(request, f"Bienvenue {prenom} ! Complète ton profil BAC.")
        return redirect('profil')

    return render(request, 'orientation/inscription.html')


def connexion(request):
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant','').strip()
        pwd = request.POST.get('password','')
        try:
            if '@' in identifiant:
                utilisateur = Utilisateur.objects.get(email_util=identifiant)
            else:
                utilisateur = Utilisateur.objects.get(username=identifiant)
            if check_password(pwd, utilisateur.pwd_util):
                request.session['user_id'] = utilisateur.id
                utilisateur.derniere_connexion = timezone.now()
                utilisateur.save()
                return redirect('dashboard')
            else:
                messages.error(request, "Mot de passe incorrect.")
        except Utilisateur.DoesNotExist:
            messages.error(request, "Aucun compte avec cet identifiant.")
    return render(request, 'orientation/connexion.html')


def deconnexion(request):
    request.session.flush()
    return redirect('accueil')


def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')
    utilisateur = Utilisateur.objects.get(id=user_id)
    try:
        profil_bac = ProfilBachelier.objects.get(utilisateur=utilisateur)
        top3 = Recommandation.objects.filter(
            utilisateur=utilisateur
        ).order_by('-score_compatibilite')[:3]
        notes = NoteBachelier.objects.filter(
            profil_bachelier=profil_bac
        ).select_related('matiere').order_by('matiere__nom_matiere')
        notes_count = notes.count()
    except ProfilBachelier.DoesNotExist:
        profil_bac = None
        top3 = []
        notes = []
        notes_count = 0
    return render(request, 'orientation/dashboard.html', {
        'utilisateur': utilisateur,
        'profil': profil_bac,
        'top3': top3,
        'notes': notes,
        'notes_count': notes_count,
    })


def profil(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')

    utilisateur = Utilisateur.objects.get(id=user_id)
    toutes_matieres = {m.nom_matiere: m.id for m in Matiere.objects.all()}

    if request.method == 'POST':
        serie         = request.POST.get('serie_bac')
        mention       = request.POST.get('mention_bac') or None
        moyenne       = request.POST.get('moyenne_bac')
        annee         = request.POST.get('annee_bac')
        etablissement = request.POST.get('etablissement_bac')
        aspirations   = request.POST.get('aspirations_bac')

        profil_bac, _ = ProfilBachelier.objects.update_or_create(
            utilisateur=utilisateur,
            defaults={
                'serie_bac': serie,
                'mention_bac': mention,
                'moyenne_bac': moyenne,
                'annee_bac': annee,
                'etablissement_bac': etablissement,
                'aspirations_bac': aspirations,
            }
        )

        NoteBachelier.objects.filter(profil_bachelier=profil_bac).delete()
        NoteTrimestrielle.objects.filter(profil_bachelier=profil_bac).delete()
        MoyenneBulletin.objects.filter(profil_bachelier=profil_bac).delete()

        matieres_serie = MATIERES_PAR_SERIE.get(serie, [])
        for nom_mat in matieres_serie:
            mat_id = toutes_matieres.get(nom_mat)
            if not mat_id:
                continue
            try:
                matiere = Matiere.objects.get(id=mat_id)
            except Matiere.DoesNotExist:
                continue

            t1_val = request.POST.get(f't1_{nom_mat}')
            t2_val = request.POST.get(f't2_{nom_mat}')
            t3_val = request.POST.get(f't3_{nom_mat}')
            bac_val = request.POST.get(f'bac_{nom_mat}')

            notes_valides = {}
            for trim, val in [('T1', t1_val), ('T2', t2_val), ('T3', t3_val)]:
                if val and val.strip():
                    nf = float(val)
                    NoteTrimestrielle.objects.create(
                        profil_bachelier=profil_bac,
                        matiere=matiere,
                        trimestre=trim,
                        note=nf,
                    )
                    notes_valides[trim] = nf

            note_bac = float(bac_val) if bac_val and bac_val.strip() else None

            t1v = notes_valides.get('T1')
            t2v = notes_valides.get('T2')
            t3v = notes_valides.get('T3')

            if t1v is not None or t2v is not None or t3v is not None:
                numerateur   = (t1v or 0)*1 + (t2v or 0)*2 + (t3v or 0)*2
                denominateur = (1 if t1v else 0) + (2 if t2v else 0) + (2 if t3v else 0)
                mga = numerateur / denominateur if denominateur > 0 else 0
                if note_bac is not None:
                    note_finale = note_bac * 0.60 + mga * 0.40
                else:
                    note_finale = mga
                NoteBachelier.objects.create(
                    profil_bachelier=profil_bac,
                    matiere=matiere,
                    note_bac=round(note_finale, 2),
                    coefficient_bac=float(matiere.coeff_default),
                )
            elif note_bac is not None:
                NoteBachelier.objects.create(
                    profil_bachelier=profil_bac,
                    matiere=matiere,
                    note_bac=note_bac,
                    coefficient_bac=float(matiere.coeff_default),
                )

            for classe in ['2nde', '1ere']:
                for trim in ['T1', 'T2', 'T3']:
                    val_b = request.POST.get(f'bulletin_{classe}_{trim}_{nom_mat}')
                    if val_b and val_b.strip():
                        MoyenneBulletin.objects.create(
                            profil_bachelier=profil_bac,
                            matiere=matiere,
                            classe=classe,
                            trimestre=trim,
                            moyenne=float(val_b),
                        )

        return redirect('concours')

    try:
        profil_existant = ProfilBachelier.objects.get(utilisateur=utilisateur)
        notes_bac_exist = {
            n.matiere.nom_matiere: str(n.note_bac)
            for n in NoteBachelier.objects.filter(profil_bachelier=profil_existant)
        }
        notes_trim_exist = {}
        for nt in NoteTrimestrielle.objects.filter(profil_bachelier=profil_existant):
            notes_trim_exist[f"{nt.trimestre}_{nt.matiere.nom_matiere}"] = str(nt.note)
        bulletins_exist = {}
        for b in MoyenneBulletin.objects.filter(profil_bachelier=profil_existant):
            trim_key = f"_{b.trimestre}" if b.trimestre else ''
            bulletins_exist[f"{b.classe}{trim_key}_{b.matiere.nom_matiere}"] = str(b.moyenne)
    except ProfilBachelier.DoesNotExist:
        profil_existant = None
        notes_bac_exist = {}
        notes_trim_exist = {}
        bulletins_exist = {}

    return render(request, 'orientation/profil.html', {
        'utilisateur': utilisateur,
        'profil': profil_existant,
        'notes_bac_exist': json.dumps(notes_bac_exist),
        'notes_trim_exist': json.dumps(notes_trim_exist),
        'bulletins_exist': json.dumps(bulletins_exist),
        'matieres_par_serie': json.dumps(MATIERES_PAR_SERIE),
        'toutes_matieres': json.dumps(toutes_matieres),
    })


def concours(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')

    utilisateur = Utilisateur.objects.get(id=user_id)
    try:
        profil_bac = ProfilBachelier.objects.get(utilisateur=utilisateur)
    except ProfilBachelier.DoesNotExist:
        return redirect('profil')

    serie = profil_bac.serie_bac
    moyenne = float(profil_bac.moyenne_bac)
    notes = {
        n.matiere.nom_matiere: float(n.note_bac)
        for n in profil_bac.notes.all() if n.note_bac
    }
    note_maths = notes.get('Mathématiques', moyenne)
    note_physique = notes.get('Physique-Chimie', moyenne)
    aspirations = (profil_bac.aspirations_bac or '').lower()

    RecommandationConcours.objects.filter(utilisateur=utilisateur).delete()
    tous_concours = Concours.objects.filter(actif=True).order_by('etablissement', 'nom_concours')
    recommandations_concours = []

    for c in tous_concours:
        series_ok = [s.strip() for s in c.series_requises.split(',')]
        score = 0
        raisons = []
        blocages = []

        # 1. Série compatible ?
        if serie in series_ok:
            score += 30
            raisons.append(f"Série BAC {serie} compatible ✅")
        else:
            if serie in SERIES_LITTERAIRES and any(s in SERIES_SCIENTIFIQUES for s in series_ok):
                score -= 40
                blocages.append(f"⛔ Série {serie} (littéraire) incompatible avec ce concours scientifique (requis : {c.series_requises})")
            else:
                score -= 20
                blocages.append(f"Série {serie} non requise (requis : {c.series_requises})")

        # 2. Moyenne suffisante ?
        moy_min = float(c.moyenne_min)
        if moyenne >= moy_min:
            bonus = min((moyenne - moy_min) * 5, 20)
            score += 20 + bonus
            raisons.append(f"Moyenne {moyenne}/20 ≥ {moy_min}/20 requis ✅")
        else:
            manque = round(moy_min - moyenne, 2)
            blocages.append(f"Moyenne insuffisante : {moyenne}/20 (requis {moy_min}/20, manque {manque} points)")
            score -= 15

        # 3. Note en Maths ?
        maths_min = float(c.note_maths_min)
        if maths_min > 0:
            if note_maths >= maths_min:
                score += 20
                raisons.append(f"Maths {note_maths}/20 ≥ {maths_min}/20 requis ✅")
            else:
                blocages.append(f"Note en Maths insuffisante : {note_maths}/20 (requis {maths_min}/20)")
                score -= 10

        # 4. Note en Physique ?
        physique_min = float(c.note_physique_min)
        if physique_min > 0:
            if note_physique >= physique_min:
                score += 15
                raisons.append(f"Physique-Chimie {note_physique}/20 ≥ {physique_min}/20 requis ✅")
            else:
                blocages.append(f"Note en Physique insuffisante : {note_physique}/20 (requis {physique_min}/20)")
                score -= 10

        # 5. Aspirations ?
        mots_etablissement = {
            'INPHB': ['inphb','ingénieur','polytechnique','yamoussoukro','génie'],
            'ESATIC': ['esatic','informatique','tic','numérique','réseau','tech'],
        }
        mots = mots_etablissement.get(c.etablissement, [])
        if any(m in aspirations for m in mots):
            score += 15
            raisons.append("Correspond à tes aspirations professionnelles ✅")

        score = max(0, min(score, 100))

        if score >= 75:
            niveau = 'Excellente'
        elif score >= 55:
            niveau = 'Bonne'
        elif score >= 35:
            niveau = 'Possible'
        else:
            niveau = 'Faible'

        details = {
            'raisons': raisons,
            'blocages': blocages,
            'serie': serie,
            'moyenne': str(moyenne),
            'note_maths': str(note_maths),
            'note_physique': str(note_physique),
        }

        reco = RecommandationConcours.objects.create(
            utilisateur=utilisateur,
            concours=c,
            score_admission=round(score, 2),
            niveau_chance=niveau,
            details=details,
        )
        recommandations_concours.append(reco)

    recommandations_concours.sort(key=lambda r: r.score_admission, reverse=True)
    inphb  = [r for r in recommandations_concours if r.concours.etablissement == 'INPHB'  and r.score_admission >= 30]
    esatic = [r for r in recommandations_concours if r.concours.etablissement == 'ESATIC' and r.score_admission >= 30]
    etat   = [r for r in recommandations_concours if r.concours.etablissement == 'ETAT'   and r.score_admission >= 20]

    # Top 3 : fusion TOUTES listes, triée par score décroissant
    top3_concours = sorted(
        inphb + esatic + etat,
        key=lambda r: r.score_admission,
        reverse=True
    )[:3]

    return render(request, 'orientation/concours.html', {
        'utilisateur': utilisateur,
        'profil': profil_bac,
        'top3_concours': top3_concours,
        'inphb': inphb,
        'esatic': esatic,
        'etat': etat,
        'note_maths': note_maths,
        'note_physique': note_physique,
    })


def resultats(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')

    utilisateur = Utilisateur.objects.get(id=user_id)
    try:
        profil_bac = ProfilBachelier.objects.get(utilisateur=utilisateur)
    except ProfilBachelier.DoesNotExist:
        return redirect('profil')

    notes = {
        n.matiere_id: float(n.note_bac)
        for n in profil_bac.notes.all() if n.note_bac
    }
    filieres = FiliereOrientation.objects.filter(actif_filiere=True)
    Recommandation.objects.filter(utilisateur=utilisateur).delete()
    aspirations_text = (profil_bac.aspirations_bac or '').lower()

    recommandations = []
    for filiere in filieres:
        ponderations = PonderationMatiere.objects.filter(filiere=filiere)
        serie   = profil_bac.serie_bac
        moyenne = float(profil_bac.moyenne_bac)

        if ponderations.exists():
            score_mat = 0
            poids_total = 0
            for p in ponderations:
                note = notes.get(p.matiere_id, moyenne)
                score_mat   += note * float(p.coeff_importance)
                poids_total += float(p.coeff_importance) * 20
            score_matieres = (score_mat / poids_total * 100) if poids_total > 0 else (moyenne / 20 * 100)
        else:
            score_matieres = moyenne / 20 * 100

        score_moyenne = moyenne / 20 * 100

        # COMPOSANTE 3 — Compatibilité série BAC (25%)
        series_compat = COMPAT_SERIE.get(filiere.code_filiere, [])

        if serie in series_compat:
            score_serie = 100
        elif not series_compat:
            score_serie = 60
        else:
            serie_famille = (
                'litteraire' if serie in SERIES_LITTERAIRES else
                'scientifique' if serie in SERIES_SCIENTIFIQUES else
                'commerciale' if serie in SERIES_COMMERCIALES else
                'tech'
            )
            compat_famille = (
                'litteraire' if any(s in SERIES_LITTERAIRES for s in series_compat) else
                'scientifique' if any(s in SERIES_SCIENTIFIQUES for s in series_compat) else
                'commerciale' if any(s in SERIES_COMMERCIALES for s in series_compat) else
                'mixte'
            )

            if serie_famille == 'litteraire' and compat_famille == 'scientifique':
                score_serie = 5
            elif serie_famille == 'scientifique' and compat_famille == 'litteraire':
                score_serie = 10
            elif serie_famille == compat_famille:
                score_serie = 40
            else:
                score_serie = 20

        keywords = ASPIRATIONS_KEYWORDS.get(filiere.code_filiere, [])
        if aspirations_text and keywords:
            matches = sum(1 for kw in keywords if kw in aspirations_text)
            score_aspiration = min(matches / len(keywords) * 100, 100)
        else:
            score_aspiration = 50

        score_final = (
            score_matieres   * 0.50 +
            score_moyenne    * 0.10 +
            score_serie      * 0.25 +
            score_aspiration * 0.15
        )
        score_final = round(min(score_final, 100), 2)

        if score_final >= 80:
            niveau = 'Excellente'
        elif score_final >= 60:
            niveau = 'Bonne'
        elif score_final >= 40:
            niveau = 'Moyenne'
        else:
            niveau = 'Faible'

        details = {
            'serie_bac': serie,
            'moyenne_bac': str(profil_bac.moyenne_bac),
            'score_matieres': round(score_matieres, 2),
            'score_moyenne': round(score_moyenne, 2),
            'score_serie': score_serie,
            'score_aspiration': round(score_aspiration, 2),
        }

        reco = Recommandation.objects.create(
            utilisateur=utilisateur,
            filiere=filiere,
            score_compatibilite=score_final,
            niveau_reco=niveau,
            details_analyse=details,
        )
        recommandations.append(reco)

    recommandations.sort(key=lambda r: r.score_compatibilite, reverse=True)
    recommandations = [r for r in recommandations if r.score_compatibilite >= 50]

    return render(request, 'orientation/resultats.html', {
        'utilisateur': utilisateur,
        'profil': profil_bac,
        'recommandations': recommandations,
    })


def detail_filiere(request, filiere_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')

    utilisateur = Utilisateur.objects.get(id=user_id)
    try:
        filiere = FiliereOrientation.objects.get(id=filiere_id)
    except FiliereOrientation.DoesNotExist:
        return redirect('resultats')

    try:
        reco = Recommandation.objects.get(utilisateur=utilisateur, filiere=filiere)
    except Recommandation.DoesNotExist:
        reco = None

    ponderations = PonderationMatiere.objects.filter(
        filiere=filiere
    ).select_related('matiere').order_by('-coeff_importance')

    try:
        profil_bac = ProfilBachelier.objects.get(utilisateur=utilisateur)
        notes = {
            n.matiere_id: float(n.note_bac)
            for n in NoteBachelier.objects.filter(profil_bachelier=profil_bac)
            if n.note_bac
        }
    except ProfilBachelier.DoesNotExist:
        profil_bac = None
        notes = {}

    matieres_detail = []
    for p in ponderations:
        note = notes.get(p.matiere_id)
        matieres_detail.append({
            'nom': p.matiere.nom_matiere,
            'coeff': float(p.coeff_importance),
            'note': note,
            'sur20': f"{note}/20" if note is not None else "Non renseignée",
            'statut': 'bon' if note and note >= 14 else ('moyen' if note and note >= 10 else 'faible'),
        })

    return render(request, 'orientation/detail_filiere.html', {
        'utilisateur': utilisateur,
        'filiere': filiere,
        'reco': reco,
        'matieres_detail': matieres_detail,
        'profil': profil_bac,
    })

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'application/pdf'
}


@require_POST
def analyser_bulletin(request):
    """
    Endpoint POST /analyser-bulletin/
    Reçoit une image ou PDF, appelle Mistral, retourne les notes en JSON.

    Pour le BAC : retourne notes calculées (note_obtenue / coefficient)
    Pour T1/T2/T3 : retourne les moyennes trimestrielles sur 20
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse(
            {'success': False, 'error': 'Non authentifié.'}, status=401
        )

    fichier = request.FILES.get('bulletin_image')
    if not fichier:
        return JsonResponse(
            {'success': False, 'error': 'Aucun fichier reçu.'}, status=400
        )

    # Vérification taille
    if fichier.size > MAX_FILE_SIZE:
        return JsonResponse({
            'success': False,
            'error': f'Fichier trop volumineux (max 10 Mo). '
                     f'Taille reçue : {fichier.size // 1024} Ko.'
        }, status=400)

    # Vérification par extension (sans python-magic)
    nom = fichier.name.lower()
    if not nom.endswith(('.jpg', '.jpeg', '.png', '.webp', '.pdf')):
        return JsonResponse({
            'success': False,
            'error': 'Format non supporté. Utilisez JPG, PNG, WebP ou PDF.'
        }, status=400)

    # Paramètres
    type_document = request.POST.get('type_document', 'T1')
    serie_bac = (request.POST.get('serie_bac', '') or '').strip().upper()

    if type_document not in ['bac', 'T1', 'T2', 'T3', 'bulletin_2nde_T1', 'bulletin_2nde_T2', 'bulletin_2nde_T3', 'bulletin_1ere_T1', 'bulletin_1ere_T2', 'bulletin_1ere_T3']:
        type_document = 'T1'

    # ─ Série : fallback BDD si le JS ne l'a pas envoyée ─────────────
    if not serie_bac:
        try:
            profil_obj = ProfilBachelier.objects.get(utilisateur__id=user_id)
            serie_bac = (profil_obj.serie_bac or '').strip().upper()
        except Exception:
            serie_bac = ''

    # ─ Bloquer si aucune série connue ────────────────────────────────
    if not serie_bac:
        return JsonResponse({
            'success': False,
            'error': (
                "⚠️ Aucune série BAC renseignée. "
                "Veuillez d'abord choisir votre série à l'étape 1 avant d'importer un document."
            )
        }, status=400)

    # Appel Mistral (la validation de cohérence série est dans le service)
    resultat = analyser_document_mistral(fichier, type_document, serie_bac)
    return JsonResponse(resultat)

def telecharger_fiche(request):
    """Génère et télécharge la fiche de recommandation en HTML imprimable."""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('connexion')

    utilisateur = Utilisateur.objects.get(id=user_id)
    try:
        profil_bac = ProfilBachelier.objects.get(utilisateur=utilisateur)
    except ProfilBachelier.DoesNotExist:
        return redirect('profil')

    recommandations = list(
        Recommandation.objects.filter(utilisateur=utilisateur)
        .order_by('-score_compatibilite')[:10]
    )
    recommandations_concours = list(
        RecommandationConcours.objects.filter(utilisateur=utilisateur)
        .order_by('-score_admission')[:5]
    )

    from django.template.loader import render_to_string
    html = render_to_string('orientation/fiche_recommandation.html', {
        'utilisateur': utilisateur,
        'profil': profil_bac,
        'recommandations': recommandations,
        'recommandations_concours': recommandations_concours,
    })
    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    response['Content-Disposition'] = f'inline; filename="fiche_AIOA_{utilisateur.username}.html"'
    return response