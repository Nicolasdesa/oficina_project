# Oficina Pro — Sistema de Gestão de Oficina
**Django + Python + SQL Server + ReportLab**

---

## Pré-requisitos

- Python 3.10+
- SQL Server (local ou remoto) com o banco `OficinaBD` criado (use o script `oficina_sqlserver.sql`)
- ODBC Driver 17 for SQL Server instalado
  - Windows: https://aka.ms/downloadmsodbcsql
  - Linux: `sudo apt install unixodbc-dev && pip install pyodbc`

---

## Instalação passo a passo

### 1. Clonar / extrair o projeto
```bash
cd /caminho/do/projeto
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar o banco de dados
Edite `oficina_project/settings.py` e ajuste:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'OficinaBD',          # nome do banco
        'USER': 'sa',                  # usuário SQL
        'PASSWORD': 'SuaSenha123',     # senha SQL
        'HOST': 'localhost',           # servidor
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

> **Autenticação Windows** — se preferir, remova USER/PASSWORD e adicione:
> ```python
> 'OPTIONS': { 'driver': 'ODBC Driver 17 for SQL Server', 'trusted_connection': 'yes' }
> ```

### 5. Criar o superusuário do Django
```bash
python manage.py createsuperuser
```

### 6. Coletar arquivos estáticos (produção)
```bash
python manage.py collectstatic
```

### 7. Rodar o servidor
```bash
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

---

## Estrutura de URLs

| URL | Descrição |
|-----|-----------|
| `/` | Dashboard |
| `/login/` | Tela de login |
| `/ordens/` | Lista todas as OS |
| `/ordens/nova/` | Criar nova OS |
| `/ordens/<id>/` | Detalhe da OS |
| `/ordens/<id>/editar/` | Editar OS |
| `/ordens/<id>/pdf/` | **Gerar PDF da OS** |
| `/ordens/clientes/` | Lista de clientes |
| `/ordens/clientes/novo/` | Novo cliente |
| `/ordens/veiculos/novo/` | Novo veículo |
| `/admin/` | Painel administrativo Django |

---

## Geração de PDF

O PDF é gerado pela biblioteca **ReportLab** e contém:

- Cabeçalho com número da OS e status colorido
- Dados do cliente e do veículo
- Datas de entrada e saída
- Descrição do serviço
- Tabela de peças com subtotais
- Tabela de mão de obra com subtotais
- **Total Geral = Peças + Mão de Obra** em destaque laranja
- Campo de assinaturas (oficina + cliente)

Para **forçar download** em vez de abrir no navegador, edite `views.py`:
```python
# Trocar 'inline' por 'attachment'
response['Content-Disposition'] = f'attachment; filename="{filename}"'
```

---

## Observações importantes

- Os models usam `managed = False` — o Django **não cria nem altera** as tabelas no SQL Server.
  Toda a estrutura do banco deve ser criada pelo script SQL fornecido.
- Os campos `NumeroOS`, `Subtotal` são colunas computadas no SQL Server — somente leitura no Django.
- O campo `data_entrada` é preenchido automaticamente pelo banco (`DEFAULT GETDATE()`).

---

## Dependências principais

| Pacote | Versão | Uso |
|--------|--------|-----|
| Django | 4.2+ | Framework web |
| mssql-django | 1.3+ | Conector SQL Server |
| pyodbc | 4.0+ | Driver ODBC |
| reportlab | 4.0+ | Geração de PDF |
| django-crispy-forms | 2.0+ | Formulários Bootstrap |
| crispy-bootstrap5 | 0.7+ | Tema Bootstrap 5 |
