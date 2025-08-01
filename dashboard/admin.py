from django.contrib import admin
from .models import  Produit, OrdreProduction, OperationProduction, Employe, Stock



@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'nom_produit', 'categorie', 'statut')
    list_filter = ('statut', 'categorie')
    search_fields = ('code_produit', 'nom_produit')

@admin.register(OrdreProduction)
class OrdreProductionAdmin(admin.ModelAdmin):
    list_display = ('code_ordre', 'produit', 'quantite_commandee', 'date_debut', 'date_fin_prevue', 'statut')
    list_filter = ('statut', 'date_debut')
    search_fields = ('code_ordre',)

class OperationProductionAdmin(admin.ModelAdmin):
    list_display = ('ordre_production', 'type_operation', 'date_debut', 'date_fin', 'liste_employes')

admin.site.register(OperationProduction, OperationProductionAdmin)
@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'role')
    search_fields = ('nom', 'prenom', 'role')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'quantite_disponible')
    search_fields = ('produit__nom_produit',)
