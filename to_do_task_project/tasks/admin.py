from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import CustomUserInfoModel, TaskModel


@admin.register(CustomUserInfoModel)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'full_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name',)}),
    )


@admin.register(TaskModel)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
