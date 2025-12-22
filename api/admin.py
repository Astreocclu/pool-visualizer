from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, VisualizationRequest, GeneratedImage, ReferenceImage

# Basic registration
admin.site.register(UserProfile)
admin.site.register(VisualizationRequest)
admin.site.register(GeneratedImage)


@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    """Admin interface for managing reference images."""

    list_display = (
        'tenant_id',
        'category',
        'option_value',
        'thumbnail_preview',
        'description',
        'uploaded_at',
    )
    list_filter = ('tenant_id', 'category')
    search_fields = ('option_value', 'description')
    readonly_fields = ('thumbnail_preview', 'uploaded_at')

    fieldsets = (
        ('Reference Details', {
            'fields': ('tenant_id', 'category', 'option_value')
        }),
        ('Image', {
            'fields': ('image', 'thumbnail', 'thumbnail_preview')
        }),
        ('Metadata', {
            'fields': ('description', 'uploaded_by', 'uploaded_at')
        }),
    )

    def thumbnail_preview(self, obj):
        """Display thumbnail in admin list and detail views."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain;" />',
                obj.thumbnail.url
            )
        elif obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain;" />',
                obj.image.url
            )
        return "-"

    thumbnail_preview.short_description = "Preview"
