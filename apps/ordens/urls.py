from django.urls import path
from . import views

urlpatterns = [
    # Ordens de Serviço
    path('',                    views.lista_ordens,    name='lista_ordens'),
    path('nova/',               views.nova_ordem,      name='nova_ordem'),
    path('<int:pk>/',           views.detalhe_ordem,   name='detalhe_ordem'),
    path('<int:pk>/editar/',    views.editar_ordem,    name='editar_ordem'),
    path('<int:pk>/excluir/',   views.excluir_ordem,   name='excluir_ordem'),
    path('<int:pk>/pdf/',       views.imprimir_os_pdf, name='imprimir_os_pdf'),

    # Clientes
    path('clientes/',           views.lista_clientes,  name='lista_clientes'),
    path('clientes/novo/',      views.novo_cliente,    name='novo_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),

    # Veículos
    path('veiculos/novo/',      views.novo_veiculo,    name='novo_veiculo'),

    # AJAX
    path('ajax/veiculos/',      views.veiculos_por_cliente, name='ajax_veiculos'),
    path('ajax/peca-valor/',    views.valor_peca,           name='ajax_peca_valor'),
    path('ajax/mecanico-valor/', views.valor_hora_mecanico, name='ajax_mecanico_valor'),
]
