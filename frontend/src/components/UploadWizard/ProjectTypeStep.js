import React, { useEffect, useState } from 'react';
import { Home, PlusSquare, Sun } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const PROJECT_TYPES = [
  {
    id: 'replace_existing',
    name: 'Replace Existing',
    description: 'Replace current windows and/or doors with new ones',
    icon: Home,
  },
  {
    id: 'new_opening',
    name: 'Create New Opening',
    description: 'Add new windows or doors where none exist',
    icon: PlusSquare,
  },
  {
    id: 'enclose_patio',
    name: 'Enclose Patio',
    description: 'Convert open patio/porch to enclosed sunroom',
    icon: Sun,
    popular: true,
  },
];

const ProjectTypeStep = ({ nextStep }) => {
  const { selections, setProjectType } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.project_type || null);

  useEffect(() => {
    if (selections.project_type) {
      setSelected(selections.project_type);
    }
  }, [selections.project_type]);

  const handleSelect = (typeId) => {
    setSelected(typeId);
    setProjectType(typeId);
  };

  const handleNext = () => {
    if (selected) {
      nextStep();
    }
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">What type of project is this?</h2>
      <p className="step-subtitle">Select your project type to get started</p>

      <div className="options-grid three-column">
        {PROJECT_TYPES.map((type) => {
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

export default ProjectTypeStep;
