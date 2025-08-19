from django.db import models
from decimal import Decimal

class Produit(models.Model):
    CATEGORIE_CHOICES = [
        ('siege_avant', 'Sièges avant'),
        ('siege_arriere', 'Sièges arrière'),
        ('garniture_laterale', 'Garniture latérale'),
    ]

    STATUT_CHOICES = [
        ('en_production', 'En production'),
        ('discontinue', 'Discontinué'),
        ('stocke', 'Stocké'),
    ]
    prix_unitaire = models.DecimalField(
        max_digits=10,  
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Prix unitaire en devise locale"
    )

    code_produit = models.CharField(max_length=50, unique=True)
    nom_produit = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_production')

    def __str__(self):
        return self.nom_produit


# 3. Employés de l’usine
class Employe(models.Model):
    ROLE_CHOICES = [
        ('operateur_main', 'Opérateur manuel'),
        ('operateur_machine', 'Opérateur machine'),
        ('superviseur', 'Superviseur'),
        ('technicien', 'Technicien'),
        ('controle_qualite', 'Contrôle Qualité'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# 4. Ordre de production
class OrdreProduction(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    code_ordre = models.CharField(max_length=50, unique=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_commandee = models.PositiveIntegerField()
    quantite_terminee = models.PositiveIntegerField(default=0)
    date_debut = models.DateField()
    date_fin_prevue = models.DateField()
    date_fin_reelle = models.DateField(null=True, blank=True)  # NOUVEAU pour IA
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    
    def save(self, *args, **kwargs):
        # NOUVEAU : Mettre date_fin_reelle quand terminé
        if self.statut == 'termine' and not self.date_fin_reelle:
            self.date_fin_reelle = date.today()
        
        # Logique existante
        if self.statut == 'termine':
            self.quantite_terminee = self.quantite_commandee
        elif self.statut == 'annule':
            self.quantite_terminee = 0
        elif self.quantite_terminee >= self.quantite_commandee and self.statut == 'en_cours':
            self.statut = 'termine'
            self.quantite_terminee = self.quantite_commandee
        elif self.quantite_terminee < self.quantite_commandee and self.statut == 'termine':
            self.statut = 'en_cours'
        
        super().save(*args, **kwargs)
    
    @property
    def pourcentage_termine(self):
        if self.quantite_commandee > 0:
            return round((self.quantite_terminee / self.quantite_commandee) * 100)
        return 0
    
    @property
    def progress_class(self):
        pourcentage = self.pourcentage_termine
        if pourcentage == 100:
            return "bg-success"
        elif pourcentage > 0:
            return "bg-warning"
        else:
            return "bg-dark"
    
    # NOUVEAU : Propriétés pour l'IA
    @property
    def est_en_retard(self):
        """Retourne True si l'ordre est en retard"""
        if self.statut == 'termine' and self.date_fin_reelle:
            return self.date_fin_reelle > self.date_fin_prevue
        elif self.statut == 'en_cours':
            return date.today() > self.date_fin_prevue
        return False
    
    @property
    def jours_retard(self):
        """Calcule le nombre de jours de retard"""
        if self.statut == 'termine' and self.date_fin_reelle:
            delta = self.date_fin_reelle - self.date_fin_prevue
            return max(0, delta.days)
        elif self.statut == 'en_cours':
            delta = date.today() - self.date_fin_prevue
            return max(0, delta.days)
        return 0
    
    @property
    def duree_prevue_jours(self):
        """Durée prévue en jours"""
        return (self.date_fin_prevue - self.date_debut).days
    
    def __str__(self):
        return self.code_ordre
# 5. Étapes réalisées sur un ordre (ex : découpe, couture)
class OperationProduction(models.Model):
    TYPE_CHOICES = [
        ('decoupe', 'Découpe'),
        ('couture', 'Couture'),
        ('assemblage', 'Assemblage'),
        ('controle_qualite', 'Contrôle qualité'),
        ('autre', 'Autre'),
    ]

    ordre_production = models.ForeignKey(OrdreProduction, on_delete=models.CASCADE)
    type_operation = models.CharField(max_length=30, choices=TYPE_CHOICES)
    quantite_demandee = models.PositiveIntegerField(default=0)  # Nouveau champ mech bel dharoura tkoun 9ad el quantité mta3 l'ordre de  production manches 500*2...
    quantite_produite = models.PositiveIntegerField()

    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    employes = models.ManyToManyField(Employe)

    def __str__(self):
        return f"{self.type_operation} - {self.ordre_production.code_ordre}"
    def liste_employes(self):
      return ", ".join([str(e) for e in self.employes.all()])


# 6. Suivi des quantités disponibles
class Stock(models.Model):
    EMPLACEMENT_CHOICES = [
        ('magasin', 'Magasin'),
        ('entrepot', 'Entrepôt'),
        ('expedition', 'Expédition'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_disponible = models.PositiveIntegerField()
    emplacement = models.CharField(
        max_length=20, 
        choices=EMPLACEMENT_CHOICES,
        default='magasin'  # Valeur par défaut
    )

    def __str__(self):
        return f"{self.produit.nom_produit} - {self.quantite_disponible} ({self.get_emplacement_display()})"
