from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
import os
import functools

load_dotenv()

class HealthCheckAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def swagger_password_protect(view_func):
    @never_cache
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        swagger_password = os.getenv('SWAGGER_PASSWORD')
        if request.session.get('swagger_authenticated', False):
            return view_func(request, *args, **kwargs)

        if request.method == 'POST':
            entered_password = request.POST.get('password', '').strip()
            if entered_password == swagger_password:
                request.session['swagger_authenticated'] = True
                request.session.modified = True
                request.session.set_expiry(3600)
                return redirect(request.path)
            return render(request, 'swagger_login.html', {'error': 'Mot de passe incorrect'})

        return render(request, 'swagger_login.html')

    return wrapper
