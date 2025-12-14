# Pool Site Assessment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert the security audit feature into a pool site assessment that analyzes backyards for pool installation readiness (trees to remove, structures to relocate, grading needs, equipment access).

**Architecture:** Reuse existing audit infrastructure (services, views, models) with pool-specific prompt and field names. Keep positive framing style matching the pool visualization prompts. Frontend updated with pool-themed colors and icons.

**Tech Stack:** Django, Gemini AI, React, Lucide icons

---

## Task 1: Update Audit Prompt for Pool Site Assessment

**Files:**
- Modify: `api/audit/prompts.py`

**Step 1: Replace the security audit prompt with pool site assessment**

```python
def get_audit_prompt():
    """
    Returns the prompt for Pool Site Assessment analysis.
    Analyzes backyard for pool installation readiness.
    """
    return """You are a Pool Installation Site Assessor. Analyze this backyard image to help homeowners understand what preparation work may be needed before pool construction.

ASSESS THESE SITE CONDITIONS:

1. Tree Clearance: Are there large trees (trunk wider than 6 inches) in the likely pool installation area that would need removal?

2. Structure Relocation: Are there existing structures (sheds, play equipment, gazebos, fencing sections) in the pool zone that would need to be moved or removed?

3. Grading Considerations: Is there visible slope or uneven terrain that may require grading or leveling work?

4. Equipment Access: Are there potential challenges for construction equipment access (narrow gates, tight pathways, obstacles)?

ANALYSIS STYLE:
- Be helpful and informative, not alarming
- Note that a professional site survey will provide exact requirements
- Focus on visible, obvious items only
- If the yard looks clear and ready, say so positively

Output your analysis in strict JSON format:
{
    "has_tree_clearance_needed": boolean,
    "has_structure_relocation_needed": boolean,
    "has_grading_needed": boolean,
    "has_access_considerations": boolean,
    "site_items": [
        {
            "type": "string (e.g., 'Large Tree', 'Shed', 'Slope', 'Narrow Gate')",
            "description": "string (brief description of the specific item)",
            "action": "string ('May need removal', 'May need relocation', 'May need grading', 'Discuss with contractor')",
            "location": "string (e.g., 'Center of yard', 'Left side', 'Near fence')"
        }
    ],
    "assessment_summary": "string (A helpful 2-3 sentence summary of site readiness. Be positive and constructive.)"
}
"""
```

**Step 2: Verify the prompt module loads**

Run: `cd /home/reid/testhome/pools-visualizer && DJANGO_SETTINGS_MODULE=pools_project.settings python3 -c "from api.audit.prompts import get_audit_prompt; print(get_audit_prompt()[:100])"`

Expected: First 100 chars of prompt showing "Pool Installation Site Assessor"

**Step 3: Commit**

```bash
git add api/audit/prompts.py
git commit -m "feat: convert security audit prompt to pool site assessment"
```

---

## Task 2: Update AuditReport Model Fields

**Files:**
- Modify: `api/audit/models.py`

**Step 1: Update model with pool-relevant field names**

```python
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
```

**Step 2: Create migration**

Run: `cd /home/reid/testhome/pools-visualizer && python3 manage.py makemigrations audit --name add_pool_site_assessment_fields`

Expected: Migration file created

**Step 3: Apply migration**

Run: `cd /home/reid/testhome/pools-visualizer && python3 manage.py migrate`

Expected: Migration applied successfully

**Step 4: Commit**

```bash
git add api/audit/models.py api/audit/migrations/
git commit -m "feat: add pool site assessment fields to AuditReport model"
```

---

## Task 3: Update AuditService to Use New Fields

**Files:**
- Modify: `api/audit/services.py`

**Step 1: Update the perform_audit method to use new field names**

Find and replace the AuditReport.objects.create call (around line 51-58):

```python
                # Create AuditReport with new pool site assessment fields
                audit_report = AuditReport.objects.create(
                    request=visualization_request,
                    # New pool site assessment fields
                    has_tree_clearance_needed=result_json.get('has_tree_clearance_needed', False),
                    has_structure_relocation_needed=result_json.get('has_structure_relocation_needed', False),
                    has_grading_needed=result_json.get('has_grading_needed', False),
                    has_access_considerations=result_json.get('has_access_considerations', False),
                    site_items=result_json.get('site_items', []),
                    assessment_summary=result_json.get('assessment_summary', "Site assessment completed."),
                    # Legacy field mappings for backwards compatibility
                    has_ground_level_access=result_json.get('has_tree_clearance_needed', False),
                    has_concealment=result_json.get('has_structure_relocation_needed', False),
                    has_glass_proximity=result_json.get('has_grading_needed', False),
                    has_hardware_weakness=result_json.get('has_access_considerations', False),
                    vulnerabilities=result_json.get('site_items', []),
                    analysis_summary=result_json.get('assessment_summary', "Site assessment completed."),
                )
```

**Step 2: Update the docstring**

Change the class and method docstrings:
- Class: "Service for performing pool site assessments using AI."
- Method: "Performs a site assessment on the backyard image."

**Step 3: Verify import still works**

Run: `cd /home/reid/testhome/pools-visualizer && DJANGO_SETTINGS_MODULE=pools_project.settings python3 -c "from api.audit.services import AuditService; print('OK')"`

Expected: "OK"

**Step 4: Commit**

```bash
git add api/audit/services.py
git commit -m "feat: update AuditService to use pool site assessment fields"
```

---

## Task 4: Update Serializer for New Fields

**Files:**
- Modify: `api/audit/serializers.py`

**Step 1: Read current serializer**

Check what fields are currently serialized.

**Step 2: Update serializer to include new fields**

```python
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
```

**Step 3: Commit**

```bash
git add api/audit/serializers.py
git commit -m "feat: update AuditReportSerializer with pool site assessment fields"
```

---

## Task 5: Update Frontend AuditResults Component

**Files:**
- Modify: `frontend/src/features/audit/AuditResults.js`

**Step 1: Rewrite component for pool site assessment**

```jsx
import React from 'react';
import { TreePine, Home, Mountain, Truck, CheckCircle } from 'lucide-react';

const AuditResults = ({ auditReport }) => {
    if (!auditReport) return null;

    const siteItems = [];

    if (auditReport.has_tree_clearance_needed) {
        siteItems.push({
            icon: <TreePine className="w-6 h-6 text-amber-500" />,
            title: "Tree Clearance",
            desc: "Large trees in the pool zone may need removal."
        });
    }
    if (auditReport.has_structure_relocation_needed) {
        siteItems.push({
            icon: <Home className="w-6 h-6 text-amber-500" />,
            title: "Structure Relocation",
            desc: "Existing structures may need to be moved or removed."
        });
    }
    if (auditReport.has_grading_needed) {
        siteItems.push({
            icon: <Mountain className="w-6 h-6 text-amber-500" />,
            title: "Grading Work",
            desc: "Terrain may require leveling or grading."
        });
    }
    if (auditReport.has_access_considerations) {
        siteItems.push({
            icon: <Truck className="w-6 h-6 text-amber-500" />,
            title: "Access Considerations",
            desc: "Discuss equipment access with your contractor."
        });
    }

    // Use new field names, fall back to legacy
    const summary = auditReport.assessment_summary || auditReport.analysis_summary;

    return (
        <div className="audit-results-container" style={{ marginTop: '2rem' }}>
            <h3 style={{ color: '#0077b6', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle /> Site Assessment
            </h3>

            <div className="audit-summary" style={{
                background: 'rgba(0, 119, 182, 0.1)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                borderLeft: '4px solid #0077b6',
                marginBottom: '1.5rem'
            }}>
                <p style={{ margin: 0, fontStyle: 'italic' }}>"{summary}"</p>
            </div>

            {siteItems.length > 0 && (
                <div className="site-items-grid" style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
                    {siteItems.map((item, index) => (
                        <div key={index} className="site-item-card" style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            padding: '1rem',
                            borderRadius: 'var(--radius-md)',
                            display: 'flex',
                            alignItems: 'start',
                            gap: '1rem'
                        }}>
                            {item.icon}
                            <div>
                                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--white)' }}>{item.title}</h4>
                                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--slate)' }}>{item.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {siteItems.length === 0 && (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#00b4d8' }}>
                    <CheckCircle className="w-12 h-12 mx-auto mb-2" />
                    <p>Your backyard looks ready for pool installation!</p>
                </div>
            )}
        </div>
    );
};

export default AuditResults;
```

**Step 2: Commit**

```bash
git add frontend/src/features/audit/AuditResults.js
git commit -m "feat: update AuditResults component for pool site assessment"
```

---

## Task 6: Update View Docstrings and Comments

**Files:**
- Modify: `api/audit/views.py`

**Step 1: Update docstrings to reflect pool site assessment**

```python
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import VisualizationRequest
from .models import AuditReport
from .serializers import AuditReportSerializer
from .services import AuditService, AuditServiceError

class AuditViewSet(viewsets.ViewSet):
    """
    ViewSet for managing Pool Site Assessments.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Trigger generation of a site assessment for a specific VisualizationRequest.
        """
        visualization_request = get_object_or_404(VisualizationRequest, pk=pk, user=request.user)

        try:
            service = AuditService()
            audit_report = service.perform_audit(visualization_request)
            serializer = AuditReportSerializer(audit_report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except AuditServiceError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def retrieve_report(self, request, pk=None):
        """
        Retrieve the site assessment report for a specific VisualizationRequest.
        """
        visualization_request = get_object_or_404(VisualizationRequest, pk=pk, user=request.user)

        try:
            audit_report = visualization_request.audit_report
            serializer = AuditReportSerializer(audit_report)
            return Response(serializer.data)
        except AuditReport.DoesNotExist:
            return Response({'error': 'Site assessment not found for this request.'}, status=status.HTTP_404_NOT_FOUND)
```

**Step 2: Commit**

```bash
git add api/audit/views.py
git commit -m "docs: update audit views docstrings for pool site assessment"
```

---

## Task 7: Update PDF Generator Audit Section

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Find and update the audit-related section in PDF generator**

The PDF generator references audit_report. Update any security-related text to pool site assessment language.

Look for references to:
- "Security Vulnerability Assessment" → "Site Assessment"
- "has_ground_level_access" → "has_tree_clearance_needed"
- Risk terminology → Preparation terminology

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat: update PDF generator for pool site assessment"
```

---

## Task 8: Final Verification

**Step 1: Run Django check**

Run: `cd /home/reid/testhome/pools-visualizer && python3 manage.py check`

Expected: "System check identified no issues"

**Step 2: Verify migrations are applied**

Run: `cd /home/reid/testhome/pools-visualizer && python3 manage.py showmigrations audit`

Expected: All migrations checked [X]

**Step 3: Start the dev server and verify no import errors**

Run: `cd /home/reid/testhome/pools-visualizer && python3 manage.py runserver 8006 --noreload &`

Expected: Server starts without import errors

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete pool site assessment conversion"
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `api/audit/prompts.py` | New pool site assessment prompt |
| `api/audit/models.py` | New fields + legacy field compatibility |
| `api/audit/services.py` | Updated to use new field names |
| `api/audit/serializers.py` | Include all new fields |
| `api/audit/views.py` | Updated docstrings |
| `frontend/src/features/audit/AuditResults.js` | Pool-themed UI |
| `api/utils/pdf_generator.py` | Updated audit section |
