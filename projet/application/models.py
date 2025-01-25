from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class Produit(models.Model):
     designation= models.CharField(max_length=50)
     prix= models.FloatField(max_length=10)
     
     def inserer_produit(designation, prix):
        return Produit.objects.create(designation=designation, prix=prix)
   
     @classmethod
     def modifier_produit(cls, produit_id, designation=None, prix=None):
        produit = cls.objects.get(pk=produit_id)
        if designation:
            produit.designation = designation
        if prix:
            produit.prix = prix
        produit.save()
        return produit

     @classmethod
     def supprimer_produit(cls, produit_id):
        produit = cls.objects.get(pk=produit_id)
        produit.delete()

     @classmethod
     def rechercher_produit(cls, keyword):
        return cls.objects.filter(designation__icontains=keyword)

     @classmethod
     def consulter_produits(cls):
        return cls.objects.all()

     @classmethod
     def imprimer_produits(cls):
        produits = cls.objects.all()
        return produits
     
     def __str__(self):
        return self.designation
     
class Client(models.Model):
     nomc= models.CharField(max_length=40)
     prenomc= models.CharField(max_length=40)
     adressec= models.CharField(max_length=100)
     telc= models.IntegerField()
     creditc= models.FloatField(max_length=20)

     @classmethod
     def modifier_client(cls, client_id, nomc=None, prenomc=None, adressec=None, telc=None, creditc=None):
        client = cls.objects.get(pk=client_id)
        if nomc:
            client.nomc = nomc
        if prenomc:
            client.prenomc = prenomc
        if adressec:
            client.adressec = adressec
        if telc:
            client.telc = telc
        if creditc:
            client.creditc = creditc
        client.save()
        return client

     @classmethod
     def supprimer_client(cls, client_id):
        client = cls.objects.get(pk=client_id)
        client.delete()

     @classmethod
     def rechercher_client(cls, keyword):
        return cls.objects.filter(nomc__icontains=keyword) | cls.objects.filter(prenomc__icontains=keyword)

     @classmethod
     def consulter_clients(cls):
        return cls.objects.all()
     def __str__(self):
        return f"{self.nomc} {self.prenomc}"


class Fournisseur(models.Model):
     nomf= models.CharField(max_length=40)
     prenomf= models.CharField(max_length=40)
     adressef= models.CharField(max_length=100)
     telf= models.IntegerField()
     soldef= models.FloatField(max_length=20)

     def __str__(self):
        return f"{self.nomf} {self.prenomf}"

class Centre(models.Model):
     designationc = models.CharField(max_length=100)
     identifiant = models.IntegerField(unique=True, default=0)
     def __str__(self):
        return self.designationc
     

class Employe(models.Model):
    nome = models.CharField(max_length=40)
    prenome = models.CharField(max_length=40)
    adressee = models.CharField(max_length=100)
    tele = models.IntegerField()
    salairee = models.FloatField(max_length=20)
    centre = models.ForeignKey(Centre, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} {self.prenome}"
     

class Achat(models.Model):
     detail= models.CharField(max_length=500)
     qteA= models.IntegerField()
     DateA=models.DateField()
     prixH= models.FloatField(max_length=20)
     montantp= models.FloatField(max_length=20)
     fournisseurA= models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
     produitA= models.ForeignKey(Produit, on_delete=models.CASCADE)
     def prixtotalAchat(self):
          return self.prixH * self.qteA
     def prixRestant(self):
          return self.prixtotalAchat()-self.montantp

class Reglement(models.Model):
     Datereg= models.DateField()
     montantreg= models.FloatField(max_length=20)
     achat=models.OneToOneField(Achat, on_delete=models.CASCADE)

class Transfert(models.Model):
    datetr= models.DateField()
    qtetr= models.IntegerField()
    prixac= models.FloatField(max_length=20)         
    produit_t= models.ForeignKey(Produit, on_delete=models.CASCADE)
    centre_t= models.ForeignKey(Centre, on_delete=models.CASCADE)


class Vente(models.Model):
     qtev= models.IntegerField()
     DateV=models.DateField()
     prixv= models.FloatField(max_length=20)
     montantv= models.FloatField(max_length=20)
     clientv= models.ForeignKey(Client, on_delete=models.CASCADE)
     produitv=models.ForeignKey(Produit, on_delete=models.CASCADE)
     centre = models.ForeignKey(Centre, on_delete=models.CASCADE, null=True, blank=True)
     def montant_total_calcule(self):
             return self.qtev * self.prixv
     def reste_apayer(self):
             return  self.montant_total_calcule() - self.montantv
     
     
     

class PaimentCredit(models.Model):
     datepv= models.DateField()
     montantpv= models.FloatField(max_length=20)
     vente= models.OneToOneField(Vente, on_delete=models.CASCADE)

class gestionEmploye(models.Model):
     employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
     date_absence = models.DateField(null=True, blank=True)
     retenueS = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     demandeAvance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     salaireJ= models.FloatField(max_length=20)

class EtatStock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_en_stock = models.IntegerField(default=0)
    def montant_total_stock(self):
        return self.produit.prix


class PV(models.Model):
    date_pv = models.DateField()
    centre = models.ForeignKey(Centre, on_delete=models.CASCADE)
    ventes = models.ManyToManyField(Vente)
    transferts = models.ManyToManyField(Transfert)
    employes = models.ManyToManyField(Employe)

class EtatStockCentre(models.Model):
    produit_stocke = models.ForeignKey(Produit, on_delete=models.CASCADE)
    centre = models.ForeignKey(Centre, on_delete=models.CASCADE)  
    quantite_en_stock_centre = models.IntegerField(default=0)

    def montant_total_stock(self):
        return self.produit.prix


class Absence(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date_absence = models.DateField()

class AvanceSalaire(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date_avance = models.DateField()
    montant = models.FloatField(max_length=20)



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)  # User is inactive until they confirm their email
    is_staff = models.BooleanField(default=False)  # An admin user; non super-users can be staff as well

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email