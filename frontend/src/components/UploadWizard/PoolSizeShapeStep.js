import { ArrowLeft, ArrowRight, Square, Circle, Hexagon, Pentagon, Octagon } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const POOL_SIZES = [
    { id: 'starter', name: 'Starter', dimensions: '12x24', description: 'Best for: Small yards, couples, plunge pools' },
    { id: 'classic', name: 'Classic', dimensions: '15x30', description: 'Best for: Average yards, families', popular: true },
    { id: 'family', name: 'Family', dimensions: '16x36', description: 'Best for: Larger yards, kids, entertaining' },
    { id: 'resort', name: 'Resort', dimensions: '18x40', description: 'Best for: Large properties, serious swimmers' },
];

const POOL_SHAPES = [
    { id: 'rectangle', name: 'Rectangle' },
    { id: 'roman', name: 'Roman' },
    { id: 'grecian', name: 'Grecian' },
    { id: 'kidney', name: 'Kidney' },
    { id: 'freeform', name: 'Freeform' },
    { id: 'lazy_l', name: 'Lazy L' },
    { id: 'oval', name: 'Oval' },
];

const PoolSizeShapeStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Pool Size & Shape</h2>
                <p className="step-subtitle">Choose your pool dimensions and style</p>
            </div>

            <section>
                <h3>Select Pool Size</h3>
                <div className="size-grid">
                    {POOL_SIZES.map(size => (
                        <div
                            key={size.id}
                            className={`size-card ${selections.size === size.id ? 'selected' : ''} ${size.popular ? 'popular' : ''}`}
                            onClick={() => setSelection('size', size.id)}
                        >
                            {size.popular && <span className="popular-badge">Popular</span>}
                            <h4>{size.name}</h4>
                            <p className="dimensions">{size.dimensions}</p>
                            <p className="description">{size.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Pool Shape</h3>
                <div className="shape-grid">
                    {POOL_SHAPES.map(shape => (
                        <div
                            key={shape.id}
                            className={`shape-card ${selections.shape === shape.id ? 'selected' : ''}`}
                            onClick={() => setSelection('shape', shape.id)}
                        >
                            <div className="shape-icon">
                                <Square size={32} />
                            </div>
                            <span>{shape.name}</span>
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
                    disabled={!selections.size || !selections.shape}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default PoolSizeShapeStep;
