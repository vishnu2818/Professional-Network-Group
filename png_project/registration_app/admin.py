from django.contrib import admin
from .models import *

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by')  # Columns displayed in the admin list view
    list_filter = ('status',)  # Add a filter sidebar for 'status'
    search_fields = ('name', 'created_by__username')  # Add a search bar for 'name' and 'created_by'
    ordering = ('status', 'name')  # Default ordering in the admin list view

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'description')  # Columns displayed in the admin list view
    list_filter = ('date',)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'publication_date', 'author')  # Columns displayed in the admin list view
    list_filter = ('publication_date',)

admin.site.register(Company, CompanyAdmin)

admin.site.register(Event, EventAdmin)

admin.site.register(NewsUpload, NewsAdmin) # Working