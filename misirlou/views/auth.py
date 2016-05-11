from django.contrib.auth.views import logout
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.generics import GenericAPIView
from rest_framework import status

from misirlou.renderers import SinglePageAppRenderer


class LoginView(GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer,
                        BrowsableAPIRenderer)

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return Response({"message": "Login successful."})
        else:
            return Response({"message": "Login unsuccessful."},
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer,
                        BrowsableAPIRenderer)

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out."})

