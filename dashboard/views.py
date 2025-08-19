import os
import json
import joblib
import time
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produit,Employe,OrdreProduction
from .forms import ProduitForm,EmployeForm,OrdreProductionForm,OperationProductionForm
from .models import OrdreProduction 
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from .models import OrdreProduction, Produit,OperationProduction
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import date
from django.shortcuts import render
from dashboard.models import OrdreProduction
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
#################################################################""


def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'liste_produits.html', {'produits': produits})


def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm()
    return render(request, 'ajouter_produit.html', {'form': form})

def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'modifier_produit.html', {'form': form})

def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit.delete()
    return redirect('liste_produits')

#############################################################################

def roles_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if role not in getattr(request.user, 'role', ''):
                messages.error(request, "Accès refusé : vous n'avez pas la permission.")
                return redirect('page_accueil')  # ou une page d'accueil, tableau de bord, etc.
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
@roles_required('admin')
# Liste des employés
def liste_employes(request):
    employes = Employe.objects.all()
    return render(request, 'liste_employes.html', {'employes': employes})

# Ajouter un employé
@roles_required('admin')
def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_employes')
    else:
        form = EmployeForm()
    return render(request, 'ajouter_employe.html', {'form': form})

# Modifier un employé
@roles_required('admin')
def modifier_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('liste_employes')
    else:
        form = EmployeForm(instance=employe)
    return render(request, 'modifier_employe.html', {'form': form})

@roles_required('admin')
def supprimer_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    if request.method == 'POST':
        employe.delete()
        return redirect('liste_employes')
    return render(request, 'supprimer_employe.html', {'employe': employe})


#########################################################################################""
def liste_ordres(request):
    ordres = OrdreProduction.objects.all()
    return render(request, 'liste_ordres.html', {'ordres': ordres})



def roles_required_multiple(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                return HttpResponseForbidden("Accès refusé : rôle insuffisant.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@roles_required_multiple(['admin', 'production'])
def ajouter_ordre(request):
    if request.method == 'POST':
        form = OrdreProductionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_ordres')
    else:
        form = OrdreProductionForm()
    return render(request, 'ajouter_ordre.html', {'form': form})

@roles_required_multiple(['admin', 'production'])
def modifier_ordre(request, id):

    ordre = get_object_or_404(OrdreProduction, pk=id)
    if request.method == 'POST':
        form = OrdreProductionForm(request.POST, instance=ordre)
        if form.is_valid():
            form.save()
            return redirect('liste_ordres')
    else:
        form = OrdreProductionForm(instance=ordre)
    return render(request, 'modifier_ordre.html', {'form': form})

@roles_required_multiple(['admin', 'production'])
def supprimer_ordre(request, id):
    ordre = get_object_or_404(OrdreProduction, id=id)
    ordre.delete()
    return redirect('liste_ordres')

###############################################################################

def liste_operations(request):
    operations = OperationProduction.objects.all()
    return render(request, 'liste_operations.html', {'operations': operations})

def ajouter_operation(request):
    if request.method == 'POST':
        form = OperationProductionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_operations')
    else:
        form = OperationProductionForm()
    return render(request, 'ajouter_operation.html', {'form': form})

def modifier_operation(request, pk):
    operation = get_object_or_404(OperationProduction, pk=pk)
    if request.method == 'POST':
        form = OperationProductionForm(request.POST, instance=operation)
        if form.is_valid():
            form.save()
            return redirect('liste_operations')
    else:
        form = OperationProductionForm(instance=operation)
    return render(request, 'modifier_operation.html', {'form': form})

def supprimer_operation(request, pk):
    operation = get_object_or_404(OperationProduction, pk=pk)
    if request.method == 'POST':
        operation.delete()
        return redirect('liste_operations')
    return render(request, 'supprimer_operation.html', {'operation': operation})




############################################################################################################################################################################






def dashboard_view(request):
    # Statistiques de base
    nb_produits = Produit.objects.count()
    nb_employes = Employe.objects.count()
    
    total_ordres = OrdreProduction.objects.count()
    ordres_en_cours = OrdreProduction.objects.filter(statut='en_cours').count()
    ordres_termines = OrdreProduction.objects.filter(statut='termine').count()
    ordres_annules = OrdreProduction.objects.filter(statut='annule').count()
    
    ordres = OrdreProduction.objects.all()
    
    # Graphique 1: Répartition des statuts (Pie Chart)
    statuts_data = {
        'En cours': ordres_en_cours,
        'Terminé': ordres_termines,
        'Annulé': ordres_annules
    }
    
    # Graphique 2: Production mensuelle
    production_mensuelle = OrdreProduction.objects.filter(
        statut='termine',
        date_debut__isnull=False
    ).annotate(
        mois=TruncMonth('date_fin_prevue')
    ).values('mois').annotate(
        quantite_totale=Sum('quantite_terminee')
    ).order_by('mois')
    
    mois_labels = []
    quantites_data = []
    for item in production_mensuelle:
        mois_labels.append(item['mois'].strftime('%B %Y'))
        quantites_data.append(item['quantite_totale'] or 0)
    
    # Préparer stats opérations production
    operations = OperationProduction.objects.select_related('ordre_production').all()
    stats = []
    print("Nombre d'opérations :", len(operations))
    for op in operations:
        maintenant = timezone.now()
        date_fin_prevue = op.ordre_production.date_fin_prevue
        if date_fin_prevue:
            date_fin_prevue_dt = datetime.combine(date_fin_prevue, datetime.max.time())
            date_fin_prevue_dt = make_aware(date_fin_prevue_dt, timezone.get_current_timezone())
            retard = maintenant > date_fin_prevue_dt
        else:
            retard = False

        pourcentage = round((op.quantite_produite / op.quantite_demandee) * 100) if op.quantite_demandee > 0 else 0

        # Debug prints pour comprendre le problème
        print(f"Opération: {op.ordre_production.code_ordre}")
        print(f"Date fin prévue: {date_fin_prevue}")
        print(f"Maintenant: {maintenant}")
        print(f"Retard: {retard}")
        print(f"Quantité produite: {op.quantite_produite}")
        print(f"Quantité demandée: {op.quantite_demandee}")

        # Logique corrigée pour l'état
        if op.quantite_produite >= op.quantite_demandee:
            etat = "Terminé"
        elif retard:
            etat = "En retard"
        else:
            etat = "En cours"

        print(f"État calculé: {etat}")
        print("---")

        stats.append({
            'code_ordre': op.ordre_production.code_ordre,
            'type_operation': op.get_type_operation_display(),
            'quantite_demandee': op.quantite_demandee,
            'quantite_produite': op.quantite_produite,
            'pourcentage': pourcentage,
            'etat': etat,
        })

    # Fusionner tout dans un seul context
    context = {
        'nb_produits': nb_produits,
        'nb_employes': nb_employes,
        'total_ordres': total_ordres,
        'ordres_en_cours': ordres_en_cours,
        'ordres_termines': ordres_termines,
        'ordres_annules': ordres_annules,
        'ordres': ordres,
        'statuts_data': json.dumps(statuts_data),
        'production_mensuelle': {
            'labels': json.dumps(mois_labels),
            'data': json.dumps(quantites_data)
        },
        'stats': stats,
    }

    return render(request, 'dashboard.html', context)


####################################################################################################


def prediction_retard(request):
    time.sleep(1)
    # Charger le modèle
    model_path = os.path.join('ml_models', 'mon_modele.pkl')
    model = joblib.load(model_path)

    aujourdhui = date.today()
    ordres = OrdreProduction.objects.filter(statut="en_cours")

    data = []
    for ordre in ordres:
        quantite_commandee = ordre.quantite_commandee
        quantite_terminee = ordre.quantite_terminee
        duree_prevue = (ordre.date_fin_prevue - ordre.date_debut).days
        progression = quantite_terminee / quantite_commandee if quantite_commandee > 0 else 0
        jours_passes = (aujourdhui - ordre.date_debut).days
        jours_restants = (ordre.date_fin_prevue - aujourdhui).days
        vitesse_production = quantite_terminee / jours_passes if jours_passes > 0 else 0
        production_restante_par_jour = ((quantite_commandee - quantite_terminee) / jours_restants) if jours_restants > 0 else 0

        data.append({
            "id": ordre.id,
            "produit": ordre.produit.nom if hasattr(ordre.produit, "nom") else str(ordre.produit),
            "quantite_commandee": quantite_commandee,
            "quantite_terminee": quantite_terminee,
            "duree_prevue": duree_prevue,
            "progression": progression,
            "jours_passes": jours_passes,
            "jours_restants": jours_restants,
            "vitesse_production": vitesse_production,
            "production_restante_par_jour": production_restante_par_jour,
            "date_debut": ordre.date_debut,
            "date_fin_prevue": ordre.date_fin_prevue,
        })

    df = pd.DataFrame(data)
    features = df[[
        "quantite_commandee", "quantite_terminee", "duree_prevue",
        "progression", "jours_passes", "jours_restants",
        "vitesse_production", "production_restante_par_jour"
    ]].values

    predictions = model.predict(features)

    resultats = []
    for i, pred in enumerate(predictions):
        ordre = data[i]
        if pred == 1:
            status = "retard"
        else:
            status = "a_temps"
        resultats.append({
            "id": ordre["id"],
            "produit": ordre["produit"],
            "quantite": ordre["quantite_commandee"],
            "quantite_terminee": ordre["quantite_terminee"],
            "date_debut": ordre["date_debut"],
            "date_fin_prevue": ordre["date_fin_prevue"],
            "status": status,
        })

    retard = [r for r in resultats if r["status"] == "retard"]
    a_temps = [r for r in resultats if r["status"] == "a_temps"]

    return render(request, "prediction_retard.html", {
        "resultats": {
            "retard": retard,
            "a_temps": a_temps
        }
    })






################################################################################################""
def voice_test(request):
    return render(request, 'voice.html')

