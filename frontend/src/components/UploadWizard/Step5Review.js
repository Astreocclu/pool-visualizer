import React from 'react';
import { ArrowLeft, Droplets } from 'lucide-react';

// Config lookup tables (must match backend config.py)
const POOL_SIZES = {
    starter: { name: 'Starter', dimensions: '12x24' },
    classic: { name: 'Classic', dimensions: '15x30' },
    family: { name: 'Family', dimensions: '16x36' },
    resort: { name: 'Resort', dimensions: '18x40' },
};

const POOL_SHAPES = {
    rectangle: 'Rectangle',
    roman: 'Roman',
    grecian: 'Grecian',
    kidney: 'Kidney',
    freeform: 'Freeform',
    lazy_l: 'Lazy L',
    oval: 'Oval',
};

const INTERIOR_FINISHES = {
    white_plaster: { name: 'White Plaster', water_color: 'Light Turquoise' },
    pebble_blue: { name: 'Pebble Tec - Blue', water_color: 'Deep Ocean Blue' },
    pebble_midnight: { name: 'Pebble Tec - Midnight', water_color: 'Dark Navy' },
    quartz_blue: { name: 'Quartz - Ocean Blue', water_color: 'Vibrant Blue' },
    quartz_aqua: { name: 'Quartz - Caribbean', water_color: 'Caribbean Aqua' },
    glass_tile: { name: 'Glass Tile', water_color: 'Crystal Clear' },
};

const DECK_MATERIALS = {
    travertine: 'Travertine',
    pavers: 'Pavers',
    brushed_concrete: 'Brushed Concrete',
    stamped_concrete: 'Stamped Concrete',
    flagstone: 'Flagstone',
    wood: 'Wood Deck',
};

const DECK_COLORS = {
    cream: 'Cream',
    tan: 'Tan',
    gray: 'Gray',
    terracotta: 'Terracotta',
    brown: 'Brown',
    natural: 'Natural Stone',
};

const WATER_FEATURES = {
    rock_waterfall: 'Rock Waterfall',
    bubblers: 'Bubblers / Fountain Jets',
    scuppers: 'Scuppers',
    fire_bowls: 'Fire Bowls',
    deck_jets: 'Deck Jets',
};

const LIGHTING_OPTIONS = {
    none: 'No Additional Lighting',
    pool_lights: 'LED Pool Lights',
    landscape: 'Landscape Lighting',
    both: 'Pool + Landscape Lights',
};

const LANDSCAPING_OPTIONS = {
    none: 'Existing Only',
    tropical: 'Tropical Plants',
    desert: 'Desert/Modern',
    natural: 'Natural/Native',
};

const FURNITURE_OPTIONS = {
    none: 'No Furniture',
    basic: 'Lounge Chairs',
    full: 'Full Outdoor Set',
};

const Step5Review = ({ formData, selections, prevStep, handleSubmit, isSubmitting, error }) => {
    const sizeInfo = POOL_SIZES[selections.size] || { name: selections.size, dimensions: '' };
    const finishInfo = INTERIOR_FINISHES[selections.finish] || { name: selections.finish, water_color: '' };

    // Check if any finishing touches are selected
    const hasFinishingTouches =
        selections.lighting !== 'none' ||
        selections.landscaping !== 'none' ||
        selections.furniture !== 'none';

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Ready to Visualize?</h2>
                <p className="step-subtitle">Review your pool selections</p>
            </div>

            <div className="review-card">
                {/* Pool Size & Shape */}
                <div className="review-section">
                    <h3 className="review-section-title">Pool Size & Shape</h3>
                    <div className="review-item">
                        <span className="label">Size</span>
                        <span className="value">
                            {sizeInfo.name}
                            {sizeInfo.dimensions && ` (${sizeInfo.dimensions} ft)`}
                        </span>
                    </div>
                    <div className="review-item">
                        <span className="label">Shape</span>
                        <span className="value">{POOL_SHAPES[selections.shape] || selections.shape}</span>
                    </div>
                </div>

                {/* Interior Finish */}
                <div className="review-section">
                    <h3 className="review-section-title">Interior Finish</h3>
                    <div className="review-item">
                        <span className="label">Finish</span>
                        <span className="value">{finishInfo.name}</span>
                    </div>
                    <div className="review-item">
                        <span className="label">Water Color</span>
                        <span className="value">{finishInfo.water_color}</span>
                    </div>
                </div>

                {/* Built-in Features */}
                <div className="review-section">
                    <h3 className="review-section-title">Built-in Features</h3>
                    <div className="review-item">
                        <span className="label">Tanning Ledge</span>
                        <span className="value">{selections.tanning_ledge ? 'Yes' : 'No'}</span>
                    </div>
                    {selections.tanning_ledge && selections.lounger_count > 0 && (
                        <div className="review-item">
                            <span className="label">Ledge Loungers</span>
                            <span className="value">{selections.lounger_count}</span>
                        </div>
                    )}
                    <div className="review-item">
                        <span className="label">Attached Spa</span>
                        <span className="value">{selections.attached_spa ? 'Yes' : 'No'}</span>
                    </div>
                </div>

                {/* Deck */}
                <div className="review-section">
                    <h3 className="review-section-title">Deck</h3>
                    <div className="review-item">
                        <span className="label">Material</span>
                        <span className="value">{DECK_MATERIALS[selections.deck_material] || selections.deck_material}</span>
                    </div>
                    <div className="review-item">
                        <span className="label">Color</span>
                        <span className="value">{DECK_COLORS[selections.deck_color] || selections.deck_color}</span>
                    </div>
                </div>

                {/* Water Features */}
                {selections.water_features && selections.water_features.length > 0 && (
                    <div className="review-section">
                        <h3 className="review-section-title">Water Features</h3>
                        {selections.water_features.map((featureId) => (
                            <div className="review-item" key={featureId}>
                                <span className="label">Feature</span>
                                <span className="value">{WATER_FEATURES[featureId] || featureId}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Finishing Touches */}
                {hasFinishingTouches && (
                    <div className="review-section">
                        <h3 className="review-section-title">Finishing Touches</h3>
                        {selections.lighting !== 'none' && (
                            <div className="review-item">
                                <span className="label">Lighting</span>
                                <span className="value">{LIGHTING_OPTIONS[selections.lighting]}</span>
                            </div>
                        )}
                        {selections.landscaping !== 'none' && (
                            <div className="review-item">
                                <span className="label">Landscaping</span>
                                <span className="value">{LANDSCAPING_OPTIONS[selections.landscaping]}</span>
                            </div>
                        )}
                        {selections.furniture !== 'none' && (
                            <div className="review-item">
                                <span className="label">Furniture</span>
                                <span className="value">{FURNITURE_OPTIONS[selections.furniture]}</span>
                            </div>
                        )}
                    </div>
                )}

                {/* Uploaded Image */}
                <div className="review-section">
                    <h3 className="review-section-title">Your Image</h3>
                    <div className="review-item">
                        <span className="label">File</span>
                        <span className="value">{formData.image ? formData.image.name : 'None'}</span>
                    </div>
                    {formData.imagePreview && (
                        <div className="review-image-preview">
                            <img src={formData.imagePreview} alt="Your backyard" />
                        </div>
                    )}
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-submit"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                >
                    {isSubmitting ? (
                        <>Processing...</>
                    ) : (
                        <>Generate Visualization <Droplets size={18} /></>
                    )}
                </button>
            </div>
        </div>
    );
};

export default Step5Review;
