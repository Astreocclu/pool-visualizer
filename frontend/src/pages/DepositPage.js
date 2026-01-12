import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, CreditCard, Loader2, ShieldCheck } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import { getDepositStatus, createDepositCheckout } from '../services/api';
import './DepositPage.css';

const DepositPage = () => {
  const { id } = useParams();
  const { paymentsEnabled, depositAmount } = useConfig();
  const [depositStatus, setDepositStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [leadId, setLeadId] = useState(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await getDepositStatus(id);
        setDepositStatus(data.status);
        const storedLeadId = localStorage.getItem(`lead_${id}`);
        setLeadId(storedLeadId);
      } catch (err) {
        console.error('Failed to check deposit status:', err);
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
  }, [id]);

  const handlePayDeposit = async () => {
    if (!leadId) {
      alert('Lead information not found. Please go back and submit your details again.');
      return;
    }

    setCheckoutLoading(true);
    try {
      const data = await createDepositCheckout(leadId, id);
      window.location.href = data.checkout_url;
    } catch (err) {
      console.error('Failed to create checkout:', err);
      alert('Failed to start payment. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="deposit-page loading">
        <Loader2 className="spinner" size={48} />
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="deposit-page">
      <div className="deposit-card">
        <div className="download-complete">
          <CheckCircle size={48} className="success-icon" />
          <h1>Your Quote is Ready!</h1>
          <p>Your personalized pool design proposal has been downloaded.</p>
        </div>

        {paymentsEnabled && depositStatus !== 'paid' && (
          <div className="deposit-cta">
            <div className="cta-header">
              <ShieldCheck size={32} className="cta-icon" />
              <h2>Secure Your Project</h2>
            </div>

            <p className="cta-description">
              Pay a <strong>${depositAmount}</strong> refundable deposit to lock in your design
              and get matched with a verified pool contractor in your area.
            </p>

            <ul className="cta-benefits">
              <li><CheckCircle size={16} />Deposit applies as credit toward your project</li>
              <li><CheckCircle size={16} />Priority matching with verified contractors</li>
              <li><CheckCircle size={16} />100% refundable if you change your mind</li>
            </ul>

            <button
              className="btn-pay-deposit"
              onClick={handlePayDeposit}
              disabled={checkoutLoading}
            >
              {checkoutLoading ? (
                <><Loader2 size={20} className="spinner" />Redirecting to Secure Payment...</>
              ) : (
                <><CreditCard size={20} />Pay ${depositAmount} Deposit</>
              )}
            </button>

            <p className="payment-note">
              Secure payment powered by Stripe. Your card details are never stored on our servers.
            </p>
          </div>
        )}

        {depositStatus === 'paid' && (
          <div className="deposit-confirmed">
            <CheckCircle size={48} className="confirmed-icon" />
            <h2>Deposit Confirmed!</h2>
            <p>A verified contractor will contact you within 24-48 hours to discuss your project.</p>
          </div>
        )}

        <div className="deposit-actions">
          <Link to={`/results/${id}`} className="btn-back">Back to Visualization</Link>
          <Link to="/" className="btn-home">Return to Dashboard</Link>
        </div>
      </div>
    </div>
  );
};

export default DepositPage;
