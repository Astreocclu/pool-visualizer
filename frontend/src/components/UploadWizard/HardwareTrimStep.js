import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const HARDWARE_FINISHES = [
    { id: 'white', name: 'White' },
    { id: 'brushed_nickel', name: 'Brushed Nickel' },
    { id: 'oil_rubbed_bronze', name: 'Oil-Rubbed Bronze' },
    { id: 'brass', name: 'Brass' },
];

const TRIM_STYLES = [
    { id: 'standard', name: 'Standard', description: 'Simple flat trim' },
    { id: 'craftsman', name: 'Craftsman', description: 'Bold with header detail' },
    { id: 'colonial', name: 'Colonial', description: 'Classic profiled trim' },
    { id: 'modern', name: 'Modern Flat', description: 'Minimal, sleek profile' },
];

const HardwareTrimStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Hardware & Trim</h2>
                <p className="step-subtitle">Choose hardware finish and exterior trim style</p>
            </div>

            <section>
                <h3>Select Hardware Finish</h3>
                <div className="shape-grid">
                    {HARDWARE_FINISHES.map(finish => (
                        <div
                            key={finish.id}
                            className={`shape-card ${selections.hardware_finish === finish.id ? 'selected' : ''}`}
                            onClick={() => setSelection('hardware_finish', finish.id)}
                        >
                            <span>{finish.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Exterior Trim Style</h3>
                <div className="size-grid">
                    {TRIM_STYLES.map(trim => (
                        <div
                            key={trim.id}
                            className={`size-card ${selections.trim_style === trim.id ? 'selected' : ''}`}
                            onClick={() => setSelection('trim_style', trim.id)}
                        >
                            <h4>{trim.name}</h4>
                            <p className="description">{trim.description}</p>
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
                    disabled={!selections.hardware_finish || !selections.trim_style}
                >
                    Generate Visualization <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default HardwareTrimStep;
