"""
Comando: python manage.py setup_auth
Cria a tabela Usuarios no SQL Server (se não existir) e cadastra o primeiro admin.
"""
import getpass
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Cria a tabela Usuarios no SQL Server e cadastra o primeiro admin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Setup de Autenticacao ===\n'))

        # ── 1. Cria a tabela se não existir ──────────────────────────────────
        self.stdout.write('Verificando tabela Usuarios...')
        with connection.cursor() as cursor:
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = 'Usuarios'
                )
                BEGIN
                    CREATE TABLE Usuarios (
                        UsuarioID    INT            IDENTITY(1,1) PRIMARY KEY,
                        Username     NVARCHAR(50)   NOT NULL,
                        NomeCompleto NVARCHAR(150)  NOT NULL,
                        Email        NVARCHAR(150)  NULL,
                        SenhaHash    NVARCHAR(256)  NOT NULL,
                        Perfil       NVARCHAR(20)   NOT NULL DEFAULT 'operador',
                        Ativo        BIT            NOT NULL DEFAULT 1,
                        UltimoLogin  DATETIME2      NULL,
                        DataCriacao  DATETIME2      NOT NULL DEFAULT GETDATE(),
                        CONSTRAINT UQ_Usuarios_Username UNIQUE (Username),
                        CONSTRAINT UQ_Usuarios_Email    UNIQUE (Email),
                        CONSTRAINT CK_Usuarios_Perfil   CHECK (Perfil IN ('admin','gerente','operador'))
                    )
                    PRINT 'Tabela Usuarios criada.'
                END
            """)

        self.stdout.write(self.style.SUCCESS('  Tabela Usuarios: OK'))

        # ── 2. Verifica se já existe algum admin ─────────────────────────────
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Perfil = 'admin'")
            total_admins = cursor.fetchone()[0]

        if total_admins > 0:
            self.stdout.write(self.style.WARNING(
                f'  Ja existe(m) {total_admins} admin(s). Pulando criacao.\n'
                '  Para adicionar outro usuario, use: python manage.py criar_admin\n'
            ))
            return

        # ── 3. Coleta dados do primeiro admin ────────────────────────────────
        self.stdout.write('\nNenhum admin encontrado. Vamos criar o primeiro:\n')

        username = input('  Username [admin]: ').strip() or 'admin'
        nome     = input('  Nome completo [Administrador]: ').strip() or 'Administrador'
        email    = input('  E-mail (opcional): ').strip() or None

        while True:
            senha = getpass.getpass('  Senha (min. 6 caracteres): ')
            if len(senha) < 6:
                self.stderr.write('  Senha muito curta. Tente novamente.')
                continue
            conf = getpass.getpass('  Confirme a senha: ')
            if senha != conf:
                self.stderr.write('  As senhas nao conferem. Tente novamente.')
                continue
            break

        senha_hash = make_password(senha)

        # ── 4. Insere o admin ────────────────────────────────────────────────
        with connection.cursor() as cursor:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE Username = %s)
                BEGIN
                    INSERT INTO Usuarios (Username, NomeCompleto, Email, SenhaHash, Perfil, Ativo)
                    VALUES (%s, %s, %s, %s, 'admin', 1)
                END
            """, [username, username, nome, email, senha_hash])

        self.stdout.write(self.style.SUCCESS(f'\n  Usuario "{username}" criado com sucesso!'))
        self.stdout.write(f'  Perfil : admin')
        self.stdout.write(f'  Acesse : http://127.0.0.1:8000/login/\n')
