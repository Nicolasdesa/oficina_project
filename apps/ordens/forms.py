from django import forms
from django.forms import inlineformset_factory
from .models import OrdemServico, ItemPeca, ItemMaoObra, Cliente, Veiculo, Mecanico, Peca


class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = ['nome', 'cpf_cnpj', 'telefone', 'email', 'endereco']
        widgets = {
            'nome':     forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email':    forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VeiculoForm(forms.ModelForm):
    class Meta:
        model  = Veiculo
        fields = ['cliente', 'descricao', 'placa', 'chassi', 'ano', 'cor']
        widgets = {
            'cliente':   forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'placa':     forms.TextInput(attrs={'class': 'form-control'}),
            'chassi':    forms.TextInput(attrs={'class': 'form-control'}),
            'ano':       forms.NumberInput(attrs={'class': 'form-control'}),
            'cor':       forms.TextInput(attrs={'class': 'form-control'}),
        }


class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model  = OrdemServico
        fields = ['cliente', 'veiculo', 'descricao_servico', 'status', 'observacoes', 'data_saida']
        widgets = {
            'cliente':           forms.Select(attrs={'class': 'form-select', 'id': 'id_cliente'}),
            'veiculo':           forms.Select(attrs={'class': 'form-select', 'id': 'id_veiculo'}),
            'descricao_servico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status':            forms.Select(attrs={'class': 'form-select'}),
            'observacoes':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'data_saida':        forms.DateTimeInput(
                                     attrs={'class': 'form-control', 'type': 'datetime-local'},
                                     format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_saida'].required = False
        # Sempre aceita qualquer veículo — o AJAX filtra visualmente por cliente
        self.fields['veiculo'].queryset = Veiculo.objects.all()


class ItemPecaForm(forms.ModelForm):
    class Meta:
        model  = ItemPeca
        fields = ['peca', 'quantidade', 'valor_unitario']
        widgets = {
            'peca':           forms.Select(attrs={'class': 'form-select peca-select'}),
            'quantidade':     forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Força queryset explícito para evitar problema com PK customizado
        self.fields['peca'].queryset = Peca.objects.all().order_by('descricao')


class ItemMaoObraForm(forms.ModelForm):
    class Meta:
        model  = ItemMaoObra
        fields = ['mecanico', 'tipo_servico', 'horas_trabalhadas', 'valor_hora']
        widgets = {
            'mecanico':          forms.Select(attrs={'class': 'form-select mecanico-select'}),
            'tipo_servico':      forms.TextInput(attrs={'class': 'form-control'}),
            'horas_trabalhadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'valor_hora':        forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Força queryset explícito para mecânicos ativos
        self.fields['mecanico'].queryset = Mecanico.objects.filter(ativo=True).order_by('nome')


# Formsets inline
ItemPecaFormSet = inlineformset_factory(
    OrdemServico, ItemPeca,
    form=ItemPecaForm,
    extra=1, can_delete=True,
    fk_name='ordem',
)

ItemMaoObraFormSet = inlineformset_factory(
    OrdemServico, ItemMaoObra,
    form=ItemMaoObraForm,
    extra=1, can_delete=True,
    fk_name='ordem',
)
