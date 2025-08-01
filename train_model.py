import os  # Module pour gérer les fichiers et dossiers
import sys  # Module pour gérer le chemin d'accès au projet
import django  # Pour configurer et utiliser Django dans un script externe
import pandas as pd  # Pour manipuler les données sous forme de tableau (DataFrame)
from datetime import date  # Pour gérer les dates
import joblib  # Pour sauvegarder et charger le modèle d'IA

# Configuration Django
sys.path.append(r"C:\Users\merie\textile_project")  # Ajout du chemin du projet Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dms_textile.settings')  # Définir les paramètres Django
django.setup()  # Initialisation de Django pour pouvoir utiliser les modèles

from dashboard.models import OrdreProduction  # Importer le modèle OrdreProduction

# 1. Récupérer les données
ordres = OrdreProduction.objects.all()  # Récupérer tous les ordres de production depuis la base de données
data = []  # Liste qui contiendra toutes les données formatées
aujourdhui = date.today()  # Date actuelle pour les calculs

# Parcourir chaque ordre de production
for ordre in ordres:
    quantite_commandee = ordre.quantite_commandee  # Quantité commandée pour cet ordre
    quantite_terminee = ordre.quantite_terminee  # Quantité déjà produite
    duree_prevue = (ordre.date_fin_prevue - ordre.date_debut).days  # Durée prévue de production en jours
    retard = 0  # Initialisation de la variable retard (0 = à l'heure)

    # Vérifier si l'ordre est en retard
    if ordre.date_fin_reelle and ordre.date_fin_reelle > ordre.date_fin_prevue:
        retard = 1  # Si la date de fin réelle dépasse la date prévue, il y a retard

    # Calcul de la progression de production (en pourcentage si > 0 sinon 0)
    progression = quantite_terminee / quantite_commandee if quantite_commandee > 0 else 0

    # Calcul du nombre de jours passés depuis le début de la production
    jours_passes = (aujourdhui - ordre.date_debut).days

    # Calcul du nombre de jours restants jusqu'à la date prévue de fin
    jours_restants = (ordre.date_fin_prevue - aujourdhui).days

    # Calcul de la vitesse de production par jour
    vitesse_production = quantite_terminee / jours_passes if jours_passes > 0 else 0

    # Quantité restante à produire par jour pour terminer dans les temps
    production_restante_par_jour = (
        (quantite_commandee - quantite_terminee) / jours_restants
        if jours_restants > 0 else 0
    )

    # Ajouter toutes les informations calculées dans la liste "data"
    data.append({
        "id": ordre.id,  # ID de l'ordre
        "produit": ordre.produit.nom if hasattr(ordre.produit, "nom") else str(ordre.produit),  # Nom du produit
        "quantite_commandee": quantite_commandee,
        "quantite_terminee": quantite_terminee,
        "duree_prevue": duree_prevue,
        "progression": progression,
        "jours_passes": jours_passes,
        "jours_restants": jours_restants,
        "vitesse_production": vitesse_production,
        "production_restante_par_jour": production_restante_par_jour,
        "retard": retard,
        "statut": ordre.statut,
    })

# Conversion de la liste "data" en tableau Pandas
df = pd.DataFrame(data)

# 2. Garder uniquement les ordres terminés pour entraîner le modèle
df_train = df[df["statut"] == "termine"]

from sklearn.model_selection import train_test_split  # Pour séparer les données en train et test
from sklearn.ensemble import RandomForestClassifier  # Modèle IA utilisé (Random Forest)
from sklearn.metrics import accuracy_score  # Pour mesurer la précision du modèle
from sklearn.utils import resample  # Pour équilibrer les classes (retard vs à l'heure)

# Définir les caractéristiques (X) et la cible (y)
X = df_train[[
    "quantite_commandee", "quantite_terminee", "duree_prevue",
    "progression", "jours_passes", "jours_restants",
    "vitesse_production", "production_restante_par_jour"
]]
y = df_train["retard"]  # Cible : 1 si en retard, 0 sinon

# Équilibrage des données pour avoir autant d'ordres en retard que d'ordres à l'heure
df_balanced = pd.concat([
    resample(df_train[df_train.retard == 1], replace=True, n_samples=max(1, y.value_counts().max()), random_state=42),
    resample(df_train[df_train.retard == 0], replace=True, n_samples=y.value_counts().max(), random_state=42)
])

# Redéfinir X et y après équilibrage
X = df_balanced.drop(columns=["retard", "statut", "id", "produit"])
y = df_balanced["retard"]

# Séparer les données en deux jeux : entraînement (80%) et test (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle IA (Random Forest)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Évaluer la précision du modèle sur le jeu de test
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Précision du modèle équilibré : {accuracy * 100:.2f}%")

# Sauvegarder le modèle dans un dossier "ml_models"
os.makedirs('ml_models', exist_ok=True)
joblib.dump(model, 'ml_models/mon_modele.pkl')
print("Modèle sauvegardé dans 'ml_models/mon_modele.pkl'")

# 3. Prédire sur les ordres en cours
df_en_cours = df[df["statut"] == "en_cours"]  # Filtrer uniquement les ordres en cours

# Préparer les données pour prédire le retard
donnees_prediction = df_en_cours[[
    "quantite_commandee", "quantite_terminee", "duree_prevue",
    "progression", "jours_passes", "jours_restants",
    "vitesse_production", "production_restante_par_jour"
]].values

# Prédire avec le modèle entraîné
predictions = model.predict(donnees_prediction)

# Afficher le résultat pour chaque ordre
for i, pred in enumerate(predictions):
    ordre = df_en_cours.iloc[i]
    if pred == 1:  # Si prédiction = retard
        print(f"⚠️ L'ordre ID {ordre['id']} – {ordre['produit']} ({ordre['quantite_commandee']} unités) risque d'être en retard.")
    else:  # Sinon à l'heure
        print(f"✅ L'ordre ID {ordre['id']} – {ordre['produit']} devrait être terminé à temps.")
