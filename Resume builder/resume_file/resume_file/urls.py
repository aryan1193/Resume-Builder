"""
URL configuration for resume_file project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from home.views import *
from home.views import download_pdf

urlpatterns = [
    # Authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Main pages
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('search/', search_resumes, name='search_resumes'),
    
    # Resume management
    path('create/', create_resume, name='create_resume'),
    path('resume/<int:resume_id>/', view_resume, name='view_resume'),
    path('resume/<int:resume_id>/edit/', edit_resume, name='edit_resume'),
    path('resume/<int:resume_id>/delete/', delete_resume, name='delete_resume'),
    path('resume/<int:resume_id>/download/', download_pdf, name='download_pdf'),
    
    # API endpoints
    path('api/add-skill/', add_skill_ajax, name='add_skill_ajax'),
    path('api/remove-skill/', remove_skill_ajax, name='remove_skill_ajax'),
    
    # Legacy routes (for backward compatibility)
    path('resume/', gen_resume, name='resume'),
    path('download_pdf/', download_pdf, name='download_pdf'),
    
    # Admin
    path('admin/', admin.site.urls),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)