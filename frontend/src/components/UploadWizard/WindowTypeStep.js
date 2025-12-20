// frontend/src/components/UploadWizard/WindowTypeStep.js
import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const WINDOW_TYPES = [
    { id: 'single_hung', name: 'Single Hung', description: 'Bottom sash slides up, top is fixed' },
    { id: 'double_hung', name: 'Double Hung', description: 'Both sashes slide up and down', popular: true },
    { id: 'casement', name: 'Casement', description: 'Hinged on side, swings outward' },
    { id: 'slider', name: 'Slider', description: 'Sash slides horizontally' },
    { id: 'picture', name: 'Picture', description: 'Fixed, non-operable for views' },
];

const WINDOW_STYLES = [
    { id: 'modern', name: 'Modern' },
    { id: 'traditional', name: 'Traditional' },
    { id: 'colonial', name: 'Colonial' },
    { id: 'craftsman', name: 'Craftsman' },
];

const WindowTypeStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Window Type & Style</h2>
                <p className="step-subtitle">Choose your window type and architectural style</p>
            </div>

            <section>
                <h3>Select Window Type</h3>
                <div className="size-grid">
                    {WINDOW_TYPES.map(type => (
                        <div
                            key={type.id}
                            className={`size-card ${selections.window_type === type.id ? 'selected' : ''} ${type.popular ? 'popular' : ''}`}
                            onClick={() => setSelection('window_type', type.id)}
                        >
                            {type.popular && <span className="popular-badge">Popular</span>}
                            <h4>{type.name}</h4>
                            <p className="description">{type.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Architectural Style</h3>
                <div className="shape-grid">
                    {WINDOW_STYLES.map(style => (
                        <div
                            key={style.id}
                            className={`shape-card ${selections.window_style === style.id ? 'selected' : ''}`}
                            onClick={() => setSelection('window_style', style.id)}
                        >
                            <span>{style.name}</span>
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
                    disabled={!selections.window_type || !selections.window_style}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default WindowTypeStep;
