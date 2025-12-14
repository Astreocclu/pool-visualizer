from django.db import models
from api.models import VisualizationRequest

class AuditReport(models.Model):
    """
    Stores the site assessment results for a pool visualization request.
    """
    request = models.OneToOneField(
        VisualizationRequest,
        on_delete=models.CASCADE,
        related_name='audit_report',
        help_text="Associated visualization request"
    )

    # Site Assessment Flags (Boolean for easy querying)
    has_tree_clearance_needed = models.BooleanField(default=False, help_text="Large trees in pool zone")
    has_structure_relocation_needed = models.BooleanField(default=False, help_text="Structures to move/remove")
    has_grading_needed = models.BooleanField(default=False, help_text="Slope or terrain issues")
    has_access_considerations = models.BooleanField(default=False, help_text="Equipment access challenges")

    # Legacy fields - keep for migration compatibility
    has_ground_level_access = models.BooleanField(default=False, help_text="DEPRECATED - use has_tree_clearance_needed")
    has_concealment = models.BooleanField(default=False, help_text="DEPRECATED - use has_structure_relocation_needed")
    has_glass_proximity = models.BooleanField(default=False, help_text="DEPRECATED - use has_grading_needed")
    has_hardware_weakness = models.BooleanField(default=False, help_text="DEPRECATED - use has_access_considerations")

    # Detailed Analysis (JSON) - renamed from vulnerabilities
    site_items = models.JSONField(
        default=list,
        help_text="List of site items identified with descriptions and actions"
    )
    vulnerabilities = models.JSONField(
        default=list,
        help_text="DEPRECATED - use site_items"
    )

    # AI Reasoning - renamed for clarity
    assessment_summary = models.TextField(default="", help_text="AI generated summary of site readiness")
    analysis_summary = models.TextField(default="", help_text="DEPRECATED - use assessment_summary")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Site Assessment for Request {self.request.id}"
