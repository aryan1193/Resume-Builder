from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import *
from .utils import render_to_pdf
import json
import re

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

# Main Views
def home(request):
    """Landing page with featured resumes and app overview"""
    featured_resumes = Resume.objects.filter(is_public=True).order_by('-views_count')[:6]
    context = {
        'featured_resumes': featured_resumes,
        'total_resumes': Resume.objects.count(),
        'total_users': User.objects.count(),
    }
    return render(request, 'home.html', context)

@login_required
def dashboard(request):
    """User dashboard showing their resumes"""
    user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    context = {
        'resumes': user_resumes,
        'total_resumes': user_resumes.count(),
    }
    return render(request, 'dashboard.html', context)

def create_resume(request):
    """Create a new resume"""
    if request.method == 'POST':
        # Server-side validation
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Name validation
        import re
        name_pattern = re.compile(r'^[A-Za-z\s]{3,}$')
        if not name_pattern.match(name):
            messages.error(request, 'Name must be at least 3 letters long and contain only letters and spaces.')
            return render(request, 'create_resume.html')
        
        # Email validation
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'create_resume.html')
        
        # Create new resume
        resume = Resume.objects.create(
            user=request.user if request.user.is_authenticated else None,
            title=request.POST.get('title', 'My Resume'),
            template=request.POST.get('template', 'modern'),
            name=request.POST.get('name', ''),
            about=request.POST.get('about', ''),
            age=request.POST.get('age', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            linkedin=request.POST.get('linkedin', ''),
            github=request.POST.get('github', ''),
            portfolio=request.POST.get('portfolio', ''),
            twitter=request.POST.get('twitter', ''),
        )
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            resume.profile_picture = request.FILES['profile_picture']
            resume.save()
        
        # Add skills
        skills = request.POST.getlist('skills[]')
        skill_proficiencies = request.POST.getlist('skill_proficiencies[]')
        
        for i in range(len(skills)):
            if skills[i].strip():
                Skill.objects.create(
                    resume=resume,
                    name=skills[i].strip(),
                    proficiency=skill_proficiencies[i] if i < len(skill_proficiencies) else 'intermediate'
                )
        
        # Add education
        degrees = request.POST.getlist('degrees[]')
        institutions = request.POST.getlist('institutions[]')
        years = request.POST.getlist('years[]')
        gpas = request.POST.getlist('gpas[]')
        
        for i in range(len(degrees)):
            if degrees[i].strip():
                Education.objects.create(
                    resume=resume,
                    degree=degrees[i].strip(),
                    institution=institutions[i].strip() if i < len(institutions) else '',
                    year=years[i].strip() if i < len(years) else '',
                    gpa=gpas[i].strip() if i < len(gpas) else '',
                )
        
        # Add languages
        languages = request.POST.getlist('languages[]')
        proficiencies = request.POST.getlist('proficiencies[]')
        
        for i in range(len(languages)):
            if languages[i].strip():
                Language.objects.create(
                    resume=resume,
                    name=languages[i].strip(),
                    proficiency=proficiencies[i] if i < len(proficiencies) else 'intermediate'
                )
        
        # Add projects
        project_titles = request.POST.getlist('project_titles[]')
        project_durations = request.POST.getlist('project_durations[]')
        project_descriptions = request.POST.getlist('project_descriptions[]')
        project_technologies = request.POST.getlist('project_technologies[]')
        
        for i in range(len(project_titles)):
            if project_titles[i].strip():
                Project.objects.create(
                    resume=resume,
                    title=project_titles[i].strip(),
                    duration=project_durations[i].strip() if i < len(project_durations) else '',
                    description=project_descriptions[i].strip() if i < len(project_descriptions) else '',
                    technologies=project_technologies[i].strip() if i < len(project_technologies) else '',
                )
        
        # Add work experience
        companies = request.POST.getlist('companies[]')
        positions = request.POST.getlist('positions[]')
        work_durations = request.POST.getlist('work_durations[]')
        work_locations = request.POST.getlist('work_locations[]')
        work_descriptions = request.POST.getlist('work_descriptions[]')
        
        for i in range(len(companies)):
            if companies[i].strip():
                WorkExperience.objects.create(
                    resume=resume,
                    company=companies[i].strip(),
                    position=positions[i].strip() if i < len(positions) else '',
                    duration=work_durations[i].strip() if i < len(work_durations) else '',
                    description=work_descriptions[i].strip() if i < len(work_descriptions) else '',
                )
        
        # Add certifications
        cert_names = request.POST.getlist('cert_names[]')
        cert_issuers = request.POST.getlist('cert_issuers[]')
        cert_dates = request.POST.getlist('cert_dates[]')
        cert_expiry_dates = request.POST.getlist('cert_expiry_dates[]')
        cert_ids = request.POST.getlist('cert_ids[]')
        cert_urls = request.POST.getlist('cert_urls[]')
        
        for i in range(len(cert_names)):
            if cert_names[i].strip():
                try:
                    date_obtained = timezone.datetime.strptime(cert_dates[i], '%Y-%m-%d').date() if cert_dates[i] else timezone.now().date()
                    expiry_date = timezone.datetime.strptime(cert_expiry_dates[i], '%Y-%m-%d').date() if cert_expiry_dates[i] else None
                    
                    Certification.objects.create(
                        resume=resume,
                        name=cert_names[i].strip(),
                        issuer=cert_issuers[i].strip() if i < len(cert_issuers) else '',
                        date_obtained=date_obtained,
                        expiry_date=expiry_date,
                        credential_id=cert_ids[i].strip() if i < len(cert_ids) else '',
                        credential_url=cert_urls[i].strip() if i < len(cert_urls) else '',
                    )
                except:
                    pass
        
        # Add achievements
        achievement_titles = request.POST.getlist('achievement_titles[]')
        achievement_descriptions = request.POST.getlist('achievement_descriptions[]')
        achievement_years = request.POST.getlist('achievement_years[]')
        
        for i in range(len(achievement_titles)):
            if achievement_titles[i].strip():
                Achievement.objects.create(
                    resume=resume,
                    title=achievement_titles[i].strip(),
                    description=achievement_descriptions[i].strip() if i < len(achievement_descriptions) else '',
                    date=None,  # We'll use year instead of date for simplicity
                )
        
        # Add references
        ref_names = request.POST.getlist('ref_names[]')
        ref_positions = request.POST.getlist('ref_positions[]')
        ref_companies = request.POST.getlist('ref_companies[]')
        ref_emails = request.POST.getlist('ref_emails[]')
        ref_phones = request.POST.getlist('ref_phones[]')
        ref_relationships = request.POST.getlist('ref_relationships[]')
        
        for i in range(len(ref_names)):
            if ref_names[i].strip():
                Reference.objects.create(
                    resume=resume,
                    name=ref_names[i].strip(),
                    position=ref_positions[i].strip() if i < len(ref_positions) else '',
                    company=ref_companies[i].strip() if i < len(ref_companies) else '',
                    email=ref_emails[i].strip() if i < len(ref_emails) else '',
                    phone=ref_phones[i].strip() if i < len(ref_phones) else '',
                    relationship=ref_relationships[i].strip() if i < len(ref_relationships) else '',
                )
        
        messages.success(request, 'Resume created successfully!')
        return redirect('view_resume', resume_id=resume.id)
    
    return render(request, 'create_resume.html')

def view_resume(request, resume_id):
    """View a specific resume"""
    resume = get_object_or_404(Resume, id=resume_id)
    
    # Increment view count
    resume.views_count += 1
    resume.save()
    
    context = {
        'resume': resume,
        'skills': resume.skills.all(),
        'education': resume.education.all(),
        'languages': resume.languages.all(),
        'projects': resume.projects.all(),
        'work_experience': resume.work_experience.all(),
        'certifications': resume.certifications.all(),
        'achievements': resume.achievements.all(),
        'references': resume.references.all(),
    }
    
    template_name = f'resume_templates/{resume.template}.html'
    return render(request, template_name, context)

@login_required
def edit_resume(request, resume_id):
    """Edit an existing resume"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Update resume basic info
        resume.title = request.POST.get('title', resume.title)
        resume.template = request.POST.get('template', resume.template)
        resume.name = request.POST.get('name', resume.name)
        resume.about = request.POST.get('about', resume.about)
        resume.age = request.POST.get('age', resume.age)
        resume.email = request.POST.get('email', resume.email)
        resume.phone = request.POST.get('phone', resume.phone)
        resume.address = request.POST.get('address', resume.address)
        resume.linkedin = request.POST.get('linkedin', resume.linkedin)
        resume.github = request.POST.get('github', resume.github)
        resume.portfolio = request.POST.get('portfolio', resume.portfolio)
        resume.twitter = request.POST.get('twitter', resume.twitter)
        
        if 'profile_picture' in request.FILES:
            resume.profile_picture = request.FILES['profile_picture']
        
        resume.save()
        
        # Handle related data updates (simplified for brevity)
        # In a full implementation, you'd handle each section separately
        
        messages.success(request, 'Resume updated successfully!')
        return redirect('view_resume', resume_id=resume.id)
    
    context = {
        'resume': resume,
        'skills': resume.skills.all(),
        'education': resume.education.all(),
        'languages': resume.languages.all(),
        'projects': resume.projects.all(),
        'work_experience': resume.work_experience.all(),
        'certifications': resume.certifications.all(),
        'achievements': resume.achievements.all(),
        'references': resume.references.all(),
    }
    
    return render(request, 'edit_resume.html', context)

@login_required
def delete_resume(request, resume_id):
    """Delete a resume"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()
    messages.success(request, 'Resume deleted successfully!')
    return redirect('dashboard')

def download_pdf(request, resume_id):
    """Download resume as PDF"""
    resume = get_object_or_404(Resume, id=resume_id)
    
    # Increment download count
    resume.downloads_count += 1
    resume.save()
    
    context = {
        'resume': resume,
        'skills': resume.skills.all(),
        'education': resume.education.all(),
        'languages': resume.languages.all(),
        'projects': resume.projects.all(),
        'work_experience': resume.work_experience.all(),
        'certifications': resume.certifications.all(),
        'achievements': resume.achievements.all(),
        'references': resume.references.all(),
    }
    
    template_name = f'resume_templates/{resume.template}.html'
    return render_to_pdf(template_name, context)

def search_resumes(request):
    """Search public resumes"""
    query = request.GET.get('q', '')
    resumes = Resume.objects.filter(is_public=True)
    
    if query:
        resumes = resumes.filter(
            Q(name__icontains=query) |
            Q(title__icontains=query) |
            Q(about__icontains=query) |
            Q(skills__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(resumes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'resumes': page_obj,
        'query': query,
    }
    return render(request, 'search_resumes.html', context)

# API Views for AJAX functionality
def add_skill_ajax(request):
    """Add skill via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        resume_id = request.POST.get('resume_id')
        skill_name = request.POST.get('skill_name')
        proficiency = request.POST.get('proficiency', 80)
        
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
            skill = Skill.objects.create(
                resume=resume,
                name=skill_name,
                proficiency=proficiency
            )
            return JsonResponse({
                'success': True,
                'skill': {
                    'id': skill.id,
                    'name': skill.name,
                    'proficiency': skill.proficiency
                }
            })
        except:
            return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def remove_skill_ajax(request):
    """Remove skill via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        skill_id = request.POST.get('skill_id')
        
        try:
            skill = Skill.objects.get(id=skill_id, resume__user=request.user)
            skill.delete()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Legacy view for backward compatibility
def gen_resume(request):
    """Legacy resume generation view"""
    if request.method == 'POST':
        context = {
            'name': request.POST.get('name', ''),
            'about': request.POST.get('about', ''),
            'age': request.POST.get('age', ''),
            'email': request.POST.get('email', ''),
            'phone': request.POST.get('phone', ''),
            'skill1': request.POST.get('skill1', ''),
            'skill2': request.POST.get('skill2', ''),
            'skill3': request.POST.get('skill3', ''),
            'skill4': request.POST.get('skill4', ''),
            'skill5': request.POST.get('skill5', ''),
            'degree1': request.POST.get('degree1', ''),
            'college1': request.POST.get('college1', ''),
            'year1': request.POST.get('year1', ''),
            'degree2': request.POST.get('degree2', ''),
            'college2': request.POST.get('college2', ''),
            'year2': request.POST.get('year2', ''),
            'degree3': request.POST.get('degree3', ''),
            'college3': request.POST.get('college3', ''),
            'year3': request.POST.get('year3', ''),
            'lang1': request.POST.get('lang1', ''),
            'lang2': request.POST.get('lang2', ''),
            'lang3': request.POST.get('lang3', ''),
            'project1': request.POST.get('project1', ''),
            'durat1': request.POST.get('duration1', ''),
            'desc1': request.POST.get('desc1', ''),
            'project2': request.POST.get('project2', ''),
            'durat2': request.POST.get('duration2', ''),
            'desc2': request.POST.get('desc2', ''),
            'company1': request.POST.get('company1', ''),
            'post1': request.POST.get('post1', ''),
            'duration1': request.POST.get('duration1', ''),
            'lin11': request.POST.get('lin11', ''),
            'company2': request.POST.get('company2', ''),
            'post2': request.POST.get('post2', ''),
            'duration2': request.POST.get('duration2', ''),
            'lin21': request.POST.get('lin21', ''),
            'ach1': request.POST.get('ach1', ''),
            'ach2': request.POST.get('ach2', ''),
            'ach3': request.POST.get('ach3', '')
        }
        return render(request, 'resume.html', context)
    return render(request, 'index.html')
