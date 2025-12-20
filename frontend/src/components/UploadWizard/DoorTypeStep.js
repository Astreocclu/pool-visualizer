import React, { useEffect, useState } from 'react';
import { Square, Columns, FoldVertical, DoorOpen } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const DOOR_TYPES = [
  {
    id: 'none',
    name: 'Windows Only',
    description: 'No doors, windows only',
    icon: Square,
  },
  {
    id: 'sliding_glass',
    name: 'Sliding Glass Door',
    description: 'Standard sliding glass door for patio access',
    icon: Columns,
    popular: true,
  },
  {
    id: 'accordion',
    name: 'Accordion Door',
    description: 'Multi-panel folding door that opens completely',
    icon: FoldVertical,
    popular: true,
  },
  {
    id: 'bi_fold',
    name: 'Bi-Fold Door',
    description: 'Panels fold in pairs for wide opening',
    icon: FoldVertical,
  },
  {
    id: 'french',
    name: 'French Door',
    description: 'Classic hinged double doors with glass',
    icon: DoorOpen,
  },
];

const DoorTypeStep = ({ nextStep, prevStep }) => {
  const { selections, setDoorType } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.door_type || null);

  useEffect(() => {
    if (selections.door_type) {
      setSelected(selections.door_type);
    }
  }, [selections.door_type]);

  const handleSelect = (typeId) => {
    setSelected(typeId);
    setDoorType(typeId);
  };

  const handleNext = () => {
    if (selected) {
      nextStep();
    }
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Door Type</h2>
      <p className="step-subtitle">Choose the type of door for your project (or windows only)</p>

      <div className="options-grid">
        {DOOR_TYPES.map((type) => {
          const IconComponent = type.icon;
          return (
            <div
              key={type.id}
              className={`option-card ${selected === type.id ? 'selected' : ''}`}
              onClick={() => handleSelect(type.id)}
            >
              {type.popular && <span className="popular-badge">Popular</span>}
              <div className="option-icon">
                <IconComponent size={32} />
              </div>
              <h3 className="option-name">{type.name}</h3>
              <p className="option-description">{type.description}</p>
            </div>
          );
        })}
      </div>

      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>
          Back
        </button>
        <button
          className="nav-button primary"
          onClick={handleNext}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default DoorTypeStep;
