from django.db import models


class Usuario(models.Model):
    PERFIL_CHOICES = [
        ('admin',    'Administrador'),
        ('gerente',  'Gerente'),
        ('operador', 'Operador'),
    ]

    usuario_id    = models.AutoField(primary_key=True, db_column='UsuarioID')
    username      = models.CharField('Usuario', max_length=50, unique=True,
                                      db_column='Username')
    nome_completo = models.CharField('Nome completo', max_length=150,
                                      db_column='NomeCompleto')
    email         = models.EmailField('E-mail', null=True, blank=True,
                                       db_column='Email')
    senha_hash    = models.CharField('Senha (hash)', max_length=256,
                                      db_column='SenhaHash')
    perfil        = models.CharField('Perfil', max_length=20,
                                      choices=PERFIL_CHOICES, default='operador',
                                      db_column='Perfil')
    ativo         = models.BooleanField('Ativo', default=True,
                                         db_column='Ativo')
    ultimo_login  = models.DateTimeField('Ultimo login', null=True, blank=True,
                                          db_column='UltimoLogin')
    data_criacao  = models.DateTimeField('Criado em', auto_now_add=True,
                                          db_column='DataCriacao')

    class Meta:
        db_table = 'Usuarios'
        managed  = False
        ordering = ['username']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} ({self.get_perfil_display()})'
