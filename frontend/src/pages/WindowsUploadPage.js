import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import ProjectTypeStep from '../components/UploadWizard/ProjectTypeStep';
import DoorTypeStep from '../components/UploadWizard/DoorTypeStep';
import WindowTypeStep from '../components/UploadWizard/WindowTypeStep';
import FrameMaterialStep from '../components/UploadWizard/FrameMaterialStep';
import GrillePatternStep from '../components/UploadWizard/GrillePatternStep';
import HardwareTrimStep from '../components/UploadWizard/HardwareTrimStep';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const WindowsUploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    image: null
  });
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
      // Include window selections data
      const selectionsPayload = {
        project_type: selections.project_type,
        door_type: selections.door_type,
        window_type: selections.window_type,
        window_style: selections.window_style,
        frame_material: selections.frame_material,
        frame_color: selections.frame_color,
        grille_pattern: selections.grille_pattern,
        glass_option: selections.glass_option,
        hardware_finish: selections.hardware_finish,
        trim_style: selections.trim_style,
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
            style={{ width: `${((step - 1) / 7) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
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
        <ProjectTypeStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 2 && (
        <DoorTypeStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 3 && (
        <WindowTypeStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 4 && (
        <FrameMaterialStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 5 && (
        <GrillePatternStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 6 && (
        <HardwareTrimStep
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 7 && (
        <Step4Upload
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 8 && (
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

export default WindowsUploadPage;
