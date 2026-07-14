from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.user.permissions import IsModeratorUser
from .models import Notification
from .serializers import NotificationSerializer

class MesNotificationsView(APIView):
    permission_classes=[IsModeratorUser]
    authentication_classes=[]
    def get(self, request):
        qs=Notification.objects.filter(destinataire=request.user)
        return Response(NotificationSerializer(qs, many=True).data)

class LireNotificationView(APIView):
    permission_classes=[IsModeratorUser]
    authentication_classes=[]
    def post(self, request, notification_id):
        n=Notification.objects.filter(id=notification_id,destinataire=request.user).first()
        if not n: return Response({'detail':'Notification introuvable.'},status=404)
        if not n.est_lue:
            n.est_lue=True; n.lue_le=timezone.now(); n.save(update_fields=['est_lue','lue_le'])
        return Response(NotificationSerializer(n).data)

class ToutMarquerLuView(APIView):
    permission_classes=[IsModeratorUser]
    authentication_classes=[]
    def post(self, request):
        Notification.objects.filter(destinataire=request.user,est_lue=False).update(est_lue=True,lue_le=timezone.now())
        return Response({'detail':'Toutes les notifications ont été marquées comme lues.'})
