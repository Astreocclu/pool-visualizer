import { useEffect } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import './DepositPage.css';

const DepositSuccessPage = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    console.log('Payment successful, session:', sessionId);
  }, [sessionId]);

  return (
    <div className="deposit-page">
      <div className="deposit-card">
        <div className="deposit-confirmed" style={{ marginBottom: 0, padding: '40px 24px' }}>
          <CheckCircle size={64} className="confirmed-icon" />
          <h1 style={{ fontSize: '28px', color: '#166534', marginBottom: '16px' }}>
            Payment Successful!
          </h1>
          <h2 style={{ color: '#15803d', fontWeight: 'normal', marginBottom: '16px' }}>
            Your $500 deposit has been received
          </h2>
          <p style={{ color: '#166534', lineHeight: '1.6' }}>
            Thank you for securing your project! A verified pool contractor
            will contact you within 24-48 hours to discuss your design and
            schedule a site visit.
          </p>
        </div>

        <div className="deposit-actions" style={{ marginTop: '24px' }}>
          <Link to={`/results/${id}`} className="btn-back">View Your Design</Link>
          <Link to="/" className="btn-home">
            Go to Dashboard<ArrowRight size={16} style={{ marginLeft: '8px' }} />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DepositSuccessPage;
