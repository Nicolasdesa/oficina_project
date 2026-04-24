from django.urls import path
from . import views

urlpatterns = [
    path('login/',           views.view_login,      name='login'),
    path('logout/',          views.view_logout,     name='logout'),
    path('alterar-senha/',   views.alterar_senha,   name='alterar_senha'),
    path('usuarios/',        views.lista_usuarios,  name='lista_usuarios'),
    path('usuarios/novo/',   views.novo_usuario,    name='novo_usuario'),
    path('usuarios/<int:pk>/editar/',  views.editar_usuario,  name='editar_usuario'),
    path('usuarios/<int:pk>/excluir/', views.excluir_usuario, name='excluir_usuario'),
]
