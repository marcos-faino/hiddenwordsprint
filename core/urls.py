from django.urls import path

from core.views import Home, CacaPalavras

urlpatterns = [
    path("", Home.as_view(), name='cacapalavras'),
]