import React, { useEffect, useState } from 'react';
import { Sun, Zap } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const SOLAR_OPTIONS = [
  { id: 'none', name: 'No Solar', description: 'Roof only, no solar panels', icon: null },
  { id: 'partial', name: 'Partial Coverage', description: 'Solar on part of the roof', icon: Sun, popular: true },
  { id: 'full_south', name: 'Full South Roof', description: 'Maximize solar on south-facing', icon: Zap },
  { id: 'full_all', name: 'Maximum Coverage', description: 'Solar on all viable areas', icon: Zap },
];

const SolarOptionStep = ({ nextStep, prevStep }) => {
  const { selections, setSolarOption } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.solar_option || null);

  useEffect(() => {
    if (selections.solar_option) setSelected(selections.solar_option);
  }, [selections.solar_option]);

  const handleSelect = (id) => { setSelected(id); setSolarOption(id); };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Solar Panel Options</h2>
      <p className="step-subtitle">Would you like to add solar panels?</p>
      <div className="options-grid">
        {SOLAR_OPTIONS.map((o) => {
          const Icon = o.icon;
          return (
            <div key={o.id} className={`option-card ${selected === o.id ? 'selected' : ''}`} onClick={() => handleSelect(o.id)}>
              {o.popular && <span className="popular-badge">Popular</span>}
              {Icon && <div className="option-icon"><Icon size={32} /></div>}
              <h3 className="option-name">{o.name}</h3>
              <p className="option-description">{o.description}</p>
            </div>
          );
        })}
      </div>
      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>Back</button>
        <button className="nav-button primary" onClick={nextStep} disabled={!selected}>Next</button>
      </div>
    </div>
  );
};

export default SolarOptionStep;
