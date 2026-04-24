# apps/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.ordens.models import OrdemServico, Cliente, Veiculo
from django.db.models import Count


@login_required
def dashboard(request):
    total_os        = OrdemServico.objects.count()
    em_andamento    = OrdemServico.objects.filter(status='Em andamento').count()
    aguardando      = OrdemServico.objects.filter(status='Aguardando peça').count()
    concluidas      = OrdemServico.objects.filter(status='Concluído').count()
    total_clientes  = Cliente.objects.count()
    ultimas_ordens  = OrdemServico.objects.select_related('cliente', 'veiculo').order_by('-data_entrada')[:5]

    return render(request, 'core/dashboard.html', {
        'total_os':       total_os,
        'em_andamento':   em_andamento,
        'aguardando':     aguardando,
        'concluidas':     concluidas,
        'total_clientes': total_clientes,
        'ultimas_ordens': ultimas_ordens,
    })
