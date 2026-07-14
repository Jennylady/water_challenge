from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.user.permissions import IsModeratorUser
from .models import BadgeUtilisateur,Certificat,ConfigurationNiveau
from .serializers import BadgeUtilisateurSerializer,CertificatSerializer,ConfigurationNiveauSerializer
class MesRecompensesView(APIView):
    permission_classes=[IsModeratorUser]; authentication_classes=[]
    def get(self,request):
        return Response({'badges':BadgeUtilisateurSerializer(BadgeUtilisateur.objects.filter(utilisateur=request.user),many=True).data,'certificats':CertificatSerializer(Certificat.objects.filter(utilisateur=request.user),many=True).data})
