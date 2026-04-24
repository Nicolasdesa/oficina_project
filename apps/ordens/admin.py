from django.contrib import admin
from .models import Cliente, Veiculo, Mecanico, OrdemServico, Peca, ItemPeca, ItemMaoObra


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ['nome', 'cpf_cnpj', 'telefone', 'email']
    search_fields = ['nome', 'cpf_cnpj', 'telefone']


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display  = ['descricao', 'placa', 'cliente', 'ano', 'cor']
    search_fields = ['descricao', 'placa']
    list_filter   = ['ano']


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especialidade', 'valor_hora', 'ativo']
    list_filter  = ['ativo']


class ItemPecaInline(admin.TabularInline):
    model  = ItemPeca
    extra  = 0
    fields = ['peca', 'quantidade', 'valor_unitario']


class ItemMaoObraInline(admin.TabularInline):
    model  = ItemMaoObra
    extra  = 0
    fields = ['mecanico', 'tipo_servico', 'horas_trabalhadas', 'valor_hora']


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display  = ['numero_os', 'cliente', 'veiculo', 'status', 'data_entrada', 'data_saida']
    list_filter   = ['status']
    search_fields = ['cliente__nome', 'veiculo__placa', 'descricao_servico']
    inlines       = [ItemPecaInline, ItemMaoObraInline]
    readonly_fields = ['numero_os', 'data_entrada', 'data_criacao']


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display  = ['descricao', 'codigo', 'fornecedor', 'valor_unitario', 'estoque']
    search_fields = ['descricao', 'codigo', 'fornecedor']
