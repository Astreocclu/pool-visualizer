import { useState, useEffect } from 'react';
import { fetchTenantConfig } from '../services/api';

/**
 * Hook to fetch and cache tenant configuration.
 * 
 * @returns {Object} { config, loading, error }
 */
export function useTenantConfig() {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check sessionStorage cache first
        const cached = sessionStorage.getItem('tenantConfig');
        if (cached) {
            try {
                setConfig(JSON.parse(cached));
                setLoading(false);
                return;
            } catch (e) {
                sessionStorage.removeItem('tenantConfig');
            }
        }

        // Fetch from API
        const fetchConfig = async () => {
            try {
                const data = await fetchTenantConfig();

                // Cache for session
                sessionStorage.setItem('tenantConfig', JSON.stringify(data));
                setConfig(data);
            } catch (err) {
                console.error('Failed to fetch tenant config:', err);
                setError(err.message || 'Failed to load configuration');

                // Fallback to hardcoded defaults (backward compatibility)
                setConfig(getDefaultConfig());
            } finally {
                setLoading(false);
            }
        };

        fetchConfig();
    }, []);

    return { config, loading, error };
}

/**
 * Fallback configuration if API fails.
 * Defaults to pools tenant configuration.
 */
function getDefaultConfig() {
    return {
        tenant_id: 'pools',
        display_name: 'Pool Visualizer AI',
        choices: {
            size: [
                ['starter', 'Starter (12x24)'],
                ['classic', 'Classic (15x30)'],
                ['family', 'Family (16x36)'],
                ['resort', 'Resort (18x40)'],
            ],
            shape: [
                ['rectangle', 'Rectangle'],
                ['roman', 'Roman'],
                ['kidney', 'Kidney'],
                ['freeform', 'Freeform'],
            ],
            finish: [
                ['white_plaster', 'White Plaster'],
                ['pebble_blue', 'Pebble Tec - Blue'],
                ['quartz_blue', 'Quartz - Ocean Blue'],
            ],
            deck_material: [
                ['travertine', 'Travertine'],
                ['pavers', 'Pavers'],
                ['stamped_concrete', 'Stamped Concrete'],
            ],
        },
    };
}

export default useTenantConfig;
