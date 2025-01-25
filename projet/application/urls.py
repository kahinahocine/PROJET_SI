from django.urls import path
from . import views

urlpatterns = [
    path('acheter_matiere/', views.acheter_matiere, name='acheter_matiere'),
    path('journal_achats/', views.journal_achats, name='journal_achats'),
    path('supprimer_achat/<int:pk>/', views.supprimer_achat, name='supprimer_achat'),
    path('completer_paiement_fournisseur/<int:pk>/', views.completer_paiement_fournisseur, name='completer_paiement_fournisseur'),
    path('creer_fournisseur/', views.creer_fournisseur, name='creer_fournisseur'),
    path('index/', views.index, name='index'),
    path('transfertMat', views.transfert_matiere, name='transfert_matiere'),
    path('ventreMat/', views.vente_matiere, name='vente_matiere'),
    path('journalVen', views.journal_vente, name='journal_vente'),
    path('journalTran', views.journal_transfert, name='journal_transfert'),
    path('etat_stock/', views.etat_stock , name='etat_stock'),
    path('ajustement_stock/', views.ajustement_stock, name='ajustement_stock'),
    

    path('creer_client/', views.creer_client, name='creer_client'),
    path('supprimer_vente/<int:pk>/', views.supprimer_vente, name='supprimer_vente'),
    path('completer_credit/<int:pk>/', views.completer_credit, name='completer_credit'),
    path('modifier_achat/<int:pk>/', views.modifier_achat, name='modifier_achat'),
    path('modifier_vente/<int:pk>/', views.modifier_vente, name='modifier_vente'),
    path('centre/<int:centre_id>/transferts_recus/', views.transferts_recus, name='transferts_recus'),
    path('gerer_employes/centre/<int:centre_id>/',  views.gerer_employes_centre, name='gerer_employes_centre'),
    path('journal_vente_centre/<int:centre_id>/', views.journal_vente_centre, name='journal_vente_centre'),
    path('supprimer_vente_centre/<int:centre_id>/<int:vente_id>/', views.supprimer_vente_centre, name='supprimer_vente_centre'),
  


    path('gerer_items/', views.gerer_items, name='gerer_items'),
    path('ajouter_produit/', views.ajouter_produit, name='ajouter_produit'),
    path('modifier_produit/<int:pk>//', views.modifier_produit, name='modifier_produit'),
    path('supprimer_produit/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),
    path('rechercher_produit/', views.rechercher_produit, name='rechercher_produit'),
    path('gerer_produits/', views.consulter_produits, name='gerer_produits'),
    path('imprimer_produits/', views.imprimer_produits, name='imprimer_produits'),

    path('gerer_clients/', views.consulter_clients, name='gerer_clients'),
    path('modifier_client/<int:pk>/', views.modifier_client, name='modifier_client'),
    path('supprimer_client/<int:pk>/', views.supprimer_client, name='supprimer_client'),
    path('rechercher_clients/', views.rechercher_clients, name='rechercher_clients'),
    
    path('gerer_fournisseurs/', views.gerer_fournisseurs, name='gerer_fournisseurs'),
    path('modifier_fournisseur/<int:pk>/', views.modifier_fournisseur, name='modifier_fournisseur'),
    path('supprimer_fournisseur/<int:pk>/', views.supprimer_fournisseur, name='supprimer_fournisseur'),

    path('gerer_employes/', views.gerer_employes, name='gerer_employes'),
    path('ajouter_employe/', views.ajouter_employe, name='ajouter_employe'),
    path('modifier_employe/<int:pk>/', views.modifier_employe, name='modifier_employe'),
    path('supprimer_employe/<int:pk>/', views.supprimer_employe, name='supprimer_employe'),

    path('gerer_centre/', views.gerer_centre, name='gerer_centre'),
    path('ajouter_centre/', views.ajouter_centre, name='ajouter_centre'),
    path('modifier_centre/<int:pk>/', views.modifier_centre, name='modifier_centre'),
    path('supprimer_centre/<int:pk>/', views.supprimer_centre, name='supprimer_centre'),

    path('centre_menu/<int:centre_id>/', views.centre_menu, name='centre_menu'),
    path('choix_fonctionnalites/<int:centre_id>/', views.choix_fonctionnalites, name='choix_fonctionnalites'),
    path('centre/<int:centre_id>/transferts_recus/', views.transferts_recus, name='transferts_recus'),
    path('centre/<int:centre_id>/etat_stock/', views.etat_stock_centre, name='etat_stock_centre'),
    path('effectuer_vente_centre/<int:centre_id>/', views.effectuer_vente_centre, name='effectuer_vente_centre'),
    path('journal_vente_centre/<int:centre_id>/', views.journal_vente_centre, name='journal_vente_centre'),


    path('calcul_salaire_mensuel/<int:employe_id>/', views.calcul_salaire_mensuel, name='calcul_salaire_mensuel'),
    path('saisie_absence/', views.saisie_absence, name='saisie_absence'),
    path('saisie_avance/', views.saisie_avance, name='saisie_avance'),


    path('analyse-achat/', views.analyse_achat, name='analyse_achat'),

    path('top-fournisseurs/', views.top_fournisseurs, name='top_fournisseurs'),
    path('ventes-combinees/', views.combined_ventes_view, name='ventes_combinees'),
     path('analyse-ventes/', views.analyse_ventes, name='analyse_ventes')
]
