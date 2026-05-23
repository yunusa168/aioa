import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aioa_project.settings')
django.setup()

from orientation.models import Concours

concours_fonction_publique = [

    # ══════════════════════════════════════════
    # ENS — École Normale Supérieure
    # ══════════════════════════════════════════
    {
        "code": "ENS-ABIDJAN",
        "nom": "Concours d'entrée ENS — École Normale Supérieure d'Abidjan",
        "etablissement": "ETAT",
        "ecole": "ENS — École Normale Supérieure d'Abidjan",
        "filiere": "Formation de professeurs du secondaire",
        "type_acces": "ecrit",
        "series": "A1, A2, C, D, E, F1, F2, G1, G2",
        "moy_min": 11.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "4 ans",
        "description": "L'ENS forme les futurs professeurs des lycées et collèges de Côte d'Ivoire. Concours national très sélectif organisé par le Ministère de l'Éducation Nationale. Les admis bénéficient d'une bourse et d'un emploi garanti à la fonction publique après formation.",
        "debouches": "Professeur de lycée, professeur de collège, conseiller pédagogique, inspecteur de l'éducation nationale",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes, extrait de casier judiciaire, certificat médical de visite, 4 photos d'identité",
        "frais": "Gratuit (concours d'État) — bourse accordée aux admis",
        "age_max": 25,
    },

    # ══════════════════════════════════════════
    # CAFOP — Formation des instituteurs
    # ══════════════════════════════════════════
    {
        "code": "CAFOP-ABIDJAN",
        "nom": "Concours d'entrée CAFOP — Centre d'Animation et de Formation Pédagogique",
        "etablissement": "ETAT",
        "ecole": "CAFOP — Centre d'Animation et de Formation Pédagogique",
        "filiere": "Formation d'instituteurs et maîtres d'école primaire",
        "type_acces": "ecrit",
        "series": "A1, A2, C, D, E, F1, F2, F3, F4, G1, G2, TI",
        "moy_min": 10.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "2 ans",
        "description": "Le CAFOP forme les instituteurs qui enseigneront dans les écoles primaires publiques de Côte d'Ivoire. Concours ouvert à tous les bacheliers. Les admis ont un emploi garanti dans la fonction publique et perçoivent une bourse pendant la formation.",
        "debouches": "Instituteur d'école primaire, directeur d'école, conseiller pédagogique du primaire",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes BAC, extrait de casier judiciaire vierge, certificat médical, 4 photos d'identité",
        "frais": "Gratuit (concours d'État) — bourse accordée aux admis",
        "age_max": 25,
    },

    # ══════════════════════════════════════════
    # POLICE NATIONALE
    # ══════════════════════════════════════════
    {
        "code": "POLICE-OFFICIER",
        "nom": "Concours d'Officier de Police — Police Nationale de Côte d'Ivoire",
        "etablissement": "ETAT",
        "ecole": "École Nationale de Police d'Abidjan",
        "filiere": "Corps des Officiers de Police",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, G1, G2",
        "moy_min": 11.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "2 ans de formation",
        "description": "Concours d'entrée dans le corps des officiers de la Police Nationale ivoirienne. Le candidat doit être de nationalité ivoirienne, avoir une bonne condition physique, un casier judiciaire vierge. La sélection comprend un écrit, un oral, des épreuves sportives et une visite médicale.",
        "debouches": "Officier de police, commissaire de police, directeur de commissariat, responsable de brigade criminelle",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes, extrait de casier judiciaire vierge, certificat médical d'aptitude physique, 4 photos d'identité, certificat de résidence",
        "frais": "Gratuit (concours d'État)",
        "age_max": 25,
    },
    {
        "code": "POLICE-GARDIEN",
        "nom": "Concours de Gardien de la Paix — Police Nationale de Côte d'Ivoire",
        "etablissement": "ETAT",
        "ecole": "École Nationale de Police d'Abidjan",
        "filiere": "Corps des Gardiens de la Paix",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, F1, F2, F3, F4, G1, G2, TI",
        "moy_min": 10.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "1 an de formation",
        "description": "Concours d'entrée dans le corps des gardiens de la paix de la Police Nationale. Ouvert à tous les bacheliers ivoiriens en bonne condition physique. Épreuves : écrit, oral, tests sportifs, visite médicale.",
        "debouches": "Gardien de la paix, agent de police, agent de sécurité publique",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, extrait de casier judiciaire vierge, certificat médical d'aptitude, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 23,
    },

    # ══════════════════════════════════════════
    # DOUANES
    # ══════════════════════════════════════════
    {
        "code": "DOUANES-INSPECTEUR",
        "nom": "Concours d'Inspecteur des Douanes — DGD Côte d'Ivoire",
        "etablissement": "ETAT",
        "ecole": "Direction Générale des Douanes — École des Douanes",
        "filiere": "Corps des Inspecteurs des Douanes",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, G1, G2",
        "moy_min": 12.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "2 ans de formation",
        "description": "Concours d'entrée dans le corps des inspecteurs de la Direction Générale des Douanes de Côte d'Ivoire. Sélection très rigoureuse : épreuves écrites (droit, économie, culture générale), épreuves physiques, entretien oral et visite médicale. Emploi garanti dans la fonction publique.",
        "debouches": "Inspecteur des douanes, chef de brigade douanière, directeur de bureau de douane, agent de lutte contre la fraude",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes, extrait de casier judiciaire vierge, certificat médical, certificat de bonne vie et mœurs, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 25,
    },
    {
        "code": "DOUANES-AGENT",
        "nom": "Concours d'Agent des Douanes — DGD Côte d'Ivoire",
        "etablissement": "ETAT",
        "ecole": "Direction Générale des Douanes — École des Douanes",
        "filiere": "Corps des Agents des Douanes",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, F1, F2, F3, F4, G1, G2, TI",
        "moy_min": 10.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "1 an de formation",
        "description": "Concours d'entrée dans le corps des agents de douane. Ouvert à tous les bacheliers ivoiriens. Épreuves : culture générale, mathématiques, français, tests physiques et visite médicale.",
        "debouches": "Agent des douanes, contrôleur douanier, agent de surveillance aux frontières",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, extrait de casier judiciaire vierge, certificat médical d'aptitude, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 23,
    },

    # ══════════════════════════════════════════
    # GENDARMERIE NATIONALE
    # ══════════════════════════════════════════
    {
        "code": "GENDARMERIE-OFFICIER",
        "nom": "Concours d'Officier de Gendarmerie — Gendarmerie Nationale CI",
        "etablissement": "ETAT",
        "ecole": "École de Gendarmerie de Côte d'Ivoire",
        "filiere": "Corps des Officiers de Gendarmerie",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, G1, G2",
        "moy_min": 12.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "2 ans de formation",
        "description": "Concours d'entrée dans le corps des officiers de la Gendarmerie Nationale de Côte d'Ivoire. Sélection très rigoureuse comprenant des épreuves écrites, des tests physiques, un entretien psychologique et une visite médicale. Les candidats doivent avoir une taille minimale (1m70 pour les hommes, 1m65 pour les femmes).",
        "debouches": "Officier de gendarmerie, commandant de brigade, directeur de compagnie, chef d'escadron",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes, extrait de casier judiciaire vierge, certificat médical d'aptitude, certificat de bonne vie et mœurs, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 25,
    },
    {
        "code": "GENDARMERIE-SOUSOFFICIER",
        "nom": "Concours de Sous-Officier de Gendarmerie — Gendarmerie Nationale CI",
        "etablissement": "ETAT",
        "ecole": "École de Gendarmerie de Côte d'Ivoire",
        "filiere": "Corps des Sous-Officiers de Gendarmerie",
        "type_acces": "mixte",
        "series": "A1, A2, C, D, E, F1, F2, F3, F4, G1, G2, TI",
        "moy_min": 10.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "1 an de formation",
        "description": "Concours d'entrée dans le corps des sous-officiers de gendarmerie. Ouvert à tous les bacheliers ivoiriens remplissant les conditions physiques. Épreuves : culture générale, français, mathématiques, tests sportifs et visite médicale.",
        "debouches": "Gendarme, brigadier, maréchal des logis, chef de poste de gendarmerie",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, extrait de casier judiciaire vierge, certificat médical d'aptitude physique, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 23,
    },

    # ══════════════════════════════════════════
    # INFAS — Santé
    # ══════════════════════════════════════════
    {
        "code": "INFAS-INFIRMIER",
        "nom": "Concours INFAS — Formation d'Infirmiers et Sages-Femmes",
        "etablissement": "ETAT",
        "ecole": "INFAS — Institut National de Formation des Agents de Santé",
        "filiere": "Soins infirmiers, Sage-femme, Technicien de santé",
        "type_acces": "ecrit",
        "series": "C, D",
        "moy_min": 11.0,
        "maths_min": 0.0,
        "physique_min": 0.0,
        "duree": "3 ans",
        "description": "Concours national d'entrée à l'INFAS pour former les futurs agents de santé de Côte d'Ivoire. Spécialités : infirmier d'État, sage-femme, technicien de laboratoire, technicien en imagerie médicale. Les admis ont un emploi garanti dans les structures sanitaires publiques.",
        "debouches": "Infirmier d'État, sage-femme, technicien de laboratoire, aide-soignant, technicien en imagerie médicale",
        "documents": "Acte de naissance, certificat de nationalité, attestation BAC séries C ou D, relevés de notes, extrait de casier judiciaire, certificat médical, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 25,
    },

    # ══════════════════════════════════════════
    # ARMÉE DE TERRE
    # ══════════════════════════════════════════
    {
        "code": "ARMEE-OFFICIER",
        "nom": "Concours d'Officier de l'Armée — Forces Armées de Côte d'Ivoire",
        "etablissement": "ETAT",
        "ecole": "École Militaire Préparatoire Technique (EMPT) / École des Officiers",
        "filiere": "Corps des Officiers de l'Armée",
        "type_acces": "mixte",
        "series": "C, D, E, F1, F2",
        "moy_min": 12.0,
        "maths_min": 11.0,
        "physique_min": 10.0,
        "duree": "3 ans de formation militaire",
        "description": "Concours d'entrée dans le corps des officiers des Forces Armées de Côte d'Ivoire. Sélection très rigoureuse : épreuves académiques, tests physiques intenses, bilan psychologique et visite médicale approfondie. Formation à l'Académie Militaire.",
        "debouches": "Officier de l'armée de terre, commandant de compagnie, état-major des armées, attaché militaire",
        "documents": "Acte de naissance, certificat de nationalité ivoirienne, attestation BAC, relevés de notes, extrait de casier judiciaire vierge, certificat médical d'aptitude militaire, 4 photos d'identité",
        "frais": "Gratuit (concours d'État)",
        "age_max": 22,
    },
]

print("=== CHARGEMENT DES CONCOURS FONCTION PUBLIQUE ===\n")

for c in concours_fonction_publique:
    obj, created = Concours.objects.update_or_create(
        code_concours=c["code"],
        defaults={
            "nom_concours": c["nom"],
            "etablissement": "ETAT",
            "ecole": c["ecole"],
            "filiere_cible": c["filiere"],
            "type_acces": c["type_acces"],
            "series_requises": c["series"],
            "moyenne_min": c["moy_min"],
            "note_maths_min": c["maths_min"],
            "note_physique_min": c["physique_min"],
            "duree_formation": c["duree"],
            "description": c["description"],
            "debouches": c["debouches"],
            "documents_requis": c["documents"],
            "frais_inscription": c["frais"],
            "age_max": c["age_max"],
            "actif": True,
        }
    )
    statut = "✅ Créé" if created else "🔄 Mis à jour"
    print(f"{statut} : {c['nom'][:65]}...")

from orientation.models import Concours as C
print(f"\n✅ TERMINÉ !")
print(f"  Total concours : {C.objects.count()}")
print(f"  Fonction publique (ETAT) : {C.objects.filter(etablissement='ETAT').count()}")
print(f"  INPHB : {C.objects.filter(etablissement='INPHB').count()}")
print(f"  ESATIC : {C.objects.filter(etablissement='ESATIC').count()}")