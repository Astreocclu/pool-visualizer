import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import RoofMaterialStep from '../components/UploadWizard/RoofMaterialStep';
import RoofColorStep from '../components/UploadWizard/RoofColorStep';
import SolarOptionStep from '../components/UploadWizard/SolarOptionStep';
import GutterOptionStep from '../components/UploadWizard/GutterOptionStep';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const RoofsUploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ image: null });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { selections } = useVisualizationStore();

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();
      const selectionsPayload = {
        roof_material: selections.roof_material,
        roof_color: selections.roof_color,
        solar_option: selections.solar_option,
        gutter_option: selections.gutter_option,
      };
      data.append('scope', JSON.stringify(selectionsPayload));
      data.append('original_image', formData.image);
      const response = await createVisualizationRequest(data);
      navigate(`/results/${response.id}`);
    } catch (err) {
      console.error('Submit error:', err);
      const errorMsg = err.message || err.data?.detail || JSON.stringify(err.data) || 'Unknown error';
      setError(`Failed: ${errorMsg}`);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="wizard-progress-bar">
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${((step - 1) / 5) * 100}%` }} />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4, 5, 6].map(s => (
            <div key={s} className={`step-dot ${s <= step ? 'active' : ''} ${s === step ? 'current' : ''}`}>
              {s < step ? <Check size={12} /> : s}
            </div>
          ))}
        </div>
      </div>

      {step === 1 && <RoofMaterialStep nextStep={nextStep} />}
      {step === 2 && <RoofColorStep nextStep={nextStep} prevStep={prevStep} />}
      {step === 3 && <SolarOptionStep nextStep={nextStep} prevStep={prevStep} />}
      {step === 4 && <GutterOptionStep nextStep={nextStep} prevStep={prevStep} />}
      {step === 5 && <Step4Upload formData={formData} setFormData={setFormData} nextStep={nextStep} prevStep={prevStep} />}
      {step === 6 && <Step5Review formData={formData} selections={selections} prevStep={prevStep} handleSubmit={handleSubmit} isSubmitting={isSubmitting} error={error} />}
    </div>
  );
};

export default RoofsUploadPage;
