import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const INTERIOR_FINISHES = [
    { id: 'white_plaster', name: 'White Plaster', water_color: 'Light turquoise/aqua' },
    { id: 'pebble_blue', name: 'Pebble Tec - Blue', water_color: 'Deep ocean blue', popular: true },
    { id: 'pebble_midnight', name: 'Pebble Tec - Midnight', water_color: 'Dark navy/black' },
    { id: 'quartz_blue', name: 'Quartz - Ocean Blue', water_color: 'Vibrant blue' },
    { id: 'quartz_aqua', name: 'Quartz - Caribbean', water_color: 'Bright Caribbean aqua' },
    { id: 'glass_tile', name: 'Glass Tile', water_color: 'Crystal clear with shimmer' },
];

const FinishBuiltInsStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Finish & Built-ins</h2>
                <p className="step-subtitle">Select your pool's interior finish and built-in features</p>
            </div>

            <section>
                <h3>Interior Finish</h3>
                <p className="helper-text">The finish affects your pool's water color</p>
                <div className="finish-grid">
                    {INTERIOR_FINISHES.map(finish => (
                        <div
                            key={finish.id}
                            className={`finish-card ${selections.finish === finish.id ? 'selected' : ''} ${finish.popular ? 'popular' : ''}`}
                            onClick={() => setSelection('finish', finish.id)}
                        >
                            {finish.popular && <span className="popular-badge">Popular</span>}
                            <h4>{finish.name}</h4>
                            <p className="water-color">{finish.water_color}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Built-in Features</h3>
                <div className="builtin-options">
                    {/* Tanning Ledge Toggle */}
                    <div className="option-row">
                        <div className="option-label">
                            <h4>Tanning Ledge</h4>
                            <p>Shallow shelf for lounging in the water</p>
                        </div>
                        <label className="toggle-switch">
                            <input
                                type="checkbox"
                                checked={selections.tanning_ledge}
                                onChange={(e) => setSelection('tanning_ledge', e.target.checked)}
                            />
                            <span className="slider"></span>
                        </label>
                    </div>

                    {/* Ledge Lounger Count - Only visible when tanning_ledge is true */}
                    {selections.tanning_ledge && (
                        <div className="option-row sub-option">
                            <div className="option-label">
                                <h4>Ledge Loungers</h4>
                                <p>How many in-pool chaise lounges?</p>
                            </div>
                            <select
                                className="option-dropdown"
                                value={selections.lounger_count}
                                onChange={(e) => setSelection('lounger_count', parseInt(e.target.value))}
                            >
                                <option value="0">None</option>
                                <option value="2">2 Loungers</option>
                                <option value="4">4 Loungers</option>
                            </select>
                        </div>
                    )}

                    {/* Attached Spa Toggle */}
                    <div className="option-row">
                        <div className="option-label">
                            <h4>Attached Spa</h4>
                            <p>Add a hot tub connected to your pool</p>
                        </div>
                        <label className="toggle-switch">
                            <input
                                type="checkbox"
                                checked={selections.attached_spa}
                                onChange={(e) => setSelection('attached_spa', e.target.checked)}
                            />
                            <span className="slider"></span>
                        </label>
                    </div>
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
                    disabled={!selections.finish}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default FinishBuiltInsStep;
