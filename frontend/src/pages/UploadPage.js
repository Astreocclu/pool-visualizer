import React, { useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import { getTenantConfig, isValidTenant } from '../config/tenants';

// Pool steps
import PoolSizeShapeStep from '../components/UploadWizard/PoolSizeShapeStep';
import FinishBuiltInsStep from '../components/UploadWizard/FinishBuiltInsStep';
import DeckStep from '../components/UploadWizard/DeckStep';
import WaterFeaturesStep from '../components/UploadWizard/WaterFeaturesStep';
import FinishingStep from '../components/UploadWizard/FinishingStep';

// Windows steps
import ProjectTypeStep from '../components/UploadWizard/ProjectTypeStep';
import DoorTypeStep from '../components/UploadWizard/DoorTypeStep';
import WindowTypeStep from '../components/UploadWizard/WindowTypeStep';
import FrameMaterialStep from '../components/UploadWizard/FrameMaterialStep';
import GrillePatternStep from '../components/UploadWizard/GrillePatternStep';
import HardwareTrimStep from '../components/UploadWizard/HardwareTrimStep';

// Roofs steps
import RoofMaterialStep from '../components/UploadWizard/RoofMaterialStep';
import RoofColorStep from '../components/UploadWizard/RoofColorStep';
import SolarOptionStep from '../components/UploadWizard/SolarOptionStep';
import GutterOptionStep from '../components/UploadWizard/GutterOptionStep';

// Shared steps
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';

import './UploadPage.css';

// Component registry - maps component names to actual components
const STEP_COMPONENTS = {
  PoolSizeShapeStep,
  FinishBuiltInsStep,
  DeckStep,
  WaterFeaturesStep,
  FinishingStep,
  ProjectTypeStep,
  DoorTypeStep,
  WindowTypeStep,
  FrameMaterialStep,
  GrillePatternStep,
  HardwareTrimStep,
  RoofMaterialStep,
  RoofColorStep,
  SolarOptionStep,
  GutterOptionStep,
  Step4Upload,
  Step5Review,
};

const UploadPage = () => {
  const { tenantId = 'pools' } = useParams();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ image: null });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { selections } = useVisualizationStore();

  // Get tenant configuration
  const tenantConfig = useMemo(() => getTenantConfig(tenantId), [tenantId]);
  const steps = tenantConfig.steps;
  const totalSteps = steps.length;

  // Redirect if invalid tenant
  if (!isValidTenant(tenantId)) {
    navigate('/upload/pools');
    return null;
  }

  const nextStep = () => setStep(prev => Math.min(prev + 1, totalSteps));
  const prevStep = () => setStep(prev => Math.max(prev - 1, 1));

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();

      // Build selections payload from tenant-specific keys
      const selectionsPayload = {};
      tenantConfig.selectionsKeys.forEach(key => {
        if (selections[key] !== undefined) {
          selectionsPayload[key] = selections[key];
        }
      });

      data.append('scope', JSON.stringify(selectionsPayload));
      data.append('tenant_id', tenantId);  // CRITICAL: Send tenant_id
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

  // Render current step component
  const renderStep = () => {
    const stepConfig = steps[step - 1];
    const StepComponent = STEP_COMPONENTS[stepConfig.component];

    if (!StepComponent) {
      return <div>Unknown step: {stepConfig.component}</div>;
    }

    // Shared props for all steps
    const stepProps = {
      nextStep,
      prevStep,
    };

    // Special props for specific steps
    if (stepConfig.component === 'Step4Upload') {
      return (
        <StepComponent
          {...stepProps}
          formData={formData}
          setFormData={setFormData}
        />
      );
    }

    if (stepConfig.component === 'Step5Review') {
      return (
        <StepComponent
          {...stepProps}
          formData={formData}
          selections={selections}
          handleSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
      );
    }

    return <StepComponent {...stepProps} />;
  };

  return (
    <div className="upload-page">
      {/* Tenant header */}
      <div className="tenant-header">
        <h1>{tenantConfig.name}</h1>
        <p>{tenantConfig.description}</p>
      </div>

      {/* Progress bar */}
      <div className="wizard-progress-bar">
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {steps.map((s, idx) => (
            <div
              key={idx}
              className={`step-dot ${idx + 1 <= step ? 'active' : ''} ${idx + 1 === step ? 'current' : ''}`}
              title={s.label}
            >
              {idx + 1 < step ? <Check size={12} /> : idx + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Current step */}
      {renderStep()}
    </div>
  );
};

export default UploadPage;
