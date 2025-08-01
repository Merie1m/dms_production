#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta
import random

# === Configuration Django (AJOUT IMPORTANT) ===
sys.path.append(r"C:\Users\merie\textile_project")  # Chemin vers ton projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dms_textile.settings')
django.setup()

# Maintenant on peut importer nos modèles
from dashboard.models import Produit, Employe, OrdreProduction

def create_test_data():
    print('🚀 Création des données de test...')
    
    # 1. Créer des produits
    produits_data = [
        {'code': 'SA001', 'nom': 'Siège avant cuir noir', 'categorie': 'siege_avant'},
        {'code': 'SA002', 'nom': 'Siège avant tissu gris', 'categorie': 'siege_avant'},
        {'code': 'SR001', 'nom': 'Siège arrière cuir beige', 'categorie': 'siege_arriere'},
        {'code': 'GL001', 'nom': 'Garniture latérale droite', 'categorie': 'garniture_laterale'},
    ]
    
    for p in produits_data:
        produit, created = Produit.objects.get_or_create(
            code_produit=p['code'],
            defaults={
                'nom_produit': p['nom'],
                'categorie': p['categorie'],
                'prix_unitaire': random.uniform(50, 200)
            }
        )
        if created:
            print(f'✅ Produit créé: {produit.nom_produit}')
    
    # 2. Créer des employés
    employes_data = [
        ('Dupont', 'Jean', 'operateur_machine'),
        ('Martin', 'Marie', 'operateur_main'),
        ('Bernard', 'Paul', 'superviseur'),
        ('Durand', 'Sophie', 'controle_qualite'),
        ('Moreau', 'Pierre', 'technicien'),
    ]
    
    for nom, prenom, role in employes_data:
        employe, created = Employe.objects.get_or_create(
            nom=nom,
            prenom=prenom,
            defaults={'role': role}
        )
        if created:
            print(f'✅ Employé créé: {employe}')
    
    # 3. Créer des ordres historiques (pour entraîner l'IA)
    produits_db = list(Produit.objects.all())
    ordres_crees = 0
    
    for i in range(50):  # 50 ordres historiques
        produit = random.choice(produits_db)
        date_debut = date.today() - timedelta(days=random.randint(30, 120))
        duree = random.randint(5, 20)  # 5 à 20 jours
        date_fin_prevue = date_debut + timedelta(days=duree)
        
        retard = 0
        if random.random() < 0.3:
            retard = random.randint(1, 10)
        
        date_fin_reelle = date_fin_prevue + timedelta(days=retard)
        quantite = random.randint(50, 500)
        
        ordre, created = OrdreProduction.objects.get_or_create(
            code_ordre=f'ORD{1000+i}',
            defaults={
                'produit': produit,
                'quantite_commandee': quantite,
                'quantite_terminee': quantite,
                'date_debut': date_debut,
                'date_fin_prevue': date_fin_prevue,
                'date_fin_reelle': date_fin_reelle,
                'statut': 'termine'
            }
        )
        if created:
            ordres_crees += 1
    
    print(f'✅ {ordres_crees} ordres historiques créés')
    
    # 4. Créer quelques ordres en cours
    ordres_cours_crees = 0
    for i in range(10):
        produit = random.choice(produits_db)
        date_debut = date.today() - timedelta(days=random.randint(1, 10))
        duree = random.randint(5, 15)
        date_fin_prevue = date_debut + timedelta(days=duree)
        quantite = random.randint(50, 300)
        quantite_terminee = random.randint(0, quantite//2)
        
        ordre, created = OrdreProduction.objects.get_or_create(
            code_ordre=f'CURR{2000+i}',
            defaults={
                'produit': produit,
                'quantite_commandee': quantite,
                'quantite_terminee': quantite_terminee,
                'date_debut': date_debut,
                'date_fin_prevue': date_fin_prevue,
                'statut': 'en_cours'
            }
        )
        if created:
            ordres_cours_crees += 1
    
    print(f'✅ {ordres_cours_crees} ordres en cours créés')
    print('🎉 Données de test créées avec succès!')

if __name__ == '__main__':
    create_test_data()
