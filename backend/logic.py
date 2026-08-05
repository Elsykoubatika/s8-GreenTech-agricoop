"""
========================================================================
  LOGIC.PY  —  À COMPLÉTER PAR L'ÉQUIPE DATA SCIENCE
========================================================================
AgriCoop Connect — Coopérative COMAKI, Kintélé

Vous n'écrivez QUE des fonctions (ce que vous savez déjà faire : boucles,
conditions, dictionnaires). Vous ne touchez à AUCUN autre fichier.

Chaque fonction reçoit des données simples (listes, dictionnaires) et doit
RENVOYER un résultat. Pas de print, pas de input, pas de requête réseau,
pas de Flask, pas de base de données. Juste : des paramètres entrent, une
valeur sort.

Le fichier est découpé en 4 zones de responsabilité. Si vous êtes 2 Data
Scientists, une répartition équilibrée est : Personne 1 = Zone A + Zone C
(11 fonctions), Personne 2 = Zone B + Zone D (9 fonctions). Si vous êtes 3 :
Personne 1 = Zone A (6), Personne 2 = Zone B (7), Personne 3 = Zone C + D (7).

  - ZONE A : Tableau de bord & Statistiques    — 6 fonctions
  - ZONE B : Membres & Livraisons              — 7 fonctions
  - ZONE C : Ventes, Stock & Paiements         — 5 fonctions
  - ZONE D : Authentification (NOUVEAU)        — 2 fonctions

Référentiels déjà définis ci-dessous, réutilisez-les :
  PRIX_ACHAT_KG, PRIX_VENTE_KG : prix par culture (mêmes valeurs que le
  jeu de données standard).
  ACTIONS_PAR_ROLE : ce que chaque rôle a le droit de faire (module
  Authentification).

Quand vos fonctions sont correctes :
  1. les tests passent au vert   (python -m pytest -v, depuis backend/)
  2. l'API démarre et renvoie les bons résultats  (python app.py)

Remplacez chaque `pass` / `# TODO` par votre code.
========================================================================
"""

PRIX_ACHAT_KG = {
    "Manioc": 150,
    "Maïs": 200,
    "Arachide": 400,
}

PRIX_VENTE_KG = {
    "Manioc": 220,
    "Maïs": 280,
    "Arachide": 500,
}

# Ce que chaque rôle a le droit de faire (module Authentification).
# Un "rôle" correspond à un type d'utilisateur connecté ; une "action" est
# une opération précise de l'application. Si l'action demandée n'apparaît
# pas dans la liste du rôle, l'accès doit être refusé .
ACTIONS_PAR_ROLE = {
    "Secrétaire": ["gerer_comptes", "gerer_membres", "tableau_de_bord", "consulter_rapport_partenaire"],
    "Président": ["enregistrer_vente", "tableau_de_bord", "generer_rapport_partenaire"],
    "Trésorière": ["enregistrer_paiement", "tableau_de_bord"],
    "Responsable dépôt": ["enregistrer_livraison", "tableau_de_bord"],
    "Membre": ["consulter_fiche_membre"],
}


# ========================================================================
# ZONE A — Tableau de bord & Statistiques
# ========================================================================

def calculer_indicateurs_globaux(livraisons, ventes, paiements):
    """
    Calcule les principaux indicateurs globaux affichés sur le tableau
    de bord à partir des livraisons, ventes et paiements.

    Paramètres :
        livraisons : liste de dict, chacun contenant au minimum
            "membre_id", "culture" et "quantite"

        ventes : liste de dict, chacun contenant au minimum
            "quantite"

        paiements : liste de dict, chacun contenant au minimum
            "montant"

    Retourne :
        un dictionnaire contenant :
            - "stock_total" : quantité restante en stock
            - "montant_du_total" : montant restant à payer aux membres
            - "nb_membres_actifs" : nombre de membres ayant effectué
              au moins une livraison
            - "nb_livraisons_mois" : nombre total de livraisons

    Exemple :
        entrée -> 2 livraisons (100 kg et 50 kg), 1 vente (40 kg),
                  1 paiement (30 000)

        sortie -> {
            "stock_total": 110,
            "montant_du_total": 120000,
            "nb_membres_actifs": 2,
            "nb_livraisons_mois": 2
        }
    """
    # Calculer la quantité totale livrée moins la quantité vendue
    stock_total = sum(l["quantite"] for l in livraisons) - sum(v["quantite"] for v in ventes)

    # Initialiser le montant total à payer aux membres
    montant_du_total = 0

    # Parcourir toutes les livraisons
    for livraison in livraisons:

        # Récupérer la culture de la livraison
        culture = livraison["culture"]

        # Récupérer la quantité livrée
        quantite = livraison["quantite"]

        # Ajouter la valeur de cette livraison selon le prix d'achat
        montant_du_total += quantite * PRIX_ACHAT_KG[culture]

    # Calculer le montant déjà payé aux membres
    montant_paye = sum(p["montant"] for p in paiements)

    # Créer un ensemble des membres ayant effectué au moins une livraison
    membres_actifs = {l["membre_id"] for l in livraisons}

    # Retourner tous les indicateurs calculés
    return {
        "stock_total": stock_total,                         # Stock restant
        "montant_du_total": montant_du_total - montant_paye,# Montant restant à payer
        "nb_membres_actifs": len(membres_actifs),           # Nombre de membres actifs
        "nb_livraisons_mois": len(livraisons)               # Nombre total de livraisons
    }


def calculer_livraisons_par_jour_semaine(livraisons):
    """
    Regroupe le volume total livré (toutes cultures) par date, pour le
    graphique en barres du tableau de bord.

    Paramètre :
        livraisons : liste de dict, chacun avec "date" (str "AAAA-MM-JJ") et "quantite" (int)

    Retourne :
        un dictionnaire {date: quantite_totale_ce_jour}, une clé par date
        distincte présente dans la liste reçue.

    Exemple :
        entrée -> [{"date": "2026-07-08", "quantite": 40}, {"date": "2026-07-08", "quantite": 10}]
        sortie -> {"2026-07-08": 50}
    """
    # Dictionnaire qui contiendra les quantités par date
    resultat = {}

    # Parcourir chaque livraison
    for livraison in livraisons:

        # Récupérer la date
        date = livraison["date"]

        # Récupérer la quantité
        quantite = livraison["quantite"]

        # Si la date n'existe pas encore dans le dictionnaire
        if date not in resultat:

            # Initialiser son total à zéro
            resultat[date] = 0

        # Ajouter la quantité livrée à cette date
        resultat[date] += quantite

    # Retourner le dictionnaire final
    return resultat
def classer_membres_par_production(livraisons):
    """
    Trie les membres par volume total livré, du plus gros producteur au
    plus petit. Utilisée à la fois par le module Membres et le module
    Statistiques (classement).

    Paramètre :
        livraisons : liste de dict. Chaque dict a les clés :
            - "membre_id" (int)
            - "quantite"  (int, en kg)
            (les autres clés éventuelles, comme "culture" ou "date",
            n'ont pas besoin d'être utilisées ici)

    Retourne :
        une liste de dictionnaires {"membre_id": int, "volume_total": int},
        triée par volume_total DÉCROISSANT. Un membre apparaît une seule
        fois, avec la somme de TOUTES ses livraisons (peu importe la
        culture).

    Exemple :
        livraisons = [
            {"membre_id": 1, "quantite": 100},
            {"membre_id": 2, "quantite": 50},
            {"membre_id": 1, "quantite": 30},
            
        ]
        -> le membre 1 a livré 100 + 30 = 130 au total
        -> le membre 2 a livré 50 au total

        sortie -> [
            {"membre_id": 1, "volume_total": 130},
            {"membre_id": 2, "volume_total": 50},
        ]
    """
    # Dictionnaire contenant le volume produit par chaque membre
    volumes = {}

    # Parcourir les livraisons
    for livraison in livraisons:

        # Identifier le membre
        membre = livraison["membre_id"]

        # Récupérer la quantité livrée
        quantite = livraison["quantite"]

        # Si le membre n'existe pas encore
        if membre not in volumes:

            # Initialiser son volume à zéro
            volumes[membre] = 0

        # Ajouter sa quantité au volume total
        volumes[membre] += quantite

    # Liste qui contiendra le classement
    classement = []

    # Transformer le dictionnaire en liste de dictionnaires
    for membre, volume in volumes.items():

        classement.append({
            "membre_id": membre,
            "volume_total": volume
        })

    # Trier la liste par volume décroissant
    classement.sort(key=lambda x: x["volume_total"], reverse=True)

    # Retourner le classement
    return classement



def calculer_statistiques_globales(livraisons, ventes):
    """
    Calcule, pour chaque culture, le volume total livré et la valeur totale
    générée par les ventes de cette culture (module 5, rendement par culture).

    Paramètres :
        livraisons : liste de dict avec :
            - "culture"  (str)
            - "quantite" (int, en kg)
        ventes : liste de dict avec :
            - "culture"  (str)
            - "quantite" (int, en kg)
            - "prix_kg"  (int, en FCFA — le prix RÉELLEMENT négocié pour
              cette vente précise, pas le prix de référence PRIX_VENTE_KG)

    Retourne :
        un dictionnaire {culture: {"volume_total": int, "valeur_totale": int}}
        - volume_total  = somme des "quantite" des LIVRAISONS de cette culture
        - valeur_totale = somme de (quantite * prix_kg) des VENTES de cette culture
        Seules les cultures présentes dans livraisons ET/OU ventes doivent
        apparaître dans le résultat (pas besoin de générer les 3 cultures
        du référentiel si l'une d'elles n'a aucune donnée).

    Exemple :
        livraisons = [{"culture": "Manioc", "quantite": 100}]
        ventes     = [{"culture": "Manioc", "quantite": 50, "prix_kg": 220}]

        volume_total (Manioc)  = 100
        valeur_totale (Manioc) = 50 * 220 = 11000

        sortie -> {"Manioc": {"volume_total": 100, "valeur_totale": 11000}}
    """
    # Dictionnaire des statistiques par culture
    statistiques = {}

    # Parcourir toutes les livraisons
    for livraison in livraisons:

        # Lire la culture
        culture = livraison["culture"]

        # Lire la quantité
        quantite = livraison["quantite"]

        # Si cette culture n'existe pas encore
        if culture not in statistiques:

            # Créer les indicateurs
            statistiques[culture] = {
                "volume_total": 0,
                "valeur_totale": 0
            }

        # Ajouter le volume livré
        statistiques[culture]["volume_total"] += quantite

    # Parcourir toutes les ventes
    for vente in ventes:

        # Lire la culture vendue
        culture = vente["culture"]

        # Lire la quantité vendue
        quantite = vente["quantite"]

        # Lire le prix négocié
        prix = vente["prix_kg"]

        # Si la culture n'existe pas encore
        if culture not in statistiques:

            # La créer
            statistiques[culture] = {
                "volume_total": 0,
                "valeur_totale": 0
            }

        # Ajouter la valeur de cette vente
        statistiques[culture]["valeur_totale"] += quantite * prix

    # Retourner les statistiques
    return statistiques


def generer_indicateurs_rapport_bailleur(livraisons, ventes, paiements):
    """
    Calcule les indicateurs utilisés dans le rapport bailleur (module 5),
    destiné à être transmis à un partenaire financier.

    RÈGLE DE CONFIDENTIALITÉ IMPORTANTE (issue du FRD) :
    cette fonction NE DOIT JAMAIS retourner de donnée nominative (aucun
    nom de membre, aucun membre_id dans le résultat). Seulement des
    chiffres agrégés.

    Paramètres :
        livraisons : liste de dict avec "membre_id" (int), "quantite" (int)
        ventes     : liste de dict avec "quantite" (int), "prix_kg" (int)
        paiements  : liste de dict avec "membre_id" (int), "montant" (int)

    Retourne un dictionnaire avec EXACTEMENT ces 4 clés :
        {
            "volume_total_periode": int,      # somme des "quantite" de livraisons
            "montant_ventes_periode": int,    # somme de (quantite * prix_kg) des ventes
            "taux_regularite_paiements": int, # pourcentage 0-100, voir calcul ci-dessous
            "nb_membres_actifs": int,         # nombre de membre_id DISTINCTS dans livraisons
        }

    Calcul de taux_regularite_paiements :
        (nombre de membres actifs ayant reçu AU MOINS un paiement
         / nombre de membres actifs total) * 100, arrondi à l'entier.
        Si nb_membres_actifs == 0, retournez 0 (pour éviter une division par zéro).

    Exemple :
        livraisons = [{"membre_id": 1, "quantite": 100}, {"membre_id": 2, "quantite": 50}]
        ventes     = [{"quantite": 80, "prix_kg": 220}]
        paiements  = [{"membre_id": 1, "montant": 5000}]

        volume_total_periode   = 100 + 50 = 150
        montant_ventes_periode = 80 * 220 = 17600
        nb_membres_actifs      = 2   (membre_id 1 et 2 ont livré)
        membres payés           = {1}   (seul le membre 1 a un paiement)
        taux_regularite_paiements = round(1 / 2 * 100) = 50

        sortie -> {"volume_total_periode": 150, "montant_ventes_periode": 17600,
                   "taux_regularite_paiements": 50, "nb_membres_actifs": 2}
    """
         
    # Calculer le volume total livré
    volume_total = sum(l["quantite"] for l in livraisons)

    # Calculer le montant total des ventes
    montant_ventes = sum(
        v["quantite"] * v["prix_kg"]
        for v in ventes
    )

    # Récupérer les membres ayant livré
    membres_actifs = {l["membre_id"] for l in livraisons}

    # Récupérer les membres ayant reçu un paiement
    membres_payes = {
        p["membre_id"]
        for p in paiements
        if p["membre_id"] in membres_actifs
    }

    # Compter les membres actifs
    nb_membres = len(membres_actifs)

    # Éviter une division par zéro
    if nb_membres == 0:

        # Aucun membre actif
        taux = 0

    else:

        # Calculer le pourcentage de membres payés
        taux = round(len(membres_payes) / nb_membres * 100)

    # Retourner les indicateurs du rapport
    return {
        "volume_total_periode": volume_total,
        "montant_ventes_periode": montant_ventes,
        "taux_regularite_paiements": taux,
        "nb_membres_actifs": nb_membres
    }



def identifier_top_acheteur(ventes, acheteurs):
    """
    NOUVELLE FONCTION — identifie l'acheteur ayant acheté le plus grand
    volume total (toutes cultures confondues), pour mettre en avant le
    partenaire commercial le plus actif dans le module Statistiques.

    Paramètres :
        ventes    : liste de dict avec "acheteur_id" (int), "quantite" (int)
        acheteurs : liste de dict avec "id" (int), "nom" (str)

    Retourne :
        un dictionnaire {"acheteur_nom": str, "volume_total": int}
        représentant l'acheteur ayant le plus gros volume cumulé.
        Si la liste de ventes est vide, retourner
        {"acheteur_nom": None, "volume_total": 0}.

    Exemple :
        ventes    -> [{"acheteur_id": 1, "quantite": 150}, {"acheteur_id": 2, "quantite": 60}]
        acheteurs -> [{"id": 1, "nom": "Christiane Nkaya"}, {"id": 2, "nom": "Talangaï"}]
        sortie    -> {"acheteur_nom": "Christiane Nkaya", "volume_total": 150}
    """
    # Si aucune vente n'existe
    if not ventes:

        # Retourner un résultat vide
        return {
            "acheteur_nom": None,
            "volume_total": 0
        }

    # Dictionnaire des volumes achetés
    volumes = {}

    # Parcourir les ventes
    for vente in ventes:

        # Lire l'identifiant de l'acheteur
        identifiant = vente["acheteur_id"]

        # Cumuler les quantités achetées
        volumes[identifiant] = volumes.get(identifiant, 0) + vente["quantite"]

    # Trouver l'acheteur ayant acheté le plus
    meilleur_id = max(volumes, key=volumes.get)

    # Récupérer son volume
    meilleur_volume = volumes[meilleur_id]

    # Initialiser le nom
    nom = None

    # Rechercher son nom dans la liste des acheteurs
    for acheteur in acheteurs:

        # Vérifier si l'identifiant correspond
        if acheteur["id"] == meilleur_id:

            # Récupérer le nom
            nom = acheteur["nom"]

            # Arrêter la recherche
            break

    # Retourner le meilleur acheteur
    return {
        "acheteur_nom": nom,
        "volume_total": meilleur_volume
    }


# ========================================================================
# ZONE B — Membres & Livraisons
# ========================================================================

# NOTE : PRIX_ACHAT_KG est un dictionnaire supposé défini ailleurs dans le
# projet (ex. dans un module de constantes), qui associe chaque nom de
# culture (str) à son prix d'achat au kilo (int, en FCFA).
# Exemple attendu : PRIX_ACHAT_KG = {"Manioc": 150, "Maïs": 200, ...}


def calculer_solde_membre(membre_id, livraisons, paiements):
    """
    Calcule ce qui est dû à un membre : valeur totale de ses livraisons
    (au prix d'achat de référence) moins ce qu'il a déjà reçu en paiement.
    C'est la fonction la plus utilisée du projet : elle sert au module
    Membres (statut à jour/en retard), au module Livraisons (solde affiché
    après saisie) et au module Paiements (vérifier qu'on ne verse pas trop).

    Paramètres :
        membre_id  : int — l'identifiant du membre dont on calcule le solde
        livraisons : liste de dict. Chaque dict a les clés :
            - "membre_id" (int)
            - "culture"   (str, une des clés de PRIX_ACHAT_KG)
            - "quantite"  (int, en kg)
          Ne comptez QUE les livraisons dont "membre_id" correspond au
          paramètre membre_id — ignorez celles des autres membres.
        paiements : liste de dict. Chaque dict a les clés :
            - "membre_id" (int)
            - "montant"   (int, en FCFA)
          Même logique : ne comptez que les paiements de ce membre.

    Retourne :
        solde (int, en FCFA) = valeur totale de SES livraisons
                                (quantite * PRIX_ACHAT_KG[culture], sommé)
                                moins somme de SES paiements déjà reçus.
        Peut être 0 si le membre n'a rien livré, ou négatif si (cas
        théorique) il a été payé plus que ce qu'il a livré.

    Exemple (correspond au cas déjà vérifié lors du kickoff du projet) :
        membre_id  = 1
        livraisons = [
            {"membre_id": 1, "culture": "Manioc", "quantite": 120},
            {"membre_id": 1, "culture": "Maïs",   "quantite": 50},
            {"membre_id": 2, "culture": "Manioc", "quantite": 999},  # ignorée : autre membre
        ]
        paiements = [{"membre_id": 1, "montant": 5000}]

        valeur des livraisons du membre 1 = 120*150 + 50*200 = 18000 + 10000 = 28000
        solde = 28000 - 5000 = 23000

        sortie -> 23000
    """
    # Initialise la valeur totale des livraisons de ce membre à 0
    valeur_livraisons = 0

    # Parcourt toutes les livraisons reçues en paramètre
    for livraison in livraisons:
        # Ne traite que les livraisons appartenant au membre demandé
        if livraison["membre_id"] == membre_id:
            # Récupère le prix au kg de la culture concernée
            prix_kg = PRIX_ACHAT_KG[livraison["culture"]]
            # Ajoute la valeur de cette livraison (quantité * prix au kg) au total
            valeur_livraisons += livraison["quantite"] * prix_kg

    # Initialise le total déjà payé à ce membre à 0
    total_paiements = 0

    # Parcourt tous les paiements reçus en paramètre
    for paiement in paiements:
        # Ne traite que les paiements appartenant au membre demandé
        if paiement["membre_id"] == membre_id:
            # Ajoute le montant de ce paiement au total déjà versé
            total_paiements += paiement["montant"]

    # Le solde dû = valeur des livraisons moins ce qui a déjà été payé
    solde = valeur_livraisons - total_paiements

    # Retourne le solde final (peut être négatif dans un cas théorique)
    return solde


def detecter_membres_inactifs(membres, livraisons, jours_seuil=90):
    """
    Identifie les membres n'ayant fait aucune livraison (version
    simplifiée : présence/absence dans la liste reçue, pas de calcul de
    date réelle — c'est une évolution possible hors périmètre Must).

    Paramètres :
        membres : liste de dict. Chaque dict a les clés :
            - "id"  (int)
            - "nom" (str)
        livraisons : liste de dict, chacun avec au moins "membre_id" (int)
        jours_seuil : non utilisé dans cette version simplifiée (paramètre
            gardé pour compatibilité avec une évolution future à date réelle)

    Retourne :
        une liste de dict {"membre_id": int, "nom": str} — un élément par
        membre dont l'"id" n'apparaît dans AUCUNE livraison de la liste reçue.

    Exemple :
        membres    = [{"id": 1, "nom": "Jean Mabiala"}, {"id": 2, "nom": "Sandra Malonga"}]
        livraisons = [{"membre_id": 1, "culture": "Manioc", "quantite": 50}]

        -> le membre id=1 a livré, donc il n'est PAS inactif
        -> le membre id=2 n'apparaît dans aucune livraison, donc il EST inactif

        sortie -> [{"membre_id": 2, "nom": "Sandra Malonga"}]
    """
    # Construit un ensemble (set) de tous les membre_id présents dans les livraisons
    # (un set permet une recherche rapide d'appartenance)
    ids_ayant_livre = {livraison["membre_id"] for livraison in livraisons}

    # Initialise la liste des membres inactifs à retourner
    membres_inactifs = []

    # Parcourt chaque membre de la liste reçue
    for membre in membres:
        # Si l'id du membre n'apparaît dans aucune livraison, il est inactif
        if membre["id"] not in ids_ayant_livre:
            # Ajoute ce membre (au format attendu) à la liste des inactifs
            membres_inactifs.append({"membre_id": membre["id"], "nom": membre["nom"]})

    # Retourne la liste finale des membres inactifs
    return membres_inactifs


def detecter_anomalie_livraison(livraison):
    """
    Vérifie qu'une livraison respecte les règles métier de base avant
    d'être enregistrée (règle métier BA, FRD module Livraisons).

    Paramètre :
        livraison : dict avec les clés "membre_id", "culture", "quantite"
            (potentiellement invalides — c'est justement ce qu'on vérifie)

    Retourne :
        une liste de chaînes de caractères décrivant chaque anomalie
        détectée (liste VIDE si tout est correct — vérifiez bien qu'une
        livraison valide donne [] et pas None).

    Règles à vérifier (une livraison peut cumuler plusieurs anomalies) :
        - "quantite" doit être un nombre strictement positif
          sinon ajouter : "Quantité invalide : doit être strictement positive."
        - "culture" doit être une clé connue de PRIX_ACHAT_KG
          sinon ajouter : "Culture inconnue : {culture}."
        - "membre_id" ne doit pas être vide/None/0
          sinon ajouter : "Aucun membre rattaché à cette livraison."

    Exemple 1 (livraison invalide, deux anomalies à la fois) :
        livraison = {"membre_id": 2, "culture": "Café", "quantite": -10}
        sortie -> ["Quantité invalide : doit être strictement positive.",
                   "Culture inconnue : Café."]

    Exemple 2 (livraison valide) :
        livraison = {"membre_id": 1, "culture": "Manioc", "quantite": 100}
        sortie -> []
    """
    # Initialise la liste des anomalies détectées (vide au départ)
    anomalies = []

    # Vérifie que la quantité est un nombre strictement positif
    if livraison["quantite"] <= 0:
        # Ajoute le message d'anomalie correspondant à la quantité invalide
        anomalies.append("Quantité invalide : doit être strictement positive.")

    # Vérifie que la culture indiquée existe bien dans le référentiel des prix
    if livraison["culture"] not in PRIX_ACHAT_KG:
        # Ajoute le message d'anomalie correspondant à la culture inconnue,
        # en insérant dynamiquement le nom de la culture fautive
        anomalies.append(f"Culture inconnue : {livraison['culture']}.")

    # Vérifie que membre_id n'est pas vide, None ou 0 (valeur "fausse" en Python)
    if not livraison["membre_id"]:
        # Ajoute le message d'anomalie correspondant à l'absence de membre
        anomalies.append("Aucun membre rattaché à cette livraison.")

    # Retourne la liste complète des anomalies (vide si tout est correct)
    return anomalies


def generer_recu(membre_nom, montant):
    """
    Formate un texte de reçu simple pour un paiement effectué.

    Paramètres :
        membre_nom : str — le nom complet du membre, ex. "Jean Mabiala"
        montant    : int — le montant versé, en FCFA

    Retourne (une chaîne de caractères, EXACTEMENT ce format) :
        - si montant <= 0 : "Aucun montant à verser pour {membre_nom}."
        - sinon            : "Reçu - {membre_nom} : paiement de {montant} FCFA effectué."

    Exemples :
        generer_recu("Jean Mabiala", 5000)
          -> "Reçu - Jean Mabiala : paiement de 5000 FCFA effectué."
        generer_recu("Jean Mabiala", 0)
          -> "Aucun montant à verser pour Jean Mabiala."
    """
    # Si le montant est nul ou négatif, il n'y a rien à verser
    if montant <= 0:
        # Retourne le message indiquant qu'aucun versement n'a lieu
        return f"Aucun montant à verser pour {membre_nom}."

    # Sinon, retourne le reçu formaté avec le nom du membre et le montant versé
    return f"Reçu - {membre_nom} : paiement de {montant} FCFA effectué."


def calculer_historique_paiements_membre(membre_id, paiements):
    """
    NOUVELLE FONCTION — extrait l'historique des paiements d'un membre
    précis, pour la nouvelle page Paiements (fiche membre).

    Paramètres :
        membre_id : int
        paiements : liste de dict avec "membre_id" (int), "montant" (int), "date" (str)

    Retourne :
        une liste de dict (uniquement les paiements de ce membre),
        triée par date DÉCROISSANTE (le plus récent en premier).

    Exemple :
        paiements -> [{"membre_id": 1, "montant": 5000, "date": "2026-07-05"},
                      {"membre_id": 2, "montant": 3000, "date": "2026-07-06"},
                      {"membre_id": 1, "montant": 15000, "date": "2026-07-14"}]
        membre_id -> 1
        sortie    -> [{"membre_id": 1, "montant": 15000, "date": "2026-07-14"},
                      {"membre_id": 1, "montant": 5000, "date": "2026-07-05"}]
    """
    # Filtre uniquement les paiements appartenant au membre demandé
    paiements_membre = [p for p in paiements if p["membre_id"] == membre_id]

    # Trie la liste filtrée par date décroissante (le plus récent en premier).
    # Comme les dates sont au format "AAAA-MM-JJ", un tri alphabétique inversé
    # correspond exactement à un tri chronologique inversé.
    paiements_membre_tries = sorted(
        paiements_membre, key=lambda p: p["date"], reverse=True
    )

    # Retourne la liste triée
    return paiements_membre_tries


def rechercher_membre_similaire(nom_complet, membres):
    """
    NOUVELLE FONCTION — recherche tolérante de doublon (RM-7 du FRD) :
    avant de créer un nouveau membre, on vérifie qu'un membre au nom
    quasi identique n'existe pas déjà, pour éviter les doublons créés par
    une simple différence de majuscules ou d'espaces.

    Paramètres :
        nom_complet : str — le nom complet saisi dans le formulaire,
            ex. "  jean MABIALA " (avec espaces ou casse irrégulière
            possibles, comme le ferait une vraie saisie utilisateur)
        membres : liste de dict, chacun avec au moins "nom" (str)

    Retourne :
        le dictionnaire du membre existant si son "nom", une fois
        normalisé (mis en minuscules, espaces de début/fin retirés,
        espaces multiples réduits à un seul espace), correspond
        EXACTEMENT au nom_complet donné (lui aussi normalisé de la même
        façon). Retourne None si aucune correspondance.

    Indication : pour "réduire les espaces multiples à un seul", vous
    pouvez utiliser " ".join(texte.split()) — .split() sans argument
    découpe déjà sur n'importe quelle suite d'espaces et ignore les
    espaces de bord.

    Exemple :
        membres = [{"id": 1, "nom": "Jean Mabiala"}, {"id": 2, "nom": "Alphonsine Nkounkou"}]

        rechercher_membre_similaire("  jean   MABIALA ", membres)
        -> {"id": 1, "nom": "Jean Mabiala"}   (même nom une fois normalisé)

        rechercher_membre_similaire("Marie Koumba", membres)
        -> None   (aucun membre existant ne porte ce nom)
    """
    # Normalise le nom saisi : minuscules, espaces multiples réduits à un seul,
    # et espaces de début/fin retirés (le .split()/.join() gère tout ça d'un coup)
    nom_normalise = " ".join(nom_complet.lower().split())

    # Parcourt tous les membres existants pour chercher une correspondance
    for membre in membres:
        # Normalise de la même façon le nom du membre existant
        nom_membre_normalise = " ".join(membre["nom"].lower().split())

        # Si les deux noms normalisés sont strictement identiques, on a trouvé le doublon
        if nom_membre_normalise == nom_normalise:
            # Retourne immédiatement le membre correspondant
            return membre

    # Si aucun membre ne correspond après avoir tout parcouru, retourne None
    return None


def valider_nouveau_membre(donnees):
    """
    Vérifie que le formulaire de création d'un
    nouveau membre est complet avant de l'enregistrer.

    Paramètre :
        donnees : dict avec les clés "nom", "prenom", "village", "contact"
            (valeurs potentiellement vides ou manquantes — c'est
            justement ce qu'on vérifie)

    Retourne :
        une liste de chaînes de caractères décrivant chaque anomalie
        détectée (liste VIDE si tout est correct).

    Règles à vérifier (un formulaire peut cumuler plusieurs anomalies) :
        - "nom" ne doit pas être vide (après avoir retiré les espaces
          de début/fin) sinon ajouter : "Le nom est obligatoire."
        - "prenom" ne doit pas être vide sinon ajouter :
          "Le prénom est obligatoire."
        - "village" ne doit pas être vide sinon ajouter :
          "Le village est obligatoire."
        - "contact" ne doit pas être vide sinon ajouter :
          "Le contact est obligatoire."

    Exemple 1 (formulaire incomplet) :
        donnees = {"nom": "Koumba", "prenom": "", "village": "Séo", "contact": ""}
        sortie -> ["Le prénom est obligatoire.", "Le contact est obligatoire."]

    Exemple 2 (formulaire valide) :
        donnees = {"nom": "Koumba", "prenom": "Marie", "village": "Séo", "contact": "064111222"}
        sortie -> []
    """
    # Initialise la liste des anomalies détectées (vide au départ)
    anomalies = []

    # Vérifie que le champ "nom" n'est pas vide une fois les espaces de bord retirés
    if not donnees.get("nom", "").strip():
        # Ajoute le message d'anomalie correspondant au nom manquant
        anomalies.append("Le nom est obligatoire.")

    # Vérifie que le champ "prenom" n'est pas vide une fois les espaces de bord retirés
    if not donnees.get("prenom", "").strip():
        # Ajoute le message d'anomalie correspondant au prénom manquant
        anomalies.append("Le prénom est obligatoire.")

    # Vérifie que le champ "village" n'est pas vide une fois les espaces de bord retirés
    if not donnees.get("village", "").strip():
        # Ajoute le message d'anomalie correspondant au village manquant
        anomalies.append("Le village est obligatoire.")

    # Vérifie que le champ "contact" n'est pas vide une fois les espaces de bord retirés
    if not donnees.get("contact", "").strip():
        # Ajoute le message d'anomalie correspondant au contact manquant
        anomalies.append("Le contact est obligatoire.")

    # Retourne la liste complète des anomalies (vide si le formulaire est valide)
    return anomalies


# ========================================================================
# ZONE C — Ventes, Stock & Paiements
# ========================================================================

def calculer_stock_disponible(livraisons, ventes):
    """Calcule le stock disponible pour chaque culture à partir des livraisons et des ventes."""
    
    # 1. Initialiser le stock à 0 pour chaque culture connue dans le référentiel des prix d'achat
    stock = {culture: 0 for culture in PRIX_ACHAT_KG}

    # 2. Ajouter les quantités livrées au stock
    for livraison in livraisons:
        culture = livraison["culture"]  # récupère la culture concernée par cette livraison
        if culture in stock:  # on ignore les cultures inconnues du référentiel
            stock[culture] += livraison["quantite"]  # on ajoute la quantité livrée au stock existant

    # 3. Soustraire les quantités vendues du stock
    for vente in ventes:
        culture = vente["culture"]  # récupère la culture concernée par cette vente
        if culture in stock:  # on ignore les cultures inconnues du référentiel
            stock[culture] -= vente["quantite"]  # on retire la quantité vendue du stock

    return stock  # dictionnaire final : {culture: quantité disponible}


def verifier_stock_avant_vente(vente, stock_disponible):
    """Vérifie si la quantité demandée pour une vente est disponible en stock."""
    culture = vente["culture"]  # culture concernée par la vente
    quantite_demandee = vente["quantite"]  # quantité que le client souhaite acheter
    quantite_dispo = stock_disponible.get(culture, 0)  # quantité réellement en stock (0 si culture absente)

    # on renvoie True si le stock est suffisant, False sinon
    return quantite_demandee <= quantite_dispo


def calculer_marge_vente(vente):
    """Calcule la marge réalisée sur une vente donnée."""
    culture = vente["culture"]  # culture vendue
    quantite = vente["quantite"]  # quantité vendue
    prix_kg = vente["prix_kg"]  # prix de vente au kilo

    prix_achat_reference = PRIX_ACHAT_KG[culture]  # prix d'achat de référence pour cette culture

    # la marge = (prix de vente - prix d'achat) multiplié par la quantité vendue
    marge = (prix_kg - prix_achat_reference) * quantite

    return marge


def verifier_paiement_valide(paiement, solde_du):
    """Vérifie qu'un paiement est valide par rapport au solde dû, et renvoie la liste des anomalies détectées."""
    anomalies = []  # liste qui contiendra les messages d'erreur éventuels
    montant = paiement["montant"]  # montant du paiement à vérifier

    # le montant doit être positif (un paiement nul ou négatif n'a pas de sens)
    if montant <= 0:
        anomalies.append("Le montant doit être strictement positif.")

    # le montant payé ne doit pas dépasser ce qui est réellement dû
    if montant > solde_du:
        anomalies.append(f"Le montant dépasse le solde dû ({solde_du} FCFA).")

    return anomalies  # liste vide = paiement valide, sinon liste des problèmes trouvés


def calculer_moyenne_prix_vente(ventes, culture):
    """Calcule le prix de vente moyen pondéré (par les quantités) pour une culture donnée."""
    somme_ponderee = 0  # somme des (quantité x prix) pour chaque vente
    somme_quantites = 0  # somme totale des quantités vendues

    for vente in ventes:
        if vente["culture"] == culture:  # on ne traite que les ventes de la culture demandée
            somme_ponderee += vente["quantite"] * vente["prix_kg"]  # on accumule quantité x prix
            somme_quantites += vente["quantite"]  # on accumule la quantité totale

    # si aucune vente n'a été trouvée pour cette culture, on évite la division par zéro
    if somme_quantites == 0:
        return 0

    # moyenne pondérée = somme pondérée divisée par la quantité totale, arrondie à l'entier
    return round(somme_ponderee / somme_quantites)

# ========================================================================
# ZONE D — Authentification (nouveau module)
# ========================================================================

def authentifier_utilisateur(nom_utilisateur, mot_de_passe, utilisateurs):
    """Vérifie les identifiants d'un utilisateur et renvoie ses informations si la connexion réussit."""
    for utilisateur in utilisateurs:
        # on compare le nom d'utilisateur et le mot de passe saisis avec ceux enregistrés
        if utilisateur["nom_utilisateur"] == nom_utilisateur and utilisateur["mot_de_passe"] == mot_de_passe:
            # si la correspondance est trouvée, on renvoie les infos utiles (sans le mot de passe)
            return {
                "nom_utilisateur": utilisateur["nom_utilisateur"],
                "role": utilisateur["role"],
                "nom_complet": utilisateur["nom_complet"],
                "membre_id": utilisateur["membre_id"],
            }

    # aucun utilisateur trouvé correspondant aux identifiants -> échec de la connexion
    return None


def verifier_acces_role(role, action):
    actions_autorisees = ACTIONS_PAR_ROLE.get(role, [])
    return action in actions_autorisees
