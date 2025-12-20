import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  fetchVisualizationRequests,
  createVisualizationRequest,
  fetchScreenTypes,
  deleteVisualizationRequest,
  retryVisualizationRequest
} from '../services/api';

// Helper function for safe localStorage access
const safeLocalStorage = {
  getItem: (key) => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  setItem: (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Silently fail
    }
  },
  removeItem: (key) => {
    try {
      localStorage.removeItem(key);
    } catch {
      // Silently fail
    }
  }
};

const initialState = {
  requests: [],
  screenTypes: [],
  isLoading: false,
  error: null,
  selectedRequest: null,
  filters: {
    status: 'all',
    screenType: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc'
  },
  pagination: {
    page: 1,
    pageSize: 20,
    total: 0,
    hasNext: false,
    hasPrev: false
  },
  selections: {
    // === POOLS SELECTIONS (existing - keep these) ===
    // Screen 1: Size & Shape
    size: 'classic',
    shape: 'rectangle',

    // Screen 2: Finish & Built-ins
    finish: 'pebble_blue',
    tanning_ledge: true,
    lounger_count: 2,
    attached_spa: false,

    // Screen 3: Deck
    deck_material: 'travertine',
    deck_color: 'cream',

    // Screen 4: Water Features
    water_features: [],  // Array of feature IDs, max 2

    // Screen 5: Finishing Touches
    lighting: 'none',
    landscaping: 'none',
    furniture: 'none',

    // === WINDOWS SELECTIONS (add these) ===
    window_type: 'double_hung',
    window_style: 'traditional',
    frame_material: 'vinyl',
    frame_color: 'white',
    grille_pattern: 'none',
    glass_option: 'clear',
    hardware_finish: 'white',
    trim_style: 'standard',
    project_type: null,
    door_type: null,

    // === ROOFS SELECTIONS ===
    roof_material: null,
    roof_color: null,
    solar_option: null,
    gutter_option: null,
  }
};

const useVisualizationStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Actions
      fetchRequests: async (options = {}) => {
        const state = get();
        const { page = 1, pageSize = 20, ...filters } = options;

        set({ isLoading: true, error: null });

        try {
          const response = await fetchVisualizationRequests({
            page,
            page_size: pageSize,
            ...state.filters,
            ...filters
          });

          const requests = response.results || response;
          const isArray = Array.isArray(requests);

          set({
            requests: isArray ? requests : [requests],
            isLoading: false,
            pagination: {
              page,
              pageSize,
              total: response.count || (isArray ? requests.length : 1),
              hasNext: !!response.next,
              hasPrev: !!response.previous
            }
          });

          return response;
        } catch (error) {
          const errorMessage = error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            'Failed to fetch requests';

          set({
            error: errorMessage,
            isLoading: false
          });
          throw error;
        }
      },

      createRequest: async (formData) => {
        set({ isLoading: true, error: null });

        try {
          const newRequest = await createVisualizationRequest(formData);

          // Optimistic update
          set(state => ({
            requests: [newRequest, ...state.requests],
            isLoading: false,
            error: null
          }));

          return newRequest;
        } catch (error) {
          const errorMessage = error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            'Failed to create request';

          set({
            error: errorMessage,
            isLoading: false
          });
          throw error;
        }
      },

      deleteRequest: async (requestId) => {
        const state = get();
        const originalRequests = state.requests;

        // Optimistic update
        set(state => ({
          requests: state.requests.filter(req => req.id !== requestId)
        }));

        try {
          await deleteVisualizationRequest(requestId);
        } catch (error) {
          // Revert optimistic update on error
          set({ requests: originalRequests });

          const errorMessage = error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            'Failed to delete request';

          set({ error: errorMessage });
          throw error;
        }
      },

      retryRequest: async (requestId) => {
        set({ isLoading: true, error: null });

        try {
          const updatedRequest = await retryVisualizationRequest(requestId);

          // Update the request in the list
          set(state => ({
            requests: state.requests.map(req =>
              req.id === requestId ? updatedRequest : req
            ),
            isLoading: false
          }));

          return updatedRequest;
        } catch (error) {
          const errorMessage = error.response?.data?.detail ||
            error.response?.data?.message ||
            error.message ||
            'Failed to retry request';

          set({
            error: errorMessage,
            isLoading: false
          });
          throw error;
        }
      },

      fetchScreenTypes: async () => {
        try {
          const screenTypes = await fetchScreenTypes();
          set({ screenTypes });
          return screenTypes;
        } catch (error) {
          console.error('Failed to fetch screen types:', error);
          // Don't set error for screen types as it's not critical
          return [];
        }
      },

      // UI state management
      setSelectedRequest: (request) => {
        set({ selectedRequest: request });
      },

      clearSelectedRequest: () => {
        set({ selectedRequest: null });
      },

      setFilters: (newFilters) => {
        set(state => ({
          filters: { ...state.filters, ...newFilters }
        }));
      },

      clearFilters: () => {
        set({ filters: initialState.filters });
      },

      setSelection: (key, value) => {
        set(state => ({
          selections: { ...state.selections, [key]: value }
        }));
      },

      setSelections: (updates) => {
        set(state => ({
          selections: { ...state.selections, ...updates }
        }));
      },

      setProjectType: (project_type) => set({ selections: { ...get().selections, project_type } }),
      setDoorType: (door_type) => set({ selections: { ...get().selections, door_type } }),

      setRoofMaterial: (roof_material) => set({ selections: { ...get().selections, roof_material } }),
      setRoofColor: (roof_color) => set({ selections: { ...get().selections, roof_color } }),
      setSolarOption: (solar_option) => set({ selections: { ...get().selections, solar_option } }),
      setGutterOption: (gutter_option) => set({ selections: { ...get().selections, gutter_option } }),

      resetSelections: () => {
        set({ selections: initialState.selections });
      },

      clearError: () => {
        set({ error: null });
      },

      // Utility methods
      getRequestById: (id) => {
        const state = get();
        return state.requests.find(req => req.id === id);
      },

      getRequestsByStatus: (status) => {
        const state = get();
        return state.requests.filter(req => req.status === status);
      },

      getStats: () => {
        const state = get();
        const requests = state.requests;

        return {
          total: requests.length,
          pending: requests.filter(req => req.status === 'pending').length,
          processing: requests.filter(req => req.status === 'processing').length,
          completed: requests.filter(req => req.status === 'complete').length,
          failed: requests.filter(req => req.status === 'failed').length
        };
      },

      // Refresh data
      refresh: async () => {
        const state = get();
        await Promise.all([
          state.fetchRequests(),
          state.fetchScreenTypes()
        ]);
      }
    }),
    {
      name: 'visualization-storage',
      storage: createJSONStorage(() => safeLocalStorage),
      partialize: (state) => ({
        screenTypes: state.screenTypes,
        filters: state.filters
      })
    }
  )
);

export default useVisualizationStore;
