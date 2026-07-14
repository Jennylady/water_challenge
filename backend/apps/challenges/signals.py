from django.dispatch import Signal


# Les applications notifications/recompenses peuvent écouter ces événements sans créer
# de dépendance circulaire avec challenges.
defi_debloque = Signal()
soumission_envoyee = Signal()
soumission_traitee = Signal()