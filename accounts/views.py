from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm
from .models import CustomUser

def is_admin(user):
    return user.role == CustomUser.Role.ADMIN


def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # adapter selon ton URL
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')  # Redirige vers le dashboard si déjà connecté
#     
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             email = form.cleaned_data.get('email')
#             messages.success(request, f'Compte créé avec succès pour {email}!')
#             # Connexion automatique après inscription
#             login(request, user)
#             return redirect('dashboard')
#         else:
#             messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
#     else:
#         form = CustomUserCreationForm()
#     
#     return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        messages.success(self.request, f'Bienvenue {email}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Email ou mot de passe incorrect.')
        return super().form_invalid(form)



def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')