from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Produit
from .models import Client
from .models import Fournisseur
from .models import Centre
from .models import Employe
from .models import Reglement
from .models import Transfert
from .models import Vente
from .models import PaimentCredit
from .models import Achat
from .models import gestionEmploye
from .models import EtatStock
from .models import EtatStockCentre


# Register your models here.
admin.site.register(Produit)
admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Centre)
admin.site.register(Employe)
admin.site.register(Reglement)
admin.site.register(Transfert)
admin.site.register(Vente)
admin.site.register(PaimentCredit)
admin.site.register(Achat)
admin.site.register(gestionEmploye)
admin.site.register(EtatStock)
admin.site.register(EtatStockCentre)