"""
Comando: python manage.py criar_admin
Cria (ou atualiza) o usuário admin na tabela Usuarios do SQL Server
com a senha devidamente hasheada pelo PBKDF2-SHA256 do Django.
"""
import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.autenticacao.models import Usuario


class Command(BaseCommand):
    help = 'Cria o primeiro usuário administrador na tabela Usuarios do SQL Server'

    def add_arguments(self, parser):
        parser.add_argument('--username',  default=None)
        parser.add_argument('--nome',      default=None)
        parser.add_argument('--email',     default=None)
        parser.add_argument('--senha',     default=None)

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Criar usuário admin ===\n'))

        username = options['username'] or input('Username [admin]: ').strip() or 'admin'
        nome     = options['nome']     or input('Nome completo: ').strip() or 'Administrador'
        email    = options['email']    or input('E-mail (opcional): ').strip() or None

        senha = options['senha']
        if not senha:
            while True:
                senha = getpass.getpass('Senha (mín. 6 caracteres): ')
                if len(senha) < 6:
                    self.stderr.write('Senha muito curta. Tente novamente.')
                    continue
                conf = getpass.getpass('Confirme a senha: ')
                if senha != conf:
                    self.stderr.write('As senhas não conferem. Tente novamente.')
                    continue
                break

        senha_hash = make_password(senha)

        usuario, criado = Usuario.objects.update_or_create(
            username=username,
            defaults={
                'nome_completo': nome,
                'email':         email,
                'senha_hash':    senha_hash,
                'perfil':        'admin',
                'ativo':         True,
            }
        )

        if criado:
            self.stdout.write(self.style.SUCCESS(f'\n✔ Usuário "{username}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✔ Usuário "{username}" atualizado com sucesso!'))

        self.stdout.write(f'  Perfil : admin')
        self.stdout.write(f'  Acesse : http://127.0.0.1:8000/login/\n')
