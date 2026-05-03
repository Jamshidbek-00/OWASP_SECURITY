from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('add-note/', views.add_note, name='add_note'),
    path('toggle-security/', views.toggle_security, name='toggle_security'),
    path('security-test/', views.security_test_page, name='security_test_page'),
    path('register/', views.register_view, name='register'),
]