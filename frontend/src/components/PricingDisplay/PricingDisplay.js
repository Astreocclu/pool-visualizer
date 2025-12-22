import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Calculator, FileText } from 'lucide-react';
import './PricingDisplay.css';

const PricingDisplay = ({ priceData, onSaveQuote, onContactSales }) => {
  const [showBreakdown, setShowBreakdown] = useState(false);

  if (!priceData) {
    return null;
  }

  const formatCurrency = (value) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  return (
    <div className="pricing-card">
      {/* Header */}
      <div className="pricing-header">
        <div className="pricing-title">
          <Calculator size={20} />
          <h3>Estimated Cost</h3>
        </div>
        <span className={`pricing-badge ${priceData.type}`}>
          {priceData.type === 'estimate' ? 'Estimate' : 'Quote'}
        </span>
      </div>

      {/* Total Price */}
      <div className="pricing-total">
        <span className="total-amount">{formatCurrency(priceData.total)}</span>
        <button
          className="breakdown-toggle"
          onClick={() => setShowBreakdown(!showBreakdown)}
        >
          {showBreakdown ? 'Hide' : 'Show'} Details
          {showBreakdown ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Itemized Breakdown */}
      {showBreakdown && (
        <div className="pricing-breakdown">
          <div className="line-items">
            {priceData.line_items?.map((item, index) => (
              <div key={index} className="line-item">
                <div className="item-info">
                  <span className="item-name">{item.name}</span>
                  {item.description && (
                    <span className="item-description">{item.description}</span>
                  )}
                </div>
                <span className="item-total">{formatCurrency(item.total)}</span>
              </div>
            ))}
          </div>

          <div className="pricing-subtotals">
            <div className="subtotal-row">
              <span>Subtotal</span>
              <span>{formatCurrency(priceData.subtotal)}</span>
            </div>
            <div className="subtotal-row">
              <span>Overhead & Fees</span>
              <span>{formatCurrency(priceData.overhead)}</span>
            </div>
            <div className="subtotal-row">
              <span>Tax</span>
              <span>{formatCurrency(priceData.tax)}</span>
            </div>
            <div className="subtotal-row total">
              <span>Total</span>
              <span>{formatCurrency(priceData.total)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="pricing-actions">
        <button className="btn-primary" onClick={onSaveQuote}>
          <FileText size={16} />
          Save Quote
        </button>
        <button className="btn-secondary" onClick={onContactSales}>
          Contact Sales
        </button>
      </div>

      {/* Disclaimer */}
      <p className="pricing-disclaimer">
        * Estimate valid for 30 days. Final quote subject to site inspection.
      </p>
    </div>
  );
};

export default PricingDisplay;
