import React from 'react';
import useVisualizerStore from '../../store/visualizerStore';
import './WizardStep.css';

const DECK_MATERIALS = [
    { id: 'travertine', name: 'Travertine', popular: true },
    { id: 'pavers', name: 'Pavers' },
    { id: 'brushed_concrete', name: 'Brushed Concrete' },
    { id: 'stamped_concrete', name: 'Stamped Concrete' },
    { id: 'flagstone', name: 'Flagstone' },
    { id: 'wood', name: 'Wood Deck' },
];

const DECK_COLORS = [
    { id: 'cream', name: 'Cream' },
    { id: 'tan', name: 'Tan' },
    { id: 'gray', name: 'Gray' },
    { id: 'terracotta', name: 'Terracotta' },
    { id: 'brown', name: 'Brown' },
    { id: 'natural', name: 'Natural Stone' },
];

function DeckStep() {
    const { selections, setSelection } = useVisualizerStore();

    const handleMaterialSelect = (materialId) => {
        setSelection('deck_material', materialId);
    };

    const handleColorSelect = (colorId) => {
        setSelection('deck_color', colorId);
    };

    return (
        <div className="wizard-step">
            <h2 className="wizard-step-title">Choose Your Deck</h2>
            <p className="wizard-step-description">
                Select the material and color for your pool deck
            </p>

            <div className="wizard-section">
                <h3 className="wizard-section-title">Deck Material</h3>
                <div className="wizard-options">
                    {DECK_MATERIALS.map((material) => (
                        <button
                            key={material.id}
                            className={`wizard-option ${
                                selections.deck_material === material.id ? 'selected' : ''
                            }`}
                            onClick={() => handleMaterialSelect(material.id)}
                        >
                            {material.name}
                            {material.popular && (
                                <span className="wizard-badge">Popular</span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            <div className="wizard-section">
                <h3 className="wizard-section-title">Deck Color</h3>
                <div className="wizard-options">
                    {DECK_COLORS.map((color) => (
                        <button
                            key={color.id}
                            className={`wizard-option ${
                                selections.deck_color === color.id ? 'selected' : ''
                            }`}
                            onClick={() => handleColorSelect(color.id)}
                        >
                            <span className={`color-chip deck-${color.id}`}></span>
                            {color.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default DeckStep;
