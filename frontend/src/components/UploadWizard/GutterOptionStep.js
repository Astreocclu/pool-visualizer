import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const GUTTER_OPTIONS = [
  { id: 'none', name: 'No Gutters', description: 'No gutter system' },
  { id: 'standard', name: 'Standard Gutters', description: 'Aluminum K-style gutters', popular: true },
  { id: 'seamless', name: 'Seamless Gutters', description: 'Premium seamless system' },
  { id: 'copper', name: 'Copper Gutters', description: 'Premium copper half-round' },
];

const GutterOptionStep = ({ nextStep, prevStep }) => {
  const { selections, setGutterOption } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.gutter_option || null);

  useEffect(() => {
    if (selections.gutter_option) setSelected(selections.gutter_option);
  }, [selections.gutter_option]);

  const handleSelect = (id) => { setSelected(id); setGutterOption(id); };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Gutter Options</h2>
      <p className="step-subtitle">Select a gutter system for your new roof</p>
      <div className="options-grid">
        {GUTTER_OPTIONS.map((o) => (
          <div key={o.id} className={`option-card ${selected === o.id ? 'selected' : ''}`} onClick={() => handleSelect(o.id)}>
            {o.popular && <span className="popular-badge">Popular</span>}
            <h3 className="option-name">{o.name}</h3>
            <p className="option-description">{o.description}</p>
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

export default GutterOptionStep;
