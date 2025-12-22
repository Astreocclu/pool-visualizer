/**
 * Tenant Content Loader
 * Provides tenant-specific marketing content for UI components
 */

import { isValidTenant } from '../config/tenants';

// Import all tenant content
import { poolsContent } from './pools';
import { windowsContent } from './windows';
import { roofsContent } from './roofs';

const TENANT_CONTENT = {
  pools: poolsContent,
  windows: windowsContent,
  roofs: roofsContent,
};

/**
 * Get content for a specific tenant
 * @param {string} tenantId - The tenant identifier (pools, windows, roofs)
 * @returns {object} The tenant's content object
 */
export const getTenantContent = (tenantId) => {
  const safeTenantId = isValidTenant(tenantId) ? tenantId : 'pools';
  return TENANT_CONTENT[safeTenantId] || TENANT_CONTENT.pools;
};
