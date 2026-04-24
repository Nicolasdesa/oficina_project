"""
backends.py
Backend de autenticação customizado que valida login
diretamente na tabela Usuarios do SQL Server.
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
user_logged_in.disconnect(update_last_login)

from .models import Usuario
from .forms import LoginForm, UsuarioForm, AlterarSenhaForm

class SQLServerBackend(BaseBackend):
    """
    Autentica contra a tabela Usuarios do SQL Server.
    Retorna um objeto User do Django (sem salvar no banco Django)
    para que o sistema de sessões funcione normalmente.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            usuario = Usuario.objects.get(username__iexact=username, ativo=True)
        except Usuario.DoesNotExist:
            # Executa o check mesmo sem encontrar (evita timing attack)
            check_password(password, 'pbkdf2_sha256$600000$dummy$dummy')
            return None

        if not check_password(password, usuario.senha_hash):
            return None

        # Atualiza último login
        usuario.ultimo_login = timezone.now()
        usuario.save(update_fields=['ultimo_login'])

        # Retorna um User Django virtual (id = UsuarioID do SQL Server)
        return self._get_or_build_django_user(usuario)

    def get_user(self, user_id):
        try:
            usuario = Usuario.objects.get(pk=user_id, ativo=True)
            return self._get_or_build_django_user(usuario)
        except Usuario.DoesNotExist:
            return None

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_or_build_django_user(self, usuario):
        """
        Constrói um objeto User do Django em memória a partir do registro
        da tabela Usuarios. Não persiste nada no banco do Django.
        """
        user = DjangoUser(
            id         = usuario.pk,
            username   = usuario.username,
            email      = usuario.email or '',
            is_active  = usuario.ativo,
            is_staff   = usuario.perfil in ('admin', 'gerente'),
            is_superuser = usuario.perfil == 'admin',
        )
        # Preenche first/last name a partir de NomeCompleto
        partes = usuario.nome_completo.split(' ', 1)
        user.first_name = partes[0]
        user.last_name  = partes[1] if len(partes) > 1 else ''

        # Evita que o Django tente fazer queries na tabela auth_user
        user.backend = f'{self.__class__.__module__}.{self.__class__.__name__}'
        return user
