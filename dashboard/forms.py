from django import forms
from .models import Produit,Employe,OrdreProduction,OperationProduction

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['code_produit', 'nom_produit', 'description', 'categorie', 'statut']


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'role']



class OrdreProductionForm(forms.ModelForm):
    class Meta:
        model = OrdreProduction
        fields = '__all__'


class OperationProductionForm(forms.ModelForm):
    class Meta:
        model = OperationProduction
        fields = '__all__'


