import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const ROOF_COLORS = [
  { id: 'charcoal', name: 'Charcoal', hex: '#36454F' },
  { id: 'black', name: 'Black', hex: '#1a1a1a' },
  { id: 'brown', name: 'Brown', hex: '#5C4033' },
  { id: 'tan', name: 'Tan', hex: '#D2B48C' },
  { id: 'terracotta', name: 'Terracotta', hex: '#E2725B' },
  { id: 'slate_gray', name: 'Slate Gray', hex: '#708090' },
  { id: 'weathered_wood', name: 'Weathered Wood', hex: '#8B7355' },
  { id: 'green', name: 'Forest Green', hex: '#228B22' },
  { id: 'blue', name: 'Colonial Blue', hex: '#4169E1' },
  { id: 'white', name: 'White', hex: '#F5F5F5' },
];

const RoofColorStep = ({ nextStep, prevStep }) => {
  const { selections, setRoofColor } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.roof_color || null);

  useEffect(() => {
    if (selections.roof_color) setSelected(selections.roof_color);
  }, [selections.roof_color]);

  const handleSelect = (id) => { setSelected(id); setRoofColor(id); };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Roof Color</h2>
      <p className="step-subtitle">Choose the color for your new roof</p>
      <div className="color-options-grid">
        {ROOF_COLORS.map((c) => (
          <div key={c.id} className={`color-option ${selected === c.id ? 'selected' : ''}`} onClick={() => handleSelect(c.id)}>
            <div className="color-swatch" style={{ backgroundColor: c.hex }} />
            <span className="color-name">{c.name}</span>
          </div>
        ))}
      </div>
      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>Back</button>
        <button className="nav-button primary" onClick={nextStep} disabled={!selected}>Next</button>
      </div>
    </div>
  );
};

export default RoofColorStep;
