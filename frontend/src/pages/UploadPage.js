import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import PoolSizeShapeStep from '../components/UploadWizard/PoolSizeShapeStep';
import FinishBuiltInsStep from '../components/UploadWizard/FinishBuiltInsStep';
import DeckStep from '../components/UploadWizard/DeckStep';
import WaterFeaturesStep from '../components/UploadWizard/WaterFeaturesStep';
import FinishingStep from '../components/UploadWizard/FinishingStep';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const UploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    image: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  // Use store selections - all step components write to this
  const { selections } = useVisualizationStore();

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();
      // Include selections data
      const selectionsPayload = {
        size: selections.size,
        shape: selections.shape,
        finish: selections.finish,
        tanning_ledge: selections.tanning_ledge,
        lounger_count: selections.lounger_count,
        attached_spa: selections.attached_spa,
        deck_material: selections.deck_material,
        deck_color: selections.deck_color,
        water_features: selections.water_features,
        lighting: selections.lighting,
        landscaping: selections.landscaping,
        furniture: selections.furniture,
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
          <div
            className="progress-fill"
            style={{ width: `${((step - 1) / 6) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4, 5, 6, 7].map(s => (
            <div
              key={s}
              className={`step-dot ${s <= step ? 'active' : ''} ${s === step ? 'current' : ''}`}
            >
              {s < step ? <Check size={12} /> : s}
            </div>
          ))}
        </div>
      </div>

      {step === 1 && (
        <PoolSizeShapeStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 2 && (
        <FinishBuiltInsStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 3 && (
        <DeckStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 4 && (
        <WaterFeaturesStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 5 && (
        <FinishingStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 6 && (
        <Step4Upload
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 7 && (
        <Step5Review
          formData={formData}
          selections={selections}
          prevStep={prevStep}
          handleSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
      )}
    </div>
  );
};

export default UploadPage;
