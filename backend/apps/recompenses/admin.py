from django.contrib import admin
from .models import Badge,BadgeUtilisateur,Certificat,ConfigurationNiveau
admin.site.register(Badge)
admin.site.register(BadgeUtilisateur)
admin.site.register(Certificat)
admin.site.register(ConfigurationNiveau)
