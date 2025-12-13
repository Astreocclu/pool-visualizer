import { useState } from 'react';
import { ArrowLeft, Droplets, Square, Palette, Waves } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const Step2Scope = ({ nextStep, prevStep }) => {
    const { scope, setScope } = useVisualizationStore();
    const [subStep, setSubStep] = useState('shape');

    const selectOption = (key, value, next) => {
        setScope(key, value);
        if (next === 'done') {
            nextStep();
        } else {
            setSubStep(next);
        }
    };

    return (
        <div className="wizard-step fade-in">
            {/* POOL SHAPE */}
            {subStep === 'shape' && (
                <>
                    <div className="step-header">
                        <Square size={48} className="step-icon" />
                        <h2>What pool shape do you want?</h2>
                        <p className="step-subtitle">Choose the shape for your pool</p>
                    </div>
                    <div className="choice-cards vertical">
                        <button className="choice-card" onClick={() => selectOption('poolShape', 'rectangle', 'surface')}>
                            <span>Rectangle</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('poolShape', 'freeform', 'surface')}>
                            <span>Freeform / Organic</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('poolShape', 'kidney', 'surface')}>
                            <span>Kidney</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('poolShape', 'lshaped', 'surface')}>
                            <span>L-Shaped</span>
                        </button>
                    </div>
                </>
            )}

            {/* POOL SURFACE */}
            {subStep === 'surface' && (
                <>
                    <div className="step-header">
                        <Palette size={48} className="step-icon" />
                        <h2>What pool surface finish?</h2>
                        <p className="step-subtitle">This affects the water color appearance</p>
                    </div>
                    <div className="choice-cards vertical">
                        <button className="choice-card" onClick={() => selectOption('poolSurface', 'white_plaster', 'deck')}>
                            <span>White Plaster (Light Blue Water)</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('poolSurface', 'pebble_tec_blue', 'deck')}>
                            <span>Pebble Tec Blue (Deep Blue Water)</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('poolSurface', 'pebble_tec_midnight', 'deck')}>
                            <span>Pebble Tec Midnight (Dark Blue Water)</span>
                        </button>
                    </div>
                </>
            )}

            {/* DECK MATERIAL */}
            {subStep === 'deck' && (
                <>
                    <div className="step-header">
                        <Droplets size={48} className="step-icon" />
                        <h2>What deck material?</h2>
                        <p className="step-subtitle">Choose the surrounding deck finish</p>
                    </div>
                    <div className="choice-cards vertical">
                        <button className="choice-card" onClick={() => selectOption('deckMaterial', 'travertine', 'waterFeature')}>
                            <span>Travertine</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('deckMaterial', 'concrete', 'waterFeature')}>
                            <span>Stamped Concrete</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('deckMaterial', 'pavers', 'waterFeature')}>
                            <span>Pavers</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('deckMaterial', 'wood', 'waterFeature')}>
                            <span>Wood Deck</span>
                        </button>
                    </div>
                </>
            )}

            {/* WATER FEATURE */}
            {subStep === 'waterFeature' && (
                <>
                    <div className="step-header">
                        <Waves size={48} className="step-icon" />
                        <h2>Add a water feature?</h2>
                        <p className="step-subtitle">Optional enhancement</p>
                    </div>
                    <div className="choice-cards vertical">
                        <button className="choice-card" onClick={() => selectOption('waterFeature', 'none', 'done')}>
                            <span>No Water Feature</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('waterFeature', 'waterfall', 'done')}>
                            <span>Waterfall</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('waterFeature', 'fountain', 'done')}>
                            <span>Fountain Jets</span>
                        </button>
                        <button className="choice-card" onClick={() => selectOption('waterFeature', 'infinity_edge', 'done')}>
                            <span>Infinity Edge</span>
                        </button>
                    </div>
                </>
            )}

            <div className="wizard-actions">
                <button className="btn-back" onClick={subStep === 'shape' ? prevStep : () => {
                    const prevSteps = { surface: 'shape', deck: 'surface', waterFeature: 'deck' };
                    setSubStep(prevSteps[subStep] || 'shape');
                }}>
                    <ArrowLeft size={18} /> Back
                </button>
            </div>
        </div>
    );
};

export default Step2Scope;
