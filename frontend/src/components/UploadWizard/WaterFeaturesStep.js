import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const WATER_FEATURES = [
    { id: 'rock_waterfall', name: 'Rock Waterfall' },
    { id: 'bubblers', name: 'Bubblers / Fountain Jets' },
    { id: 'scuppers', name: 'Scuppers' },
    { id: 'fire_bowls', name: 'Fire Bowls' },
    { id: 'deck_jets', name: 'Deck Jets' },
];

const WaterFeaturesStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    // Initialize water_features as empty array if undefined
    const waterFeatures = selections.water_features || [];

    const handleFeatureToggle = (featureId) => {
        const isSelected = waterFeatures.includes(featureId);

        if (isSelected) {
            // Remove the feature
            const updated = waterFeatures.filter(id => id !== featureId);
            setSelection('water_features', updated);
        } else {
            // Add the feature if we haven't reached the max
            if (waterFeatures.length < 2) {
                const updated = [...waterFeatures, featureId];
                setSelection('water_features', updated);
            }
            // Silently ignore if already at max (UI feedback is visual via disabled state)
        }
    };

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Water Features</h2>
                <p className="step-subtitle">Add ambiance with water features (Optional - Select up to 2)</p>
            </div>

            <section>
                <h3>Select Water Features</h3>
                <p className="helper-text">
                    {waterFeatures.length === 0 && "Choose up to 2 features or skip this step"}
                    {waterFeatures.length === 1 && "You can select 1 more feature"}
                    {waterFeatures.length === 2 && "Maximum features selected"}
                </p>
                <div className="feature-grid">
                    {WATER_FEATURES.map(feature => {
                        const isSelected = waterFeatures.includes(feature.id);
                        const isDisabled = !isSelected && waterFeatures.length >= 2;

                        return (
                            <div
                                key={feature.id}
                                className={`feature-card ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                                onClick={() => !isDisabled && handleFeatureToggle(feature.id)}
                            >
                                <div className="feature-checkbox">
                                    {isSelected && <span className="checkmark">✓</span>}
                                </div>
                                <h4>{feature.name}</h4>
                            </div>
                        );
                    })}
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
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default WaterFeaturesStep;
