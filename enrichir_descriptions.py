"""
Script à lancer via : python manage.py shell < enrichir_descriptions.py
Ajoute les descriptions manquantes pour toutes les filières.
"""
from orientation.models import FiliereOrientation

descriptions = {
    # ── UNA ──────────────────────────────────────────────────────
    'UNA-BIO': "Formation en biologie générale à l'Université Nangui Abrogoua d'Abidjan. Couvre la biologie cellulaire, la génétique, la physiologie animale et végétale. Débouche sur des carrières en recherche, enseignement et laboratoires.",
    'UNA-BIOCHIM': "Formation en biochimie à l'UNA couvrant la chimie des molécules du vivant, les enzymes, le métabolisme et les techniques de laboratoire. Passerelle vers la pharmacie, l'agroalimentaire et la recherche biomédicale.",
    'UNA-BOTANIQUE': "Spécialité botanique et protection des végétaux à l'UNA. Étude des plantes, de leur physiologie, de leur protection contre les maladies et ravageurs. Débouchés en agronomie, CNRA, ANADER et gestion forestière.",
    'UNA-ZOOLOGIE': "Formation en zoologie et production animale à l'UNA. Étude des animaux, de leur comportement, de leur élevage et de leur exploitation. Débouchés en élevage, vétérinaire, MIRAH et industrie agropastorale.",
    'UNA-ENVIR': "Licence et Master en gestion de l'environnement à l'UNA. Couvre l'écologie, la gestion des ressources naturelles, le droit de l'environnement et les études d'impact. Débouchés en ONG, ministère de l'Environnement et cabinets d'études.",
    'UNA-MATHS': "Formation en mathématiques pures et appliquées à l'UNA. Algèbre, analyse, probabilités, statistiques et mathématiques appliquées. Débouchés en enseignement secondaire et supérieur, actuariat, statistique et recherche.",
    'UNA-PHYSIQUE': "Licence et Master en physique à l'UNA. Mécanique, thermodynamique, électromagnétisme, physique quantique et physique appliquée. Débouchés en enseignement, recherche et industrie.",
    'UNA-CHIMIE': "Formation en physique-chimie à l'UNA. Chimie organique, inorganique, physico-chimie et techniques analytiques. Débouchés dans l'industrie chimique, agroalimentaire, pharmaceutique et l'enseignement.",
    'UNA-STA': "Licence en Sciences et Technologies des Aliments à l'UNA. Couvre la technologie alimentaire, le contrôle qualité, la microbiologie alimentaire et la nutrition. Débouchés dans l'industrie agroalimentaire ivoirienne et les laboratoires.",
    'UNA-EPSS': "École Préparatoire aux Sciences de la Santé de l'UNA. Formation de 2 ans préparant aux concours de médecine, pharmacie et odontologie. Concours d'entrée sélectif — programme intensif en biologie, chimie et physique.",
    'UNA-MATHINFO-L12': "Cycle Licence 1 & 2 en Mathématiques et Informatique à l'UNA. Bases solides en algorithmique, programmation, mathématiques discrètes et systèmes. Passerelle vers les licences spécialisées Maths ou Informatique en L3.",
    'UNA-L3-MATHS': "Licence 3 Mathématiques à l'UNA. Approfondissement en algèbre avancée, analyse réelle, probabilités et statistiques. Accessible après une L2 Mathématiques validée.",
    'UNA-L3-GENIE-INFO': "Licence 3 Informatique à l'UNA. Spécialisation en génie logiciel, bases de données, réseaux et sécurité. Accessible après une L2 Informatique ou Mathématiques-Informatique.",

    # ── UAO ──────────────────────────────────────────────────────
    'UAO-DROIT': "Formation en droit à l'Université Alassane Ouattara de Bouaké. Droit civil, pénal, commercial, constitutionnel et international. Débouchés en barreau, magistrature, notariat, administration publique et entreprises.",
    'UAO-ECO': "Licence et Master en Sciences Économiques à l'UAO. Microéconomie, macroéconomie, économétrie, finance et développement. Débouchés dans les banques, ministères, organismes internationaux et conseil.",
    'UAO-LETTRES': "Licence et Master en Lettres Modernes et Sciences du Langage à l'UAO. Littérature française et africaine, linguistique, stylistique et communication. Débouchés en enseignement, journalisme et édition.",
    'UAO-BIO': "Formation en biologie et physiologie végétales à l'UAO Bouaké. Couvre la botanique, l'agronomie, la physiologie végétale et l'écologie. Débouchés en recherche agronomique, enseignement et environnement.",
    'UAO-CHIMIE': "Licence et Master en Chimie et Biochimie à l'UAO. Chimie organique, inorganique, biochimie et techniques analytiques. Débouchés dans les laboratoires, l'industrie et l'enseignement.",
    'UAO-PSYCHO': "Formation en Psychologie et Sciences de l'Éducation à l'UAO Bouaké. Psychologie clinique, sociale, du développement et sciences de l'éducation. Débouchés en conseil scolaire, RH, ONGs et formation.",
    'UAO-STAPS': "Licence et Master en Sciences et Techniques des Activités Physiques et Sportives à l'UAO Bouaké. Formation théorique et pratique en sport, kinésiologie et management sportif. Aptitude physique requise à l'entrée.",
    'UAO-MATHINFO-L12': "Cycle L1 & L2 en Mathématiques et Informatique à l'UAO de Bouaké. Algorithmique, programmation, mathématiques et systèmes d'information. Passerelle vers les spécialisations en L3.",
    'UAO-L3-MATHS': "Licence 3 Mathématiques à l'UAO de Bouaké. Algèbre, analyse, probabilités et statistiques avancées. Accessible après une L2 Mathématiques.",
    'UAO-L3-GENIE-INFO': "Licence 3 Informatique à l'UAO de Bouaké. Génie logiciel, réseaux, bases de données et cybersécurité. Accessible après une L2 Informatique.",

    # ── UFHB ──────────────────────────────────────────────────────
    'UFHB-MATHS': "Licence et Master en Mathématiques à l'UFHB (Université de Cocody). Formation en mathématiques pures et appliquées, actuariat et statistiques. Débouchés en enseignement supérieur, BCEAO, banques et compagnies d'assurance.",
    'UFHB-PHYSIQUE': "Formation en Physique à l'UFHB. Physique fondamentale, électronique, optique et physique des matériaux. Débouchés en recherche, industrie, enseignement et télécommunications.",
    'UFHB-CHIMIE': "Licence et Master en Chimie à l'UFHB. Chimie organique, analytique et des matériaux. Débouchés en industrie pétrolière, pharmaceutique, agroalimentaire et enseignement.",
    'UFHB-GEO': "Formation en Géologie et Sciences de la Terre à l'UFHB. Pétrologie, tectonique, hydrogéologie et exploitation minière. Débouchés dans les mines, le BTP, la PETROCI et les cabinets géotechniques.",
    'UFHB-BIOSCI': "Licence et Master en Biosciences à l'UFHB. Biologie cellulaire, moléculaire, génétique et biotechnologies. Débouchés en recherche biomédicale, industrie pharmaceutique et biotechnologie.",
    'UFHB-ECO': "Licence et Master en Sciences Économiques et Gestion à l'UFHB (Université de Cocody). Économie, finance, management et comptabilité. Débouchés dans les banques, entreprises, ministères et organismes internationaux.",
    'UFHB-DROIT': "Formation en Droit à la Faculté de Droit de l'UFHB. Droit privé, public, pénal, commercial et international. L'une des facultés de droit les plus réputées de Côte d'Ivoire. Débouchés en barreau, magistrature et entreprises.",
    'UFHB-SCIPO': "Licence et Master en Sciences Politiques à l'UFHB. Relations internationales, science politique, diplomatie et administration publique. Débouchés au ministère des Affaires Étrangères, ONGs et organisations régionales.",
    'UFHB-LETTRES': "Licence et Master en Lettres Modernes à l'UFHB. Littérature française, africaine et comparée, linguistique et stylistique. Débouchés en enseignement, journalisme, édition et communication.",
    'UFHB-LANGUES': "Formation en Langues Étrangères Appliquées (Anglais, Espagnol, Allemand) à l'UFHB. Linguistique, traduction, civilisation et interprétariat. Débouchés en traduction, diplomatie, tourisme et enseignement des langues.",
    'UFHB-COMM': "Licence et Master en Communication et Journalisme à l'UFHB. Journalisme, communication institutionnelle, médias numériques et relations publiques. Débouchés dans les médias, agences de communication et entreprises.",
    'UFHB-PSYCHO': "Formation en Psychologie et Sociologie à l'UFHB. Psychologie clinique, du travail et sociale ; sociologie des organisations. Débouchés en RH, conseil, ONGs et secteur social.",
    'UFHB-CRIMI': "Licence et Master en Criminologie et Réinsertion Sociale à l'UFHB. Droit pénal, victimologie, criminologie et travail social. Débouchés en justice, système pénitentiaire et associations d'aide aux victimes.",
    'UFHB-MATHINFO-L12': "Cycle L1 & L2 en Mathématiques et Informatique à l'UFHB (Cocody). Solides bases en programmation, algorithmique et mathématiques. Passerelle vers les spécialisations en L3.",
    'UFHB-L3-MATHS': "Licence 3 Mathématiques à l'UFHB. Spécialisation en algèbre, analyse et statistiques. Accessible après une L2 Mathématiques.",
    'UFHB-L3-GENIE-INFO': "Licence 3 Informatique à l'UFHB. Génie logiciel, réseaux, IA et cybersécurité. Accessible après une L2 Informatique.",
    'UFHB-ODONTO': "Formation en Odontostomatologie (chirurgie dentaire) à l'UFHB. 6 ans d'études incluant sciences fondamentales et cliniques. Concours d'entrée très sélectif. Débouchés en cabinet privé, hôpital et CHU.",

    # ── UIB ──────────────────────────────────────────────────────
    'UIB-INFO': "Licence et Master en Informatique à l'Université Internationale de Bouaké. Réseaux, télécommunications, développement logiciel et systèmes embarqués. Formation professionnalisante orientée marché de l'emploi ivoirien.",
    'UIB-FINANCE': "Licence en Finance, Comptabilité et Banque à l'UIB Bouaké. Comptabilité générale, analyse financière, fiscalité et gestion bancaire. Formation axée sur les besoins des entreprises ivoiriennes.",
    'UIB-GESTION': "Licence en Marketing, Gestion des Entreprises et Ressources Humaines à l'UIB. Management, stratégie, marketing digital et GRH. Formation professionnelle reconnue par le milieu des entreprises.",
    'UIB-DROIT': "Licence en Droit à l'Université Internationale de Bouaké. Droit des affaires, droit social, droit public et procédures. Formation accessible et professionnalisante pour les futurs juristes d'entreprise.",

    # ── PIGIER ──────────────────────────────────────────────────────
    'PIGIER-COMPTA': "BTS et Licence en Comptabilité, Finance et Audit à Pigier Côte d'Ivoire. Formation pratique en comptabilité, contrôle de gestion, fiscalité et audit. Forte insertion professionnelle dans le tissu économique ivoirien.",
    'PIGIER-MARKET': "BTS et Licence en Marketing et Communication à Pigier CI. Techniques de vente, marketing digital, communication et gestion commerciale. Débouchés en agences de publicité, entreprises et startups.",
    'PIGIER-RH': "BTS et Licence en Gestion des Entreprises et Ressources Humaines à Pigier. Paie, recrutement, droit du travail et management. Formation très demandée par les PME et grandes entreprises ivoiriennes.",
    'PIGIER-INFO': "BTS et Licence en Réseaux et Génie Logiciel à Pigier CI. Développement web, réseaux, administration système et support. Formation orientée employabilité immédiate.",
    'PIGIER-TOURISME': "BTS et Licence en Tourisme et Hôtellerie à Pigier CI. Gestion hôtelière, tourisme d'affaires, accueil et langues. Débouchés dans les hôtels, agences de voyage et Air Côte d'Ivoire.",

    # ── IIPEA ──────────────────────────────────────────────────────
    'IIPEA-INFO': "Licence et Master en Informatique, IA, Cybersécurité et Réseaux à l'IIPEA. Formation moderne couvrant l'intelligence artificielle, la cybersécurité et le développement. Établissement reconnu par le MESRS.",
    'IIPEA-GESTION': "Licence et Master en Gestion, Comptabilité, Finance et Marketing à l'IIPEA. Formation complète en sciences de gestion avec stages obligatoires en entreprise.",
    'IIPEA-DROIT': "Licence et Master en Droit et Administration à l'IIPEA. Droit des affaires, administration publique et gestion des organisations. Formation axée sur la pratique professionnelle.",
    'IIPEA-LOGISTIQUE': "Licence et Master en Logistique et Commerce International à l'IIPEA. Supply chain, transit, douane, Incoterms et commerce extérieur. Secteur en forte croissance en Côte d'Ivoire.",

    # ── MASTERS ──────────────────────────────────────────────────────
    'UNA-M12-MIAGE': "Master MIAGE (Méthodes Informatiques Appliquées à la Gestion des Entreprises) à l'UNA. Formation Bac+5 alliant informatique et gestion. Accessible après une Licence 3 MIAGE ou équivalent. Très recherché par les DSI.",
    'UNA-M12-GENIE-INFO': "Master Génie Informatique à l'UNA. Spécialisation avancée en architecture logicielle, DevOps, IA et sécurité des systèmes. Accessible après une Licence 3 Informatique. Formation d'élite.",
    'UAO-M12-MIAGE': "Master MIAGE à l'Université Alassane Ouattara de Bouaké. Formation Bac+5 en systèmes d'information et management. Accessible après une L3 MIAGE. Excellents débouchés en ESN et grandes entreprises.",
    'UAO-M12-GENIE-INFO': "Master Génie Informatique à l'UAO de Bouaké. Architecture des systèmes, génie logiciel et intelligence artificielle. Accessible après une L3 Informatique. Formation d'ingénieur senior.",
    'UFHB-M12-MIAGE': "Master MIAGE à l'UFHB (Cocody). La MIAGE de l'UFHB est l'une des plus reconnues de Côte d'Ivoire. Formation Bac+5 en informatique de gestion. Partenariats avec les grandes entreprises d'Abidjan.",
    'UFHB-M12-GENIE-INFO': "Master Génie Informatique à l'UFHB. Formation d'excellence Bac+5 en développement avancé, cybersécurité et cloud computing. Accessible après une L3 Informatique. Forte demande des recruteurs.",

    # ── INPHB & CONCOURS ──────────────────────────────────────────────────────
    'INPHB-AGRO': "Formation d'ingénieur agronome à l'INPHB (Institut National Polytechnique Félix Houphouët-Boigny). 5 ans de formation en agronomie, agroéconomie et industrie agro-alimentaire. Concours très sélectif.",
    'INPHB-GENIE-CIVIL': "Formation d'ingénieur en Génie Civil à l'INPHB. Conception, calcul de structures, BTP et urbanisme. L'une des filières les plus prestigieuses de Côte d'Ivoire. Débouchés en cabinet d'études, BTP et fonction publique.",
    'INPHB-INFO': "Formation d'ingénieur en Informatique à l'INPHB. Développement, réseaux, IA et systèmes embarqués. Diplôme d'ingénieur reconnu internationalement. Concours très sélectif — les meilleurs bacheliers C, D, E et TI.",
}

updated = 0
not_found = []
for code, description in descriptions.items():
    count = FiliereOrientation.objects.filter(code_filiere=code).update(description=description)
    if count:
        updated += count
    else:
        not_found.append(code)

print(f"✅ {updated} filières enrichies")
if not_found:
    print(f"⚠️  Non trouvées en base : {not_found}")

# Vérifier les filières sans description restantes
sans_desc = FiliereOrientation.objects.filter(
    actif_filiere=True, description=''
).values_list('code_filiere', 'nom_filiere')
if sans_desc:
    print(f"\nFilières actives encore sans description ({len(sans_desc)}) :")
    for code, nom in sans_desc:
        print(f"  {code} | {nom}")
else:
    print("\n✅ Toutes les filières actives ont une description !")
