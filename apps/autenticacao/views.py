from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils import timezone

from .models import Usuario
from .forms import LoginForm, UsuarioForm, AlterarSenhaForm


# ── Login / Logout ────────────────────────────────────────────────────────────

def view_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user, backend='apps.autenticacao.backends.SQLServerBackend')
            messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'autenticacao/login.html', {'form': form})


def view_logout(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# ── Gerenciamento de usuários (somente admin) ─────────────────────────────────

def _somente_admin(request):
    """Retorna True se o usuário tem perfil admin."""
    try:
        return Usuario.objects.get(pk=request.user.id, ativo=True).perfil == 'admin'
    except Usuario.DoesNotExist:
        return False


@login_required
def lista_usuarios(request):
    if not _somente_admin(request):
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard')

    usuarios = Usuario.objects.all()
    return render(request, 'autenticacao/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def novo_usuario(request):
    if not _somente_admin(request):
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            u = form.save()
            messages.success(request, f'Usuário "{u.username}" criado com sucesso!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()

    return render(request, 'autenticacao/form_usuario.html', {
        'form': form, 'titulo': 'Novo Usuário',
    })


@login_required
def editar_usuario(request, pk):
    if not _somente_admin(request):
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'autenticacao/form_usuario.html', {
        'form': form, 'titulo': f'Editar — {usuario.username}', 'usuario': usuario,
    })


@login_required
def excluir_usuario(request, pk):
    if not _somente_admin(request):
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.pk == request.user.id:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('lista_usuarios')

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário removido.')
        return redirect('lista_usuarios')

    return render(request, 'autenticacao/confirmar_exclusao.html', {'usuario': usuario})


# ── Alterar senha (o próprio usuário) ────────────────────────────────────────

@login_required
def alterar_senha(request):
    try:
        usuario = Usuario.objects.get(pk=request.user.id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AlterarSenhaForm(request.POST)
        if form.is_valid():
            if not check_password(form.cleaned_data['senha_atual'], usuario.senha_hash):
                form.add_error('senha_atual', 'Senha atual incorreta.')
            else:
                from django.contrib.auth.hashers import make_password
                usuario.senha_hash = make_password(form.cleaned_data['nova_senha'])
                usuario.save(update_fields=['senha_hash'])
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('dashboard')
    else:
        form = AlterarSenhaForm()

    return render(request, 'autenticacao/alterar_senha.html', {'form': form})
