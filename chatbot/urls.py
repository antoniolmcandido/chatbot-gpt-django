# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Rota para a página principal que renderiza o chat
    path("", views.chat_view, name="chat"),
    # Rota da API que recebe as perguntas e devolve as respostas
    path("api/chat/", views.chat_api, name="chat_api"),
]
