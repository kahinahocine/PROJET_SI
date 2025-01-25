from django import forms
from .models import Absence, Achat, AvanceSalaire, Centre, Employe, Fournisseur, Produit, Transfert, Vente ,Client,PaimentCredit
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
# creation de form achat pour l'utiliser dans la fonction qu'on deffiné dans views 
class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = '__all__'
        labels = {
            'detail': 'Détail de l\'achat',
            'qteA': 'Quantité à acheter',
            'DateA': 'Date d\'achat',
            'prixH': 'Prix unitaire',
            'montantp': 'Montant payé',
            'fournisseurA': 'Fournisseur',
            'produitA': 'Produit',
        }
        widgets = {
            'fournisseurA': forms.Select(attrs={'class': 'selectpicker'}),
            'produitA': forms.Select(attrs={'class': 'selectpicker'}),
            'DateA': forms.DateInput(attrs={'type': 'date'}),
        }
# creation de form paiment 
class PaiementFournisseurForm(forms.Form):
     montant_paiement = forms.DecimalField(max_digits=20, decimal_places=2)

class RechercheAchatForm(forms.Form):
    fournisseur = forms.CharField(required=False, label='Fournisseur')
    date_debut = forms.DateField(required=False, label='Date début',  widget=forms.DateInput(attrs={'type': 'date'}))
    date_fin = forms.DateField(required=False, label='Date fin', widget=forms.DateInput(attrs={'type': 'date'}))
    produit = forms.CharField(required=False, label='Produit')
     
class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nomf', 'prenomf', 'adressef', 'telf', 'soldef']

class TransfertForm(forms.ModelForm):
    class Meta:
        model = Transfert
        fields = '__all__'
        labels = {
            'datetr': 'Date de transfert',
            'qtetr': 'Quantité transférée',
            'prixac': 'Prix d\'achat',
            'produit_t': 'Produit transféré',
            'centre_t': 'Centre de destination',
        }
        widgets = {
            'datetr':forms.DateInput(attrs={'type': 'date'}),
        }


class TransfertSearchForm(forms.Form):
    date_filter = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    produit_filter = forms.CharField(max_length=100, required=False)

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = '__all__'
        labels = {
            'qtev': 'Quantité vendue',
            'DateV': 'Date de vente',
            'prixv': 'Prix unitaire',
            'montantv': 'Montant payé',
            'clientv': 'Client',
            'produitv': 'Produit',
        }
        widgets = {
            'clientv': forms.Select(attrs={'class': 'selectpicker'}),
            'produitv': forms.Select(attrs={'class': 'selectpicker'}),
            'DateV': forms.DateInput(attrs={'type': 'date'}),
        }
        

class RechercheEtatStockForm(forms.Form):
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), required=False)
    date_achat = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    nom_produit = forms.CharField(max_length=50, required=False)

class RechercheJournalVenteForm(forms.Form):
    date_vente = forms.DateField(label='Date de vente', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label='Client', required=False)
    produit = forms.ModelChoiceField(queryset=Produit.objects.all(), label='Produit', required=False)

class AjustementStockForm(forms.Form):
    designation = forms.CharField(max_length=50)
    nouvelle_quantite = forms.IntegerField()
    nouveau_prix = forms.FloatField()


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class CompleterCreditForm(forms.ModelForm):
    class Meta:
        model = PaimentCredit
        fields = ['montantpv']

class TransfertForm(forms.ModelForm):
    class Meta:
        model = Transfert
        fields = '__all__'

class TransfertSearchForm(forms.Form):
    date_filter = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    produit_filter = forms.CharField(max_length=100, required=False)       


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = '__all__'
        widgets = {
            'centre': forms.Select(attrs={'class': 'selectpicker'}),
            'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
            'prenome': forms.TextInput(attrs={'readonly': 'readonly'}),
            'adressee': forms.TextInput(attrs={'readonly': 'readonly'}),
            'tele': forms.TextInput(attrs={'readonly': 'readonly'}),
            'salairee': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class CentreForm(forms.ModelForm):
    class Meta:
        model = Centre
        fields = ['designationc']


class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = '__all__'
        widgets = {
            'date_absence': forms.DateInput(attrs={'type': 'date'}),
        }

class AvanceSalaireForm(forms.ModelForm):
    class Meta:
        model = AvanceSalaire
        fields = '__all__'
        widgets = {
            'date_avance': forms.DateInput(attrs={'type': 'date'}),
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')