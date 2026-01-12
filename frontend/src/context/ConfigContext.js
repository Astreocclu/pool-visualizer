import { createContext, useContext, useState, useEffect } from 'react';
import { getConfig } from '../services/api';

const ConfigContext = createContext(null);

export function ConfigProvider({ children }) {
  const [config, setConfig] = useState({
    paymentsEnabled: false,
    stripePublicKey: null,
    depositAmount: 500,
    subscriptionAmount: 100,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await getConfig();
        setConfig({
          paymentsEnabled: data.payments_enabled,
          stripePublicKey: data.stripe_public_key,
          depositAmount: data.deposit_amount,
          subscriptionAmount: data.subscription_amount,
          loading: false,
          error: null,
        });
      } catch (err) {
        console.error('Failed to fetch config:', err);
        setConfig(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to load configuration',
        }));
      }
    };

    fetchConfig();
  }, []);

  return (
    <ConfigContext.Provider value={config}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within ConfigProvider');
  }
  return context;
}
