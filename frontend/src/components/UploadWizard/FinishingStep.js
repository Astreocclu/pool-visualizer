import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const LIGHTING_OPTIONS = [
    { id: 'none', name: 'No Additional Lighting' },
    { id: 'pool_lights', name: 'LED Pool Lights' },
    { id: 'landscape', name: 'Landscape Lighting' },
    { id: 'both', name: 'Pool + Landscape Lights' },
];

const LANDSCAPING_OPTIONS = [
    { id: 'none', name: 'Existing Only' },
    { id: 'tropical', name: 'Tropical Plants' },
    { id: 'desert', name: 'Desert/Modern' },
    { id: 'natural', name: 'Natural/Native' },
];

const FURNITURE_OPTIONS = [
    { id: 'none', name: 'No Furniture' },
    { id: 'basic', name: 'Lounge Chairs' },
    { id: 'full', name: 'Full Outdoor Set' },
];

const FinishingStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    // Get current selections with 'none' as default
    const lighting = selections.lighting || 'none';
    const landscaping = selections.landscaping || 'none';
    const furniture = selections.furniture || 'none';

    const handleLightingChange = (value) => {
        setSelection('lighting', value);
    };

    const handleLandscapingChange = (value) => {
        setSelection('landscaping', value);
    };

    const handleFurnitureChange = (value) => {
        setSelection('furniture', value);
    };

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Finishing Touches</h2>
                <p className="step-subtitle">Add the final details to complete your design (All Optional)</p>
            </div>

            <section>
                <h3>Lighting</h3>
                <p className="helper-text">Choose your preferred lighting setup</p>
                <div className="radio-group">
                    {LIGHTING_OPTIONS.map(option => (
                        <label
                            key={option.id}
                            className={`radio-option ${lighting === option.id ? 'selected' : ''}`}
                        >
                            <input
                                type="radio"
                                name="lighting"
                                value={option.id}
                                checked={lighting === option.id}
                                onChange={(e) => handleLightingChange(e.target.value)}
                            />
                            <span className="radio-label">{option.name}</span>
                        </label>
                    ))}
                </div>
            </section>

            <section>
                <h3>Landscaping</h3>
                <p className="helper-text">Select your landscaping style</p>
                <div className="radio-group">
                    {LANDSCAPING_OPTIONS.map(option => (
                        <label
                            key={option.id}
                            className={`radio-option ${landscaping === option.id ? 'selected' : ''}`}
                        >
                            <input
                                type="radio"
                                name="landscaping"
                                value={option.id}
                                checked={landscaping === option.id}
                                onChange={(e) => handleLandscapingChange(e.target.value)}
                            />
                            <span className="radio-label">{option.name}</span>
                        </label>
                    ))}
                </div>
            </section>

            <section>
                <h3>Outdoor Furniture</h3>
                <p className="helper-text">Add furniture to your pool area</p>
                <div className="radio-group">
                    {FURNITURE_OPTIONS.map(option => (
                        <label
                            key={option.id}
                            className={`radio-option ${furniture === option.id ? 'selected' : ''}`}
                        >
                            <input
                                type="radio"
                                name="furniture"
                                value={option.id}
                                checked={furniture === option.id}
                                onChange={(e) => handleFurnitureChange(e.target.value)}
                            />
                            <span className="radio-label">{option.name}</span>
                        </label>
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
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default FinishingStep;
