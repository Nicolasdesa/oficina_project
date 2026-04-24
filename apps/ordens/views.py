from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from .models import OrdemServico, Cliente, Veiculo, Mecanico, Peca
from .forms import (
    OrdemServicoForm, ItemPecaFormSet, ItemMaoObraFormSet,
    ClienteForm, VeiculoForm,
)
from .pdf_generator import gerar_pdf_os


# ── Ordens de Serviço ─────────────────────────────────────────────────────────

@login_required
def lista_ordens(request):
    q      = request.GET.get('q', '')
    status = request.GET.get('status', '')
    ordens = OrdemServico.objects.select_related('cliente', 'veiculo').all()

    if q:
        ordens = ordens.filter(
            Q(cliente__nome__icontains=q) |
            Q(veiculo__placa__icontains=q) |
            Q(descricao_servico__icontains=q)
        )
    if status:
        ordens = ordens.filter(status=status)

    return render(request, 'ordens/lista_ordens.html', {
        'ordens': ordens,
        'q': q,
        'status_filtro': status,
        'status_choices': OrdemServico.STATUS_CHOICES,
    })


@login_required
def detalhe_ordem(request, pk):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related('cliente', 'veiculo')
                            .prefetch_related('itens_peca__peca', 'itens_mo__mecanico'),
        pk=pk,
    )
    return render(request, 'ordens/detalhe_ordem.html', {'ordem': ordem})


@login_required
def nova_ordem(request):
    if request.method == 'POST':
        form          = OrdemServicoForm(request.POST)
        formset_peca  = ItemPecaFormSet(request.POST, prefix='pecas')
        formset_mo    = ItemMaoObraFormSet(request.POST, prefix='mo')

        if form.is_valid() and formset_peca.is_valid() and formset_mo.is_valid():
            ordem = form.save()
            formset_peca.instance = ordem
            formset_mo.instance   = ordem
            formset_peca.save()
            formset_mo.save()
            messages.success(request, f'OS {ordem.numero_os or ordem.pk} criada com sucesso!')
            return redirect('detalhe_ordem', pk=ordem.pk)
    else:
        form         = OrdemServicoForm()
        formset_peca = ItemPecaFormSet(prefix='pecas')
        formset_mo   = ItemMaoObraFormSet(prefix='mo')
        # No GET, começa sem veículos (AJAX carrega ao selecionar cliente)
        form.fields['veiculo'].queryset = Veiculo.objects.none()

    return render(request, 'ordens/form_ordem.html', {
        'form': form,
        'formset_peca': formset_peca,
        'formset_mo': formset_mo,
        'titulo': 'Nova Ordem de Serviço',
    })


@login_required
def editar_ordem(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    if request.method == 'POST':
        form         = OrdemServicoForm(request.POST, instance=ordem)
        formset_peca = ItemPecaFormSet(request.POST, instance=ordem, prefix='pecas')
        formset_mo   = ItemMaoObraFormSet(request.POST, instance=ordem, prefix='mo')

        if form.is_valid() and formset_peca.is_valid() and formset_mo.is_valid():
            form.save()
            formset_peca.save()
            formset_mo.save()
            messages.success(request, 'OS atualizada com sucesso!')
            return redirect('detalhe_ordem', pk=ordem.pk)
    else:
        form         = OrdemServicoForm(instance=ordem)
        formset_peca = ItemPecaFormSet(instance=ordem, prefix='pecas')
        formset_mo   = ItemMaoObraFormSet(instance=ordem, prefix='mo')

    return render(request, 'ordens/form_ordem.html', {
        'form': form,
        'formset_peca': formset_peca,
        'formset_mo': formset_mo,
        'titulo': f'Editar {ordem.numero_os or f"OS-{pk:05d}"}',
        'ordem': ordem,
    })


@login_required
def excluir_ordem(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    if request.method == 'POST':
        num = ordem.numero_os or f'OS-{pk:05d}'
        ordem.delete()
        messages.success(request, f'{num} excluída.')
        return redirect('lista_ordens')
    return render(request, 'ordens/confirmar_exclusao.html', {'ordem': ordem})


# ── PDF ───────────────────────────────────────────────────────────────────────

@login_required
def imprimir_os_pdf(request, pk):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related('cliente', 'veiculo')
                            .prefetch_related('itens_peca__peca', 'itens_mo__mecanico'),
        pk=pk,
    )
    pdf_bytes = gerar_pdf_os(ordem)
    filename  = f'OS-{ordem.pk:05d}.pdf'
    response  = HttpResponse(pdf_bytes, content_type='application/pdf')
    # 'inline' → abre no navegador; troque por 'attachment' para forçar download
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


# ── AJAX: veículos por cliente ────────────────────────────────────────────────

@login_required
def veiculos_por_cliente(request):
    cliente_id = request.GET.get('cliente_id')
    veiculos = Veiculo.objects.filter(cliente_id=cliente_id)
    data = [{'id': v.pk, 'descricao': v.descricao, 'placa': v.placa} for v in veiculos]
    return JsonResponse({'veiculos': data})


# ── AJAX: valor da peça ────────────────────────────────────────────────────────

@login_required
def valor_peca(request):
    peca_id = request.GET.get('peca_id')
    try:
        peca = Peca.objects.get(peca_id=peca_id)
        return JsonResponse({'valor': float(peca.valor_unitario)})
    except Peca.DoesNotExist:
        return JsonResponse({'valor': 0})


# ── AJAX: valor hora do mecânico ──────────────────────────────────────────────

@login_required
def valor_hora_mecanico(request):
    mec_id = request.GET.get('mecanico_id')
    try:
        mec = Mecanico.objects.get(mecanico_id=mec_id)
        return JsonResponse({'valor': float(mec.valor_hora)})
    except Mecanico.DoesNotExist:
        return JsonResponse({'valor': 0})


# ── Clientes ──────────────────────────────────────────────────────────────────

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'ordens/lista_clientes.html', {'clientes': clientes})


@login_required
def novo_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            c = form.save()
            messages.success(request, f'Cliente {c.nome} cadastrado!')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'ordens/form_cliente.html', {'form': form, 'titulo': 'Novo Cliente'})


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado!')
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'ordens/form_cliente.html', {'form': form, 'titulo': 'Editar Cliente'})


# ── Veículos ──────────────────────────────────────────────────────────────────

@login_required
def novo_veiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            v = form.save()
            messages.success(request, f'Veículo {v.descricao} cadastrado!')
            return redirect('lista_clientes')
    else:
        form = VeiculoForm()
    return render(request, 'ordens/form_veiculo.html', {'form': form, 'titulo': 'Novo Veículo'})
