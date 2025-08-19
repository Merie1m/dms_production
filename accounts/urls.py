from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.ajouter_utilisateur, name='register'),
    path('logout/', views.logout_view, name='logout'), 
]