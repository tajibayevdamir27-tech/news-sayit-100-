from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/', views.article_detail_slug, name='article_detail_slug'),
    path('article/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/article/create/', views.admin_article_create, name='admin_article_create'),
    path('admin-panel/article/<int:pk>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('admin-panel/article/<int:pk>/delete/', views.admin_article_delete, name='admin_article_delete'),
    path('admin-panel/user/<int:user_id>/staff/', views.admin_give_staff, name='admin_give_staff'),
    path('admin-panel/user/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)