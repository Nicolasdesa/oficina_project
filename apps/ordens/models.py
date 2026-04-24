from django.db import models, connection


class Cliente(models.Model):
    cliente_id    = models.AutoField(primary_key=True, db_column='ClienteID')
    nome          = models.CharField('Nome', max_length=100, db_column='Nome')
    cpf_cnpj      = models.CharField('CPF / CNPJ', max_length=20, unique=True,
                                      blank=True, null=True, db_column='CPF_CNPJ')
    telefone      = models.CharField('Telefone', max_length=20, blank=True, db_column='Telefone')
    email         = models.EmailField('E-mail', blank=True, db_column='Email')
    endereco      = models.CharField('Endereco', max_length=200, blank=True, db_column='Endereco')
    data_cadastro = models.DateTimeField('Cadastrado em', auto_now_add=True, db_column='DataCadastro')

    class Meta:
        db_table = 'Clientes'
        managed  = False
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    veiculo_id = models.AutoField(primary_key=True, db_column='VeiculoID')
    cliente    = models.ForeignKey(Cliente, on_delete=models.CASCADE,
                                    db_column='ClienteID', related_name='veiculos')
    descricao  = models.CharField('Veiculo', max_length=100, db_column='Descricao')
    placa      = models.CharField('Placa', max_length=20, blank=True, db_column='Placa')
    chassi     = models.CharField('Chassi', max_length=50, blank=True, db_column='Chassi')
    ano        = models.IntegerField('Ano', null=True, blank=True, db_column='Ano')
    cor        = models.CharField('Cor', max_length=30, blank=True, db_column='Cor')

    class Meta:
        db_table = 'Veiculos'
        managed  = False
        ordering = ['descricao']

    def __str__(self):
        return f'{self.descricao} - {self.placa}'


class Mecanico(models.Model):
    mecanico_id   = models.AutoField(primary_key=True, db_column='MecanicoID')
    nome          = models.CharField('Nome', max_length=100, db_column='Nome')
    especialidade = models.CharField('Especialidade', max_length=100, blank=True, db_column='Especialidade')
    valor_hora    = models.DecimalField('Valor/Hora', max_digits=10, decimal_places=2,
                                         default=0, db_column='ValorHora')
    ativo         = models.BooleanField('Ativo', default=True, db_column='Ativo')

    class Meta:
        db_table = 'Mecanicos'
        managed  = False
        ordering = ['nome']

    def __str__(self):
        return self.nome


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('Em andamento',    'Em andamento'),
        ('Aguardando peca', 'Aguardando peca'),
        ('Concluido',       'Concluido'),
        ('Cancelado',       'Cancelado'),
    ]

    os_id             = models.AutoField(primary_key=True, db_column='OSID')
    # NumeroOS e coluna COMPUTADA (PERSISTED) — nunca inserir/atualizar
    numero_os         = models.CharField(max_length=20, blank=True, null=True,
                                          db_column='NumeroOS', editable=False)
    cliente           = models.ForeignKey(Cliente, on_delete=models.PROTECT,
                                           db_column='ClienteID', related_name='ordens')
    veiculo           = models.ForeignKey(Veiculo, on_delete=models.PROTECT,
                                           db_column='VeiculoID', related_name='ordens')
    data_entrada      = models.DateTimeField('Entrada', auto_now_add=True, db_column='DataEntrada')
    data_saida        = models.DateTimeField('Saida', null=True, blank=True, db_column='DataSaida')
    descricao_servico = models.TextField('Descricao', db_column='DescricaoServico')
    status            = models.CharField('Status', max_length=30, choices=STATUS_CHOICES,
                                          default='Em andamento', db_column='Status')
    observacoes       = models.TextField('Observacoes', blank=True, null=True, db_column='Observacoes')
    data_criacao      = models.DateTimeField('Criado em', auto_now_add=True, db_column='DataCriacao')

    class Meta:
        db_table = 'OrdensServico'
        managed  = False
        ordering = ['-data_entrada']

    def __str__(self):
        return f'OS-{self.os_id} - {self.cliente}'

    def save(self, *args, **kwargs):
        """
        Faz INSERT/UPDATE manual ignorando NumeroOS (coluna computada).
        """
        cliente_id = self.cliente_id
        veiculo_id = self.veiculo_id
        data_saida = self.data_saida
        desc       = self.descricao_servico
        status     = self.status
        obs        = self.observacoes or None

        with connection.cursor() as cursor:
            if self.os_id and not self._state.adding:
                # UPDATE
                cursor.execute("""
                    UPDATE OrdensServico SET
                        ClienteID         = %s,
                        VeiculoID         = %s,
                        DataSaida         = %s,
                        DescricaoServico  = %s,
                        Status            = %s,
                        Observacoes       = %s
                    WHERE OSID = %s
                """, [cliente_id, veiculo_id, data_saida, desc, status, obs, self.os_id])
            else:
                # INSERT — exclui NumeroOS e DataCriacao (têm DEFAULT)
                cursor.execute("""
                    INSERT INTO OrdensServico
                        (ClienteID, VeiculoID, DataSaida, DescricaoServico, Status, Observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [cliente_id, veiculo_id, data_saida, desc, status, obs])
                # Pega o ID gerado
                cursor.execute("SELECT SCOPE_IDENTITY()")
                self.os_id = int(cursor.fetchone()[0])
                self._state.adding = False

    @property
    def total_pecas(self):
        from decimal import Decimal
        return sum((i.subtotal for i in self.itens_peca.all()), Decimal('0'))

    @property
    def total_mao_obra(self):
        from decimal import Decimal
        return sum((i.subtotal for i in self.itens_mo.all()), Decimal('0'))

    @property
    def total_geral(self):
        return self.total_pecas + self.total_mao_obra


class Peca(models.Model):
    peca_id        = models.AutoField(primary_key=True, db_column='PecaID')
    descricao      = models.CharField('Descricao', max_length=150, db_column='Descricao')
    codigo         = models.CharField('Codigo', max_length=50, unique=True,
                                       blank=True, null=True, db_column='Codigo')
    fornecedor     = models.CharField('Fornecedor', max_length=100, blank=True, db_column='Fornecedor')
    valor_unitario = models.DecimalField('Valor Unit.', max_digits=10, decimal_places=2,
                                          default=0, db_column='ValorUnitario')
    estoque        = models.IntegerField('Estoque', default=0, db_column='Estoque')

    class Meta:
        db_table = 'Pecas'
        managed  = False
        ordering = ['descricao']
        verbose_name = 'Peca'
        verbose_name_plural = 'Pecas'

    def __str__(self):
        return self.descricao


class ItemPeca(models.Model):
    item_peca_id   = models.AutoField(primary_key=True, db_column='ItemPecaID')
    ordem          = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                        db_column='OSID', related_name='itens_peca')
    peca           = models.ForeignKey(Peca, on_delete=models.PROTECT, db_column='PecaID')
    quantidade     = models.IntegerField('Qtd', default=1, db_column='Quantidade')
    valor_unitario = models.DecimalField('Valor Unit.', max_digits=10, decimal_places=2,
                                          db_column='ValorUnitario')

    class Meta:
        db_table = 'ItensPeca'
        managed  = False

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario

    def save(self, *args, **kwargs):
        if not self.valor_unitario:
            self.valor_unitario = self.peca.valor_unitario
        super().save(*args, **kwargs)


class ItemMaoObra(models.Model):
    item_mo_id        = models.AutoField(primary_key=True, db_column='ItemMOID')
    ordem             = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                           db_column='OSID', related_name='itens_mo')
    mecanico          = models.ForeignKey(Mecanico, on_delete=models.PROTECT, db_column='MecanicoID')
    tipo_servico      = models.CharField('Tipo', max_length=150, db_column='TipoServico')
    horas_trabalhadas = models.DecimalField('Horas', max_digits=5, decimal_places=2,
                                             db_column='HorasTrabalhadas')
    valor_hora        = models.DecimalField('Valor/Hora', max_digits=10, decimal_places=2,
                                             db_column='ValorHora')

    class Meta:
        db_table = 'ItensMaoObra'
        managed  = False

    @property
    def subtotal(self):
        return self.horas_trabalhadas * self.valor_hora

    def save(self, *args, **kwargs):
        if not self.valor_hora:
            self.valor_hora = self.mecanico.valor_hora
        super().save(*args, **kwargs)
