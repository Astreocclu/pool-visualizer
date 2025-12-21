/**
 * Tenant Configuration
 * Defines wizard steps and display info for each tenant (pools, windows, roofs)
 */

export const TENANT_CONFIG = {
  pools: {
    id: 'pools',
    name: 'Pool Designer',
    description: 'Design your dream swimming pool',
    steps: [
      { component: 'PoolSizeShapeStep', label: 'Size & Shape' },
      { component: 'FinishBuiltInsStep', label: 'Finish' },
      { component: 'DeckStep', label: 'Deck' },
      { component: 'WaterFeaturesStep', label: 'Water Features' },
      { component: 'FinishingStep', label: 'Finishing' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'size', 'shape', 'finish', 'tanning_ledge', 'lounger_count',
      'attached_spa', 'deck_material', 'deck_color', 'water_features',
      'lighting', 'landscaping', 'furniture'
    ],
  },
  windows: {
    id: 'windows',
    name: 'Window & Door Designer',
    description: 'Visualize new windows and doors',
    steps: [
      { component: 'ProjectTypeStep', label: 'Project Type' },
      { component: 'DoorTypeStep', label: 'Door Type' },
      { component: 'WindowTypeStep', label: 'Window Type' },
      { component: 'FrameMaterialStep', label: 'Frame' },
      { component: 'GrillePatternStep', label: 'Grilles' },
      { component: 'HardwareTrimStep', label: 'Hardware' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'project_type', 'door_type', 'window_type', 'window_style',
      'frame_material', 'frame_color', 'grille_pattern', 'glass_option',
      'hardware_finish', 'trim_style'
    ],
  },
  roofs: {
    id: 'roofs',
    name: 'Roof & Solar Designer',
    description: 'Visualize new roofing and solar panels',
    steps: [
      { component: 'RoofMaterialStep', label: 'Material' },
      { component: 'RoofColorStep', label: 'Color' },
      { component: 'SolarOptionStep', label: 'Solar' },
      { component: 'GutterOptionStep', label: 'Gutters' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'roof_material', 'roof_color', 'solar_option', 'gutter_option'
    ],
  },
};

export const getTenantConfig = (tenantId) => {
  return TENANT_CONFIG[tenantId] || TENANT_CONFIG.pools;
};

export const isValidTenant = (tenantId) => {
  return tenantId in TENANT_CONFIG;
};
