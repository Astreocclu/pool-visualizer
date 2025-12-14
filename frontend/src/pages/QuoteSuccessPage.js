import { Link, useLocation } from 'react-router-dom';
import { Mail, ArrowLeft, Waves, CheckCircle } from 'lucide-react';
import './QuoteSuccessPage.css';

const QuoteSuccessPage = () => {
  const location = useLocation();
  const { afterImageUrl } = location.state || {};

  const quoteDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const quoteNumber = `POOL-${Math.floor(1000 + Math.random() * 9000)}`;

  return (
    <div className="quote-page">
      {/* Digital Paper Document */}
      <div className="quote-document">
        {/* Document Header */}
        <header className="doc-header">
          <div className="doc-header-left">
            <Waves className="doc-logo-icon" size={32} />
            <div className="doc-brand">
              <span className="doc-brand-name">POOL</span>
              <span className="doc-brand-tagline">Visualizer AI</span>
            </div>
          </div>
          <div className="doc-header-right">
            <h1 className="doc-title">POOL DESIGN PROPOSAL</h1>
            <p className="doc-number">#{quoteNumber}</p>
          </div>
        </header>

        {/* Document Body */}
        <div className="doc-body">
          {/* Client & Quote Info Row */}
          <div className="doc-info-row">
            <div className="doc-info-block">
              <h3>Client Details</h3>
              <p className="client-name">John & Sarah Mitchell</p>
              <p className="client-address">
                4521 Willow Creek Drive<br />
                Dallas, TX 75201
              </p>
            </div>
            <div className="doc-info-block">
              <h3>Proposal Information</h3>
              <p><strong>Date:</strong> {quoteDate}</p>
              <p><strong>Valid Until:</strong> 30 Days</p>
              <p><strong>Designer:</strong> Pool Visualizer AI</p>
            </div>
          </div>

          {/* Visual Verification */}
          {afterImageUrl && (
            <div className="visual-verification">
              <h3>Design Visualization</h3>
              <div className="verification-image-wrapper">
                <img src={afterImageUrl} alt="Pool Design Preview" />
                <div className="verification-label">
                  <CheckCircle size={14} />
                  AI-Generated Preview
                </div>
              </div>
            </div>
          )}

          {/* Pool Specs */}
          <div className="specs-section">
            <h3>Pool Design Specifications</h3>
            <table className="specs-table">
              <tbody>
                <tr>
                  <td className="spec-label">Pool Size</td>
                  <td className="spec-value">Classic (15' x 30')</td>
                </tr>
                <tr>
                  <td className="spec-label">Interior Finish</td>
                  <td className="spec-value">Pebble Blue</td>
                </tr>
                <tr>
                  <td className="spec-label">Deck Material</td>
                  <td className="spec-value">Travertine - Cream</td>
                </tr>
                <tr>
                  <td className="spec-label">Features</td>
                  <td className="spec-value">Tanning Ledge, LED Lighting</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Estimated Costs */}
          <div className="costs-section">
            <h3>Estimated Investment</h3>
            <div className="cost-items">
              <div className="cost-line">
                <span className="cost-description">Pool Construction (15' x 30')</span>
                <span className="cost-dots" />
                <span className="cost-amount">$55,000.00</span>
              </div>
              <div className="cost-line">
                <span className="cost-description">Travertine Deck (400 sq ft)</span>
                <span className="cost-dots" />
                <span className="cost-amount">$12,000.00</span>
              </div>
              <div className="cost-line">
                <span className="cost-description">Tanning Ledge with Loungers</span>
                <span className="cost-dots" />
                <span className="cost-amount">$4,500.00</span>
              </div>
              <div className="cost-line sub-item">
                <span className="cost-description">LED Pool Lighting Package</span>
                <span className="cost-dots" />
                <span className="cost-amount">$2,500.00</span>
              </div>
            </div>

            <div className="cost-total">
              <span className="total-label">Estimated Total</span>
              <span className="total-amount">$74,000.00</span>
            </div>
          </div>

          {/* Footer Note */}
          <div className="doc-footer-note">
            <p>
              This visualization is for planning purposes only. Final pricing will be determined
              by your selected pool contractor after site survey. Actual costs may vary based on
              soil conditions, access, permits, and material selections.
            </p>
          </div>
        </div>

        {/* Document Footer */}
        <footer className="doc-footer">
          <div className="footer-contact">
            <p>Pool Visualizer AI | Powered by Advanced AI</p>
            <p>Helping you envision your perfect backyard</p>
          </div>
        </footer>
      </div>

      {/* Action Buttons (Outside the paper) */}
      <div className="quote-actions">
        <button className="btn-email-pdf">
          <Mail size={18} />
          EMAIL PDF TO CLIENT
        </button>
        <Link to="/" className="btn-return">
          <ArrowLeft size={18} />
          RETURN TO DASHBOARD
        </Link>
      </div>

      {/* CRM Sync Badge */}
      <div className="crm-badge">
        <span className="crm-dot" />
        Design Saved
      </div>
    </div>
  );
};

export default QuoteSuccessPage;
