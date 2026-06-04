from django.contrib import admin
from django.utils.html import format_html
from .models import Article
import random


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    

    list_display = ('title', 'category', 'created_at', 'views', 'like_count', 'status_badge')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('views', 'created_at', 'like_count')
    ordering = ('-created_at',)
    

    fieldsets = (
        ('Maqala ma\'glumat / Article Info', {
            'fields': ('title','slug', 'content', 'image')
        }),
        ('Kategoriya / Category', {
            'fields': ('category',)
        }),
        ('Statistika / Statistics', {
            'fields': ('views', 'created_at', 'like_count'),
            'classes': ('collapse',)
        }),
    )
    

    def has_add_permission(self, request):

        return request.user.has_perm('main.add_article')
    
    def has_change_permission(self, request, obj=None):

        return request.user.has_perm('main.change_article')
    
    def has_delete_permission(self, request, obj=None):

        return request.user.has_perm('main.delete_article')
    
    def has_view_permission(self, request, obj=None):

        return request.user.has_perm('main.view_article')
    

    def status_badge(self, obj):

        if obj.views > 100:
            color = '#28a745'  
            status = ' Populyar'
        elif obj.views > 50:
            color = '#ffc107'  
            status = ' O\'rtacha'
        else:
            color = '#6c757d'  
            status = '⏱️ Jana'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 20px;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Jagdayi / Status'
    

    def get_ordering(self, request):
        if request.GET.get('shuffle') == '1':
            return ['?']
        
        return ['-created_at']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['shuffle_url'] = '?shuffle=1'
        return super().changelist_view(request, extra_context)