import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const FRAME_MATERIALS = [
    { id: 'vinyl', name: 'Vinyl', description: 'Low maintenance, energy efficient' },
    { id: 'wood', name: 'Wood', description: 'Classic beauty, paintable' },
    { id: 'fiberglass', name: 'Fiberglass', description: 'Strong, durable, low expansion' },
    { id: 'aluminum', name: 'Aluminum', description: 'Slim profiles, modern look' },
];

const FRAME_COLORS = [
    { id: 'white', name: 'White' },
    { id: 'tan', name: 'Tan/Almond' },
    { id: 'brown', name: 'Brown' },
    { id: 'black', name: 'Black' },
    { id: 'bronze', name: 'Bronze' },
];

const FrameMaterialStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Frame Material & Color</h2>
                <p className="step-subtitle">Choose your frame material and finish color</p>
            </div>

            <section>
                <h3>Select Frame Material</h3>
                <div className="size-grid">
                    {FRAME_MATERIALS.map(material => (
                        <div
                            key={material.id}
                            className={`size-card ${selections.frame_material === material.id ? 'selected' : ''}`}
                            onClick={() => setSelection('frame_material', material.id)}
                        >
                            <h4>{material.name}</h4>
                            <p className="description">{material.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Frame Color</h3>
                <div className="shape-grid">
                    {FRAME_COLORS.map(color => (
                        <div
                            key={color.id}
                            className={`shape-card ${selections.frame_color === color.id ? 'selected' : ''}`}
                            onClick={() => setSelection('frame_color', color.id)}
                        >
                            <span>{color.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.frame_material || !selections.frame_color}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default FrameMaterialStep;
