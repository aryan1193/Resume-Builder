from django.contrib import admin
from .models import *

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'user', 'template', 'created_at', 'updated_at', 'is_public', 'views_count', 'downloads_count')
    list_filter = ('template', 'is_public', 'created_at', 'updated_at')
    search_fields = ('name', 'title', 'about', 'email')
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at')
    list_editable = ('is_public',)
    date_hierarchy = 'created_at'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'resume', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('name', 'resume__name')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'year', 'resume')
    list_filter = ('year',)
    search_fields = ('degree', 'institution', 'resume__name')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'proficiency', 'resume')
    list_filter = ('proficiency',)
    search_fields = ('name', 'resume__name')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'resume')
    search_fields = ('title', 'description', 'resume__name')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'duration', 'current', 'resume')
    list_filter = ('current',)
    search_fields = ('position', 'company', 'resume__name')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'date_obtained', 'expiry_date', 'resume')
    list_filter = ('date_obtained', 'expiry_date')
    search_fields = ('name', 'issuer', 'resume__name')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'resume')
    list_filter = ('date',)
    search_fields = ('title', 'description', 'resume__name')

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'company', 'resume')
    search_fields = ('name', 'position', 'company', 'resume__name')
