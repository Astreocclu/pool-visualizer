import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const ROOF_MATERIALS = [
  { id: 'asphalt_3tab', name: 'Asphalt - 3-Tab', description: 'Affordable, classic look' },
  { id: 'asphalt_architectural', name: 'Asphalt - Architectural', description: 'Premium look, 30 year lifespan', popular: true },
  { id: 'metal_standing_seam', name: 'Metal - Standing Seam', description: 'Modern, durable, 50+ years', popular: true },
  { id: 'metal_corrugated', name: 'Metal - Corrugated', description: 'Industrial/farmhouse look' },
  { id: 'clay_tile', name: 'Clay Tile', description: 'Mediterranean style, 100+ years' },
  { id: 'concrete_tile', name: 'Concrete Tile', description: 'Durable, fire-resistant' },
  { id: 'slate', name: 'Natural Slate', description: 'Premium stone, 100+ years' },
  { id: 'wood_shake', name: 'Wood Shake', description: 'Rustic natural look' },
  { id: 'tpo_flat', name: 'TPO (Flat Roof)', description: 'For flat/low-slope roofs' },
];

const RoofMaterialStep = ({ nextStep }) => {
  const { selections, setRoofMaterial } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.roof_material || null);

  useEffect(() => {
    if (selections.roof_material) setSelected(selections.roof_material);
  }, [selections.roof_material]);

  const handleSelect = (id) => { setSelected(id); setRoofMaterial(id); };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Roofing Material</h2>
      <p className="step-subtitle">Choose the type of roofing for your home</p>
      <div className="options-grid">
        {ROOF_MATERIALS.map((m) => (
          <div key={m.id} className={`option-card ${selected === m.id ? 'selected' : ''}`} onClick={() => handleSelect(m.id)}>
            {m.popular && <span className="popular-badge">Popular</span>}
            <h3 className="option-name">{m.name}</h3>
            <p className="option-description">{m.description}</p>
          </div>
        ))}
      </div>
      <div className="wizard-navigation">
        <button className="nav-button primary" onClick={nextStep} disabled={!selected}>Next</button>
      </div>
    </div>
  );
};

export default RoofMaterialStep;
