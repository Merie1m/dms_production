from django.urls import path
from . import views

urlpatterns = [
     path('produits/', views.liste_produits, name='liste_produits'),
     path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
     path('produits/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
     path('produits/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),

     
     path('employes/', views.liste_employes, name='liste_employes'),
     path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
     path('employes/modifier/<int:id>/', views.modifier_employe, name='modifier_employe'),
     path('employes/supprimer/<int:id>/', views.supprimer_employe, name='supprimer_employe'),


     path('ordres/', views.liste_ordres, name='liste_ordres'),
     path('ordres/ajouter/', views.ajouter_ordre, name='ajouter_ordre'),
     path('ordres/modifier/<int:id>/', views.modifier_ordre, name='modifier_ordre'),
     path('ordres/supprimer/<int:id>/', views.supprimer_ordre, name='supprimer_ordre_production'),


     path('operations/', views.liste_operations, name='liste_operations'),
     path('operations/ajouter/', views.ajouter_operation, name='ajouter_operation'),
     path('operations/modifier/<int:id>/', views.modifier_operation, name='modifier_operation'),
     path('operations/supprimer/<int:id>/', views.supprimer_operation, name='supprimer_operation'),
     path('prediction-retard/', views.prediction_retard, name='prediction_retard'),

    path('voice-test/', views.voice_test, name='voice_test'),

    path('', views.dashboard_view, name='dashboard'),
   
   
]
