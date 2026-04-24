from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.usuario',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
        }),
    )


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Deixe em branco para não alterar'}),
        help_text='Mínimo 6 caracteres. Deixe em branco para manter a senha atual.',
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model  = Usuario
        fields = ['username', 'nome_completo', 'email', 'perfil', 'ativo']
        widgets = {
            'username':      forms.TextInput(attrs={'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'perfil':        forms.Select(attrs={'class': 'form-select'}),
            'ativo':         forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        senha   = cleaned.get('senha')
        conf    = cleaned.get('confirmar_senha')

        if senha:
            if len(senha) < 6:
                self.add_error('senha', 'A senha deve ter pelo menos 6 caracteres.')
            if senha != conf:
                self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha   = self.cleaned_data.get('senha')
        if senha:
            usuario.senha_hash = make_password(senha)
        elif not usuario.pk:
            raise forms.ValidationError('Informe uma senha para o novo usuário.')
        if commit:
            usuario.save()
        return usuario


class AlterarSenhaForm(forms.Form):
    senha_atual = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    nova_senha = forms.CharField(
        label='Nova senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    confirmar = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('nova_senha') != cleaned.get('confirmar'):
            self.add_error('confirmar', 'As senhas não conferem.')
        return cleaned
