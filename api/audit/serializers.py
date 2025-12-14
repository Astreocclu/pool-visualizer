from rest_framework import serializers
from .models import AuditReport

class AuditReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditReport
        fields = [
            'id',
            'request',
            # New pool site assessment fields
            'has_tree_clearance_needed',
            'has_structure_relocation_needed',
            'has_grading_needed',
            'has_access_considerations',
            'site_items',
            'assessment_summary',
            # Legacy fields for backwards compatibility
            'has_ground_level_access',
            'has_concealment',
            'has_glass_proximity',
            'has_hardware_weakness',
            'vulnerabilities',
            'analysis_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
