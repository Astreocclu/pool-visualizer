import React from 'react';
import { TreePine, Home, Mountain, Truck, CheckCircle } from 'lucide-react';

const AuditResults = ({ auditReport }) => {
    if (!auditReport) return null;

    const siteItems = [];

    // Check new field names first, fall back to legacy field names
    const hasTreeClearance = auditReport.has_tree_clearance_needed ?? auditReport.has_ground_level_access;
    const hasStructureRelocation = auditReport.has_structure_relocation_needed ?? auditReport.has_concealment;
    const hasGrading = auditReport.has_grading_needed ?? auditReport.has_glass_proximity;
    const hasAccessConsiderations = auditReport.has_access_considerations ?? auditReport.has_hardware_weakness;

    if (hasTreeClearance) {
        siteItems.push({
            icon: <TreePine className="w-6 h-6 text-amber-500" />,
            title: "Tree Clearance",
            desc: "Large trees in the pool zone may need removal."
        });
    }
    if (hasStructureRelocation) {
        siteItems.push({
            icon: <Home className="w-6 h-6 text-amber-500" />,
            title: "Structure Relocation",
            desc: "Existing structures may need to be moved or removed."
        });
    }
    if (hasGrading) {
        siteItems.push({
            icon: <Mountain className="w-6 h-6 text-amber-500" />,
            title: "Grading Work",
            desc: "Terrain may require leveling or grading."
        });
    }
    if (hasAccessConsiderations) {
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
