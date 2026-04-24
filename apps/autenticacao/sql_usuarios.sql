-- ============================================================
--  TABELA DE LOGIN — SQL SERVER
--  Execute no banco OficinaBD
-- ============================================================

USE OficinaBD;
GO

IF OBJECT_ID('Usuarios', 'U') IS NOT NULL DROP TABLE Usuarios;
GO

CREATE TABLE Usuarios (
    UsuarioID    INT            IDENTITY(1,1) PRIMARY KEY,
    Username     NVARCHAR(50)   NOT NULL UNIQUE,
    NomeCompleto NVARCHAR(150)  NOT NULL,
    Email        NVARCHAR(150)  NULL UNIQUE,
    SenhaHash    NVARCHAR(256)  NOT NULL,   -- hash PBKDF2 gerado pelo Python
    Perfil       NVARCHAR(20)   NOT NULL DEFAULT 'operador'
                                CHECK (Perfil IN ('admin', 'gerente', 'operador')),
    Ativo        BIT            NOT NULL DEFAULT 1,
    UltimoLogin  DATETIME2      NULL,
    DataCriacao  DATETIME2      NOT NULL DEFAULT GETDATE()
);
GO

CREATE UNIQUE INDEX IX_Usuarios_Username ON Usuarios(Username);
GO

PRINT 'Tabela Usuarios criada!';
PRINT 'Rode: python manage.py criar_admin  para cadastrar o primeiro usuario.';
GO
