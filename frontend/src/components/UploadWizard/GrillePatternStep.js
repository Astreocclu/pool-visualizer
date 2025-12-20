import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const GRILLE_PATTERNS = [
    { id: 'none', name: 'No Grilles', description: 'Clean, unobstructed view' },
    { id: 'colonial', name: 'Colonial', description: '6 or 9 pane grid pattern' },
    { id: 'prairie', name: 'Prairie', description: 'Border grilles only' },
    { id: 'craftsman', name: 'Craftsman', description: 'Top section grilles only' },
    { id: 'diamond', name: 'Diamond', description: 'Diagonal pattern' },
];

const GLASS_OPTIONS = [
    { id: 'clear', name: 'Clear', description: 'Maximum light and visibility' },
    { id: 'low_e', name: 'Low-E', description: 'Energy efficient coating' },
    { id: 'frosted', name: 'Frosted', description: 'Privacy with diffused light' },
    { id: 'obscure', name: 'Obscure', description: 'Textured privacy glass' },
    { id: 'rain', name: 'Rain', description: 'Decorative rain pattern' },
];

const GrillePatternStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Grilles & Glass</h2>
                <p className="step-subtitle">Choose grille pattern and glass type</p>
            </div>

            <section>
                <h3>Select Grille Pattern</h3>
                <div className="size-grid">
                    {GRILLE_PATTERNS.map(pattern => (
                        <div
                            key={pattern.id}
                            className={`size-card ${selections.grille_pattern === pattern.id ? 'selected' : ''}`}
                            onClick={() => setSelection('grille_pattern', pattern.id)}
                        >
                            <h4>{pattern.name}</h4>
                            <p className="description">{pattern.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Glass Type</h3>
                <div className="size-grid">
                    {GLASS_OPTIONS.map(glass => (
                        <div
                            key={glass.id}
                            className={`size-card ${selections.glass_option === glass.id ? 'selected' : ''}`}
                            onClick={() => setSelection('glass_option', glass.id)}
                        >
                            <h4>{glass.name}</h4>
                            <p className="description">{glass.description}</p>
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
                    disabled={!selections.grille_pattern || !selections.glass_option}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default GrillePatternStep;
