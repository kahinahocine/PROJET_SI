from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q 
from django.http import Http404
from django.db.models import F, Sum, FloatField, Sum, ExpressionWrapper
from .models import Absence, AvanceSalaire, Produit, Fournisseur, Achat, Reglement, Vente, Transfert, EtatStock, Centre, EtatStockCentre, Client, Employe
from .forms import AbsenceForm, AchatForm, AvanceSalaireForm,RechercheAchatForm, PaiementFournisseurForm, VenteForm, FournisseurForm, TransfertForm, EmployeForm, RechercheEtatStockForm, AjustementStockForm, TransfertSearchForm, RechercheJournalVenteForm, CompleterCreditForm, CentreForm
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import CustomUser
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
def acheter_matiere(request):
    if request.method == 'POST':
        form = AchatForm(request.POST)
        if form.is_valid():
            # Enregistrement de l'achat à partir du formulaire
            achat = form.save(commit=False)

            # Mise à jour du solde du fournisseur
            fournisseur = achat.fournisseurA
            fournisseur.soldef -= achat.montantp
            fournisseur.save()

            # Enregistrement de l'achat avec le montant
            achat.save()

            # Mise à jour du stock
            produit = achat.produitA
            # Assuming you have EtatStock model with produit and quantite_en_stock fields
            etat_stock, created = EtatStock.objects.get_or_create(produit=produit)
            etat_stock.quantite_en_stock += achat.qteA
            etat_stock.save()

            return redirect('journal_achats')  # Redirection vers le journal des achats après l'achat

    else:
        form = AchatForm()

    return render(request, 'achat.html', {'form': form})


def modifier_achat(request, pk):
    achat = get_object_or_404(Achat, pk=pk)

    if request.method == 'POST':
        form = AchatForm(request.POST, instance=achat)
        if form.is_valid():
            # Mise à jour du solde du fournisseur
            fournisseur = achat.fournisseurA
            fournisseur.soldef -= achat.montantp  # Restaurez le montant précédent
            fournisseur.soldef += form.cleaned_data['montantp']
            fournisseur.save()


            # Enregistrez la modification de l'achat
            form.save()

            return redirect('journal_achats')  # Redirection vers le journal des achats après la modification
    else:
        form = AchatForm(instance=achat)

    return render(request, 'modifier_achat.html', {'form': form, 'achat': achat})



def modifier_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)

    if request.method == 'POST':
        form = VenteForm(request.POST, instance=vente)
        if form.is_valid():
            vente = form.save(commit=False)
            # Effectuer d'autres opérations si nécessaire
            vente.save()
            return redirect('journal_vente')

    else:
        form = VenteForm(instance=vente)

    return render(request, 'modifier_vente.html', {'form': form, 'vente': vente})






def journal_achats(request):
    achats = Achat.objects.all()
    form = RechercheAchatForm(request.GET)

    if form.is_valid():
        fournisseur = form.cleaned_data.get('fournisseur')
        date_debut = form.cleaned_data.get('date_debut')
        date_fin = form.cleaned_data.get('date_fin')
        produit = form.cleaned_data.get('produit')

        if fournisseur:
            achats = achats.filter(fournisseurA__nomf__icontains=fournisseur)

        if date_debut and date_fin:
            achats = achats.filter(DateA__range=[date_debut, date_fin])

        if produit:
            achats = achats.filter(produitA__designation__icontains=produit)

    return render(request, 'journal_achats.html', {'achats': achats, 'form': form})






def supprimer_achat(request, pk):
    achat = Achat.objects.get(id=pk)
    if request.method == 'POST':
        # Mise à jour du solde du fournisseur lors de la suppression
        achat.produitA.save()
        fournisseur = achat.fournisseurA
        fournisseur.soldef += achat.montantp
        fournisseur.save()

        achat.delete()
        return redirect('journal_achats')

    return render(request, 'supprimer_achat.html', {'achat': achat})






def completer_paiement_fournisseur(request, pk):
    achat = Achat.objects.get(pk=pk)
    if request.method == 'POST':
        form = PaiementFournisseurForm(request.POST)
        if form.is_valid():
            montant_reglement = form.cleaned_data['montant_Reglement']
                # Mise à jour du solde du fournisseur lors du règlement
            fournisseur = achat.fournisseurA
            fournisseur.soldef += montant_reglement
            fournisseur.save()

                # Mise à jour du montant du paiement
            achat.montantp += montant_reglement
            achat.save()
        else:
            return redirect('journal_achats')

    else:
        form = PaiementFournisseurForm()

    return render(request, 'completer_paiement_fournisseur.html', {'form': form, 'achat': achat})






 # fonction qui cree le fournisseur 
def creer_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            return redirect('acheter_matiere')  
    else:
        form = FournisseurForm()

    return render(request, 'creer_fournisseur.html', {'form': form})



# fonction qui nous mene vers la page d,acceuil sans parametre 
def index(request):
    return render(request, 'index.html')
# fonction qui nous permet de transferer un produit vers l'un des 3 centres 





def transfert_matiere(request):
    if request.method == 'POST':
        form = TransfertForm(request.POST)
        if form.is_valid():
            transfert = form.save(commit=False)

            # Vérification si le produit est en stock
            produit_transfere = transfert.produit_t

            try:
                # Tentative de récupération de l'objet EtatStock associé au produit
                etat_stock = EtatStock.objects.get(produit=produit_transfere)

                # Vérification de la quantité en stock
                if etat_stock.quantite_en_stock >= transfert.qtetr:
                    # Déduction de la quantité transférée du stock
                    etat_stock.quantite_en_stock -= transfert.qtetr
                    etat_stock.save()

                    # Enregistrement du transfert
                    transfert.save()

                    messages.success(request, "Le transfert a été enregistré avec succès.")
                    return redirect('journal_transfert')
                else:
                    # Le produit n'a pas assez de stock, affichez un message
                    messages.error(request, "Le produit n'a pas assez de stock.")
            except EtatStock.DoesNotExist:
                # Le produit n'a pas d'objet EtatStock, affichez un message
                messages.error(request, "Le produit n'est pas en stock.")
        else:
            # Le formulaire n'est pas valide, affichez des messages d'erreur
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = TransfertForm()

    return render(request, 'transfert_matiere.html', {'form': form})

def journal_transfert(request):
    transferts = Transfert.objects.all()
    return render(request, 'journal_transfert.html', {'transferts': transferts})

def vente_matiere(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save(commit=False)
            vente.montant_total = vente.qtev * vente.prixv  # Ajoutez cette ligne pour calculer le montant_total

            # Mettre à jour le stock
            produit = vente.produitv
            try:
                etat_stock = EtatStock.objects.get(produit=produit)
                etat_stock.quantite_en_stock -= vente.qtev
                etat_stock.save()
            except EtatStock.DoesNotExist:
                raise Http404("L'objet EtatStock n'existe pas pour le produit spécifié.")

            # Gérer le crédit client
            vente.clientv.creditc -= vente.montantv
            vente.clientv.save()
            vente.save() 
            return redirect('journal_vente')
    else:
        form = VenteForm()

    ventes = Vente.objects.all()
    return render(request, 'vente_matiere.html', {'form': form, 'ventes': ventes})

# supprimer une vente 
def supprimer_vente(request, pk):
    vente = Vente.objects.get(id=pk)

    # Annuler le déstockage du produit associé
    if request.method == 'POST':
     produit = vente.produitv
     etat_stock = EtatStock.objects.get(produit=produit)

     # Annuler la quantité déstockée
     etat_stock.quantite_en_stock += vente.qtev
     etat_stock.save()

    # Annuler l'encaissement correspondant
    vente.clientv.creditc += vente.montantv
    vente.clientv.save()

    vente.delete()
    return redirect('journal_vente')

def completer_credit(request, pk):
    vente = Vente.objects.get(id=pk)

    if request.method == 'POST':
        form = CompleterCreditForm(request.POST)

        if form.is_valid():
            montant_paiement = form.cleaned_data['montantpv']

            if 0 < montant_paiement <= vente.reste_apayer():
                vente.montantv += montant_paiement
                vente.save()

                
                vente.clientv.creditc -= montant_paiement
                vente.clientv.save()

                return redirect('journal_vente')

    else:
        form = CompleterCreditForm()

    return render(request, 'completer_credit.html', {'form': form, 'vente': vente})
# fonction pour consulter le journal des ventes 
def journal_vente(request):
    form = RechercheJournalVenteForm(request.GET)
    ventes = Vente.objects.all()

    if form.is_valid():
        date_vente = form.cleaned_data.get('date_vente')
        client = form.cleaned_data.get('client')
        produit = form.cleaned_data.get('produit')

        if date_vente:
            ventes = ventes.filter(DateV=date_vente)

        if client:
            ventes = ventes.filter(clientv=client)

        if produit:
            ventes = ventes.filter(produitv=produit)

    valeur_totale_ventes = sum(vente.montant_total_calcule() for vente in ventes)
    
    return render(request, 'journal_vente.html', {'ventes': ventes, 'valeur_totale_ventes': valeur_totale_ventes, 'form': form})

# fonction pour consulter lensemble des transferts effectue
def journal_transfert(request):
    if request.method == 'POST':
        form = TransfertSearchForm(request.POST)
        if form.is_valid():
            date_filter = form.cleaned_data.get('date_filter')
            produit_filter = form.cleaned_data.get('produit_filter')

            transferts = Transfert.objects.all()

            if date_filter:
                transferts = transferts.filter(datetr=date_filter)

            if produit_filter:
                transferts = transferts.filter(Q(produit_t__designation__icontains=produit_filter))

            return render(request, 'journal_transfert.html', {'transferts': transferts, 'form': form})

    else:
        form = TransfertSearchForm()
        transferts = Transfert.objects.all()

    return render(request, 'journal_transfert.html', {'transferts': transferts, 'form': form})



from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render
from xhtml2pdf import pisa
from io import BytesIO

def etat_stock(request):
    form = RechercheEtatStockForm(request.GET)
    produits_en_stock = EtatStock.objects.all()
    
    if form.is_valid():
        fournisseur = form.cleaned_data.get('fournisseur')
        date_achat = form.cleaned_data.get('date_achat')
        nom_produit = form.cleaned_data.get('nom_produit')

        if fournisseur:
            produits_en_stock = produits_en_stock.filter(produit__achat__fournisseurA=fournisseur)
        
        if date_achat:
            produits_en_stock = produits_en_stock.filter(produit__achat__DateA=date_achat)
        
        if nom_produit:
            produits_en_stock = produits_en_stock.filter(produit__designation__icontains=nom_produit)

    # Vérifiez si l'utilisateur a demandé un PDF
    if 'pdf' in request.GET:
        template_path = 'etat_stock_pdf.html'
        context = {'produits_en_stock': produits_en_stock}

        # Utilisez xhtml2pdf pour générer le PDF
        template = get_template(template_path)
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="etat_stock.pdf"'

        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)

        if not pdf.err:
            response.write(buffer.getvalue())
            buffer.close()
            return response

    return render(request, 'EtatStock.html', {'form': form, 'produits_en_stock': produits_en_stock})





def ajustement_stock(request):
    if request.method == 'POST':
        form = AjustementStockForm(request.POST)
        if form.is_valid():
      
            designation = form.cleaned_data['designation']
            nouvelle_quantite = form.cleaned_data['nouvelle_quantite']
            nouveau_prix = form.cleaned_data['nouveau_prix']

            try:
                # Rechercher le produit correspondant à la désignation
                produit = Produit.objects.get(designation=designation)
                # Rechercher l'état du stock associé au produit
                etat_stock = EtatStock.objects.get(produit=produit)
                # Mettre à jour la quantité en stock et le prix du produit
                etat_stock.quantite_en_stock = nouvelle_quantite
                produit.prix = nouveau_prix
                # Sauvegarder les modifications dans la base de données
                etat_stock.save()
                produit.save()
                return redirect('ajustement_stock')
            except Produit.DoesNotExist:
                # Gérer le cas où le produit n'est pas trouvé
                pass
            
            except EtatStock.DoesNotExist:
                # Gérer le cas où l'état du stock n'est pas trouvé
                pass
    else:
        form = AjustementStockForm()
    # Récupérer tous les états du stock avec les produits associés
    stock_actuel = EtatStock.objects.select_related('produit').all()
    return render(request, 'ajustement_stock.html', {'form': form, 'stock_actuel': stock_actuel})

from .forms import ClientForm

def creer_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            # Ajoutez des logiques supplémentaires si nécessaire
            return redirect('index')  # Redirigez vers la page d'accueil ou toute autre page appropriée
    else:
        form = ClientForm()

    return render(request, 'creer_client.html', {'form': form})





def calculer_valeur_totalestock():
    stock=EtatStock.all()
    total=sum()

def transferts_recus(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)
    transferts_recus = Transfert.objects.filter(centre_t=centre)

    # Traitement du formulaire de recherche
    form = TransfertSearchForm(request.GET)
    if form.is_valid():
        date_filter = form.cleaned_data.get('date_filter')
        produit_filter = form.cleaned_data.get('produit_filter')

        if date_filter:
            transferts_recus = transferts_recus.filter(datetr=date_filter)
        
        if produit_filter:
            transferts_recus = transferts_recus.filter(produit_t__designation__icontains=produit_filter)

    return render(request, 'transferts_recus.html', {
        'centre': centre,
        'transferts_recus': transferts_recus,
        'form': form,
    })



###### manipulaion des produits 


def ajouter_produit(request):
    if request.method == 'POST':
        designation = request.POST.get('designation')
        prix = request.POST.get('prix')
        Produit.inserer_produit(designation=designation, prix=prix)
        return redirect('gerer_produits')
    return render(request, 'ajouter_produit.html')

def modifier_produit(request, pk):
    produit = Produit.objects.get(pk=pk)
    if request.method == 'POST':
        new_designation = request.POST.get('new_designation')
        new_prix = request.POST.get('new_prix')
        Produit.modifier_produit(pk, new_designation, new_prix)
        return redirect('gerer_produits')
    return render(request, 'modifier_produit.html', {'produit': produit})

def supprimer_produit(request, pk):
    Produit.supprimer_produit(pk)
    return redirect('gerer_produits')

def rechercher_produit(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')
        produits = Produit.rechercher_produit(keyword)
        return render(request, 'gestionProduit.html', {'produits': produits, 'keyword': keyword})

def consulter_produits(request):
    produits = Produit.consulter_produits()
    return render(request, 'gestionProduit.html', {'produits': produits})

def imprimer_produits(request):
    produits = Produit.imprimer_produits()
    for produit in produits:
        print(f"ID: {produit.id}, Designation: {produit.designation}, Prix: {produit.prix}")
    return redirect('gerer_produits')



def gerer_items(request):
    return render(request, 'gerer.items.html')



def consulter_clients(request):
    clients = Client.consulter_clients()
    return render(request, 'gerer_client.html', {'clients': clients})

def modifier_client(request,pk):
    client = Client.objects.get(pk=pk)

    if request.method == 'POST':
        nomc = request.POST['nomc']
        prenomc = request.POST['prenomc']
        adressec = request.POST['adressec']
        telc = request.POST['telc']
        creditc = request.POST['creditc']
        Client.modifier_client(pk, nomc, prenomc, adressec, telc, creditc)
        return redirect('gerer_clients')

    return render(request, 'modifier_client.html', {'client': client})

def supprimer_client(request, pk):
    Client.supprimer_client(pk)
    return redirect('gerer_clients')

def rechercher_clients(request):
    keyword = request.GET.get('keyword', '')
    clients = Client.rechercher_clients(keyword)
    return render(request, 'gerer_client.html', {'clients': clients})


def modifier_fournisseur(request, pk):
    fournisseur = Fournisseur.objects.get(pk=pk)

    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('gerer_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)

    return render(request, 'modifier_fournisseur.html', {'form': form, 'fournisseur': fournisseur})

def gerer_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        fournisseurs = Fournisseur.objects.filter(nomf__icontains=keyword) | Fournisseur.objects.filter(prenomf__icontains=keyword)

    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_fournisseurs')
    else:
        form = FournisseurForm()

    return render(request, 'gerer_fournisseur.html', {'fournisseurs': fournisseurs, 'form': form})

def supprimer_fournisseur(request, pk):
    fournisseur = Fournisseur.objects.get(pk=pk)
    fournisseur.delete()
    return redirect('gerer_fournisseurs')


def gerer_employes(request):
    employes = Employe.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        employes = Employe.objects.filter(nome__icontains=keyword) | Employe.objects.filter(prenome__icontains=keyword)

    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_employes')
    else:
        form = EmployeForm()

    return render(request, 'gerer_employe.html', {'employes': employes})


def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_employes')  
    else:
        form = EmployeForm()

    return render(request, 'ajouter_employe.html', {'form': form})

def modifier_employe(request, pk):
    employe = Employe.objects.get(pk=pk)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('gerer_employes')
    else:
        form = EmployeForm(instance=employe)

    return render(request, 'modifier_employe.html', {'form': form, 'employe': employe})

def supprimer_employe(request, pk):
    employe = Employe.objects.get(pk=pk)
    employe.delete()
    return redirect('gerer_employes')


def gerer_centre(request):

    centres = Centre.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        centres = Centre.objects.filter(designationc__icontains=keyword)

    if request.method == 'POST':
        form = CentreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_centres')
    else:
        form = CentreForm()

    return render(request, 'gerer_centre.html', {'centres': centres})

def ajouter_centre(request):
    if request.method == 'POST':
        form = CentreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_centre')
    else:
        form = CentreForm()
    return render(request, 'ajouter_centre.html', {'form': form})

def modifier_centre(request, pk):
    centre = Centre.objects.get(pk=pk)
    if request.method == 'POST':
        form = CentreForm(request.POST, instance=centre)
        if form.is_valid():
            form.save()
            return redirect('gerer_centre')
    else:
        form = CentreForm(instance=centre)
    return render(request, 'modifier_centre.html', {'form': form})

def supprimer_centre(request, pk):
    centre = Centre.objects.get(pk=pk)
    centre.delete()
    return redirect('gerer_centre')
	
	
	
def choix_fonctionnalites(request, centre_id):
    return render(request, 'choix_fonctionnalites.html', {'centre_id': centre_id})

def centre_menu(request, centre_id):
    return redirect('choix_fonctionnalites', centre_id=centre_id)	


def transferts_recus(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)
    transferts_recus = Transfert.objects.filter(centre_t=centre)

    # Traitement du formulaire de recherche
    form = TransfertSearchForm(request.GET)
    if form.is_valid():
        date_filter = form.cleaned_data.get('date_filter')
        produit_filter = form.cleaned_data.get('produit_filter')

        if date_filter:
            transferts_recus = transferts_recus.filter(datetr=date_filter)

        if produit_filter:
            # Utilisez le champ correct dans le modèle Transfert
            transferts_recus = transferts_recus.filter(produit_t__designation__icontains=produit_filter)

        # Mise à jour des stocks dans le centre
        for transfert in transferts_recus:
            produit = transfert.produit_t  # Utilisez le champ correct ici aussi
            quantite_transferee = transfert.qtetr

            # Vérifier si l'objet EtatStockCentre existe pour ce produit et ce centre
            etat_stock_centre, created = EtatStockCentre.objects.get_or_create(
                produit_stocke=produit,  # Utilisez le champ correct ici aussi
                centre=centre,
                defaults={'quantite_en_stock_centre': 0}  # Initialiser à 0 si l'objet est nouvellement créé
            )

            # Mettre à jour la quantité en stock dans le centre
            etat_stock_centre.quantite_en_stock_centre = F('quantite_en_stock_centre') + quantite_transferee
            etat_stock_centre.save()

    return render(request, 'transferts_recus.html', {
        'centre': centre,
        'transferts_recus': transferts_recus,
        'form': form,
    })


def etat_stock_centre(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)
    produits_en_stock_centre = EtatStockCentre.objects.filter(centre=centre)

    # Initialisez le formulaire avec les données du formulaire POST s'il est soumis
    form = TransfertSearchForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            date_filter = form.cleaned_data.get('date_filter')
            produit_filter = form.cleaned_data.get('produit_filter')

            transferts_recus = Transfert.objects.filter(centre_t=centre)

            if date_filter:
                transferts_recus = transferts_recus.filter(datetr=date_filter)

            if produit_filter:
                transferts_recus = transferts_recus.filter(produit_t__designation__icontains=produit_filter)

            # Mise à jour des stocks (similaire à votre code actuel)

            if 'pdf' in request.POST:
                template_path = 'etat_stock_centre_pdf.html'
                context = {'centre': centre, 'produits_en_stock_centre': produits_en_stock_centre}

                template = get_template(template_path)
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="etat_stock_centre.pdf"'

                buffer = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)

                if not pdf.err:
                    response.write(buffer.getvalue())
                    buffer.close()
                    return response

    return render(request, 'etat_stock_centre.html', {
        'centre': centre,
        'produits_en_stock_centre': produits_en_stock_centre,
        'form': form,
    })


def effectuer_vente_centre(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)

    if request.method == 'POST':
        form = VenteForm(request.POST)

        if form.is_valid():
            vente = form.save(commit=False)

            # Vérifier si une vente similaire existe déjà
            existing_vente = Vente.objects.filter(
                produitv=vente.produitv,
                clientv=vente.clientv,
                DateV=vente.DateV
            ).first()

            if existing_vente:
                # Une vente similaire existe déjà, vous pouvez gérer cela comme vous le souhaitez
                messages.error(request, "Cette vente existe déjà.")
            else:
                # Vérifier si la quantité en stock est suffisante
                produit = vente.produitv

                try:
                    # Récupérer l'objet EtatStockCentre associé au produit et au centre
                    etat_stock = EtatStockCentre.objects.get(produit_stocke=produit, centre=centre)

                    # Vérifier si la quantité en stock est suffisante
                    if etat_stock.quantite_en_stock_centre >= vente.qtev:
                        # Enregistrer la vente avec le centre spécifique
                        vente.centre = centre  # Ajoutez cette ligne pour spécifier le centre
                        vente.save()

                        # Décrémenter la quantité en stock du centre
                        etat_stock.quantite_en_stock_centre -= vente.qtev
                        etat_stock.save()

                        # Rediriger vers le journal des ventes pour le centre spécifique
                        return redirect('journal_vente_centre', centre_id=centre.id)
                    else:
                        # Afficher un message d'erreur si la quantité en stock est insuffisante
                        messages.error(request, "La quantité en stock est insuffisante.")
                except EtatStockCentre.DoesNotExist:
                    # Gérer le cas où l'objet EtatStockCentre pour le produit dans le centre n'existe pas
                    messages.error(request, "Le produit n'est pas en stock dans ce centre.")
    else:
        form = VenteForm()

    # Filtrez les produits disponibles dans ce centre pour le formulaire
    form.fields['produitv'].queryset = Produit.objects.filter(transfert__centre_t=centre)

    return render(request, 'vente_matiere.html', {'form': form, 'centre': centre})



def journal_vente_centre(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)
    form = RechercheJournalVenteForm(request.GET)
    ventes_centre = Vente.objects.filter(produitv__transfert__centre_t=centre).distinct()

    if form.is_valid():
        date_vente = form.cleaned_data.get('date_vente')
        client = form.cleaned_data.get('client')
        produit = form.cleaned_data.get('produit')

        if date_vente:
            ventes_centre = ventes_centre.filter(DateV=date_vente)

        if client:
            ventes_centre = ventes_centre.filter(clientv=client)

        if produit:
            ventes_centre = ventes_centre.filter(produitv=produit)

    valeur_totale_ventes_centre = ventes_centre.aggregate(
        total_ventes_centre=Sum(F('qtev') * F('prixv'), output_field=FloatField())
    )['total_ventes_centre'] or 0

    return render(request, 'journal_vente_centre.html', {'centre': centre, 'ventes_centre': ventes_centre, 'valeur_totale_ventes_centre': valeur_totale_ventes_centre, 'form': form})


def supprimer_vente_centre(request, centre_id, vente_id):
    centre = get_object_or_404(Centre, id=centre_id)
    vente = get_object_or_404(Vente, id=vente_id, centre=centre)

    # Annuler le déstockage du produit associé
    if request.method == 'POST':
        produit = vente.produitv
        etat_stock_centre = EtatStockCentre.objects.get(  produit_stocke=vente.produitv, centre=Centre.objects.get(id=centre_id))

        # Annuler la quantité déstockée
        etat_stock_centre.quantite_en_stock_centre += vente.qtev
        etat_stock_centre.save()

    # Annuler l'encaissement correspondant
    vente.clientv.creditc += vente.montantv
    vente.clientv.save()

    vente.delete()
    return redirect('journal_vente_centre', centre_id=centre.id)


def gerer_employes_centre(request, centre_id):
    centre = get_object_or_404(Centre, id=centre_id)
    employes = Employe.objects.filter(centre=centre)

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        employes = employes.filter(nome__icontains=keyword) | employes.filter(prenome__icontains=keyword)

    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            employe = form.save(commit=False)
            employe.centre = centre
            employe.save()
            return redirect('gerer_employes_centre', centre_id=centre.id)
    else:
        form = EmployeForm()

    return render(request, 'gerer_employe_centre.html', {'centre': centre, 'employes': employes, 'form': form})




def calcul_salaire_mensuel(request, employe_id):
    employe = Employe.objects.get(pk=employe_id)
    salaire_quotidien = employe.salairee

    absences = Absence.objects.filter(employe=employe, date_absence__month=request.month)
    avances = AvanceSalaire.objects.filter(employe=employe, date_avance__month=request.month)

    retenues_absences = absences.aggregate(Sum('salaire_quotidien'))['salaire_quotidien__sum'] or 0
    total_avances = avances.aggregate(Sum('montant'))['montant__sum'] or 0

    salaire_mensuel = (30 - absences.count()) * salaire_quotidien - retenues_absences + total_avances

    return render(request, 'salaire_mensuel.html', {'employe': employe, 'salaire_mensuel': salaire_mensuel})

def saisie_absence(request):
    if request.method == 'POST':
        form = AbsenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Remplacez 'page_d_accueil' par l'URL de votre choix
    else:
        form = AbsenceForm()

    return render(request, 'absence_form.html', {'form': form, 'employes': Employe.objects.all()})

def saisie_avance(request):
    if request.method == 'POST':
        form = AvanceSalaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Remplacez 'page_d_accueil' par l'URL de votre choix
    else:
        form = AvanceSalaireForm()

    return render(request, 'avance_form.html', {'form': form, 'employes': Employe.objects.all()})



def analyse_achat(request):
    # Taux d'évolution des achats
    achats_total = Achat.objects.aggregate(total_achats=Sum('montantp'))
    achats_mois_precedent = Achat.objects.filter(DateA__month=12).exclude(DateA__year=timezone.now().year)

    # Agréger le montant des achats du mois précédent
    achats_montant_mois_precedent = achats_mois_precedent.aggregate(total_achats=Sum('montantp'))

    taux_evolution = 0
    if achats_total['total_achats'] and achats_montant_mois_precedent['total_achats']:
        taux_evolution = ((achats_total['total_achats'] - achats_montant_mois_precedent['total_achats']) /
                          achats_montant_mois_precedent['total_achats']) * 100

    # Top Fournisseurs
    top_fournisseurs = Fournisseur.objects.annotate(total_achats=Sum('achat__montantp')).order_by('-total_achats')[:10]

    return render(request, 'analyse_achat.html', {'taux_evolution': taux_evolution, 'top_fournisseurs': top_fournisseurs})


def top_fournisseurs(request):
    # Récupérer l'année et le mois des paramètres de requête, avec des valeurs par défaut
    annee = request.GET.get('annee', datetime.now().year)
    mois = request.GET.get('mois')

    # Commencer la requête pour les achats
    achats = Achat.objects.all()

    # Filtrer par année et mois si spécifié
    if annee:
        achats = achats.filter(DateA__year=annee)
    if mois:
        achats = achats.filter(DateA__month=mois)

    # Calculer le total des achats par fournisseur
    fournisseurs_totals = achats.values('fournisseurA__nomf') \
                                .annotate(total_achat=Sum('montantp')) \
                                .order_by('-total_achat')

    # Prendre seulement les 10 meilleurs fournisseurs
    top_fournisseurs = fournisseurs_totals[:10]

    context = {
        'top_fournisseurs': top_fournisseurs,
        'selected_annee': annee,
        'selected_mois': mois or '',  # Un mois vide si non spécifié
    }
    return render(request, 'top_fournisseurs.html', context)



def combined_ventes_view(request):
    annee = request.GET.get('annee', datetime.now().year)
    mois = request.GET.get('mois')

    # Traitement pour les centres
    centres_data = []
    for centre in Centre.objects.all():
        ventes_centre = Vente.objects.filter(produitv__transfert__centre_t=centre, DateV__year=annee)
        if mois:
            ventes_centre = ventes_centre.filter(DateV__month=mois)
        top_produits_centre = ventes_centre.values('produitv__designation') \
                                           .annotate(total_vendu=Sum('qtev')) \
                                           .order_by('-total_vendu')[:5]
        centres_data.append({'centre': centre, 'top_produits': top_produits_centre})

    # Traitement pour le magasin principal
    ventes_magasin = Vente.objects.filter(DateV__year=annee)
    if mois:
        ventes_magasin = ventes_magasin.filter(DateV__month=mois)
    top_produits_magasin = ventes_magasin.values('produitv__designation') \
                                         .annotate(total_vendu=Sum('qtev')) \
                                         .order_by('-total_vendu')[:5]

    return render(request, 'combined_ventes.html', {
        'centres_data': centres_data,
        'top_produits_magasin': top_produits_magasin,
        'selected_annee': annee,
        'selected_mois': mois or ''
    })






def analyse_ventes(request):
    annee = int(request.GET.get('annee', datetime.now().year))
    mois = request.GET.get('mois')

    ventes = Vente.objects.all()
    if annee:
        ventes = ventes.filter(DateV__year=annee)
    if mois:
        mois = int(mois)
        ventes = ventes.filter(DateV__month=mois)



    ventes_avec_benefice = ventes.annotate(
        benefice=ExpressionWrapper(
            F('prixv') * F('qtev') - F('produitv__prix') * F('qtev'),
            output_field=FloatField()
        )
    )

    benefice_total = ventes_avec_benefice.aggregate(Sum('benefice'))['benefice__sum'] or 0

  
    annee_precedente = annee - 1
    ventes_precedentes = Vente.objects.filter(DateV__year=annee_precedente)

    ventes_precedentes_avec_benefice = ventes_precedentes.annotate(
        benefice=ExpressionWrapper(
            F('prixv') * F('qtev') - F('produitv__prix') * F('qtev'),
            output_field=FloatField()
        )
    )

    benefice_precedent = ventes_precedentes_avec_benefice.aggregate(Sum('benefice'))['benefice__sum'] or 0

    taux_evolution_benefice = ((benefice_total - benefice_precedent) / benefice_precedent * 100) if benefice_precedent else 0

    context = {
        'annee': annee,
        'mois': mois,
        'ventes': ventes_avec_benefice,
        'benefice_total': benefice_total,
        'taux_evolution_benefice': taux_evolution_benefice
    }

    return render(request, 'analyse_ventes.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will be inactive until email confirmation
            user.save()
            # Send email with confirmation code
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': 'your-domain.com',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, 'from@example.com', [user.email], fail_silently=False)
            return redirect('account_activation_sent')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    # The method to activate user's account will go here
    pass