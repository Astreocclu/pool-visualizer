import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const DECK_MATERIALS = [
    { id: 'travertine', name: 'Travertine', popular: true },
    { id: 'pavers', name: 'Pavers' },
    { id: 'brushed_concrete', name: 'Brushed Concrete' },
    { id: 'stamped_concrete', name: 'Stamped Concrete' },
    { id: 'flagstone', name: 'Flagstone' },
    { id: 'wood', name: 'Wood Deck' },
];

const DECK_COLORS = [
    { id: 'cream', name: 'Cream', hex: '#F5F5DC' },
    { id: 'tan', name: 'Tan', hex: '#D2B48C' },
    { id: 'gray', name: 'Gray', hex: '#808080' },
    { id: 'terracotta', name: 'Terracotta', hex: '#E2725B' },
    { id: 'brown', name: 'Brown', hex: '#8B4513' },
    { id: 'natural', name: 'Natural Stone', hex: '#C4B7A6' },
];

const DeckStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Deck Material & Color</h2>
                <p className="step-subtitle">Select the material and color for your pool deck</p>
            </div>

            <section>
                <h3>Deck Material</h3>
                <div className="deck-material-grid">
                    {DECK_MATERIALS.map(material => (
                        <div
                            key={material.id}
                            className={`deck-material-card ${selections.deck_material === material.id ? 'selected' : ''}`}
                            onClick={() => setSelection('deck_material', material.id)}
                        >
                            {material.popular && <span className="popular-badge">Popular</span>}
                            <span>{material.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Deck Color</h3>
                <div className="deck-color-grid">
                    {DECK_COLORS.map(color => (
                        <div
                            key={color.id}
                            className={`deck-color-chip ${selections.deck_color === color.id ? 'selected' : ''}`}
                            onClick={() => setSelection('deck_color', color.id)}
                        >
                            <div
                                className="color-circle"
                                style={{ backgroundColor: color.hex }}
                            />
                            <span>{color.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                {prevStep && (
                    <button className="btn-back" onClick={prevStep}>
                        <ArrowLeft size={18} /> Back
                    </button>
                )}
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.deck_material || !selections.deck_color}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default DeckStep;
