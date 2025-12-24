import React, { useCallback } from 'react';
import { ArrowLeft, ArrowRight, Camera, Sun, TreeDeciduous } from 'lucide-react';
import ImageUploader from '../Upload/ImageUploader';

const Step4Upload = ({ formData, setFormData, nextStep, prevStep }) => {
    const handleImageSelect = useCallback((file) => {
        setFormData(prev => ({ ...prev, image: file }));
    }, [setFormData]);

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Upload Your Backyard Photo</h2>
                <p className="step-subtitle">We'll visualize your new pool in this space</p>
            </div>

            {/* Photo Tips */}
            <div className="photo-tips">
                <h4>For Best Results:</h4>
                <ul className="tips-list">
                    <li><Sun size={16} /> Take photo during daylight hours</li>
                    <li><Camera size={16} /> Stand back to capture the full yard</li>
                    <li><TreeDeciduous size={16} /> Include the area where the pool will go</li>
                </ul>
            </div>

            <div className="upload-container">
                <ImageUploader
                    onImageSelect={handleImageSelect}
                    value={formData.image}
                    placeholderText="Upload a photo of your backyard"
                    hintText="Best: Wide shot showing full yard, taken in daylight"
                />
            </div>

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!formData.image}
                >
                    Review <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default Step4Upload;
