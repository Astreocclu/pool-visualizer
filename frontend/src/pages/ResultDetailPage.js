import { useState, useEffect, useCallback, useRef } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { Shield, Download } from 'lucide-react';
import {
  getVisualizationRequestById,
  regenerateVisualizationRequest,
  getAuditReport
} from '../services/api';
import { getTenantContent } from '../content';
import './ResultDetailPage.css';

import Skeleton from '../components/Common/Skeleton';
import ProcessingScreen from '../components/ProcessingScreen';
import LeadCaptureModal from '../components/LeadCaptureModal';

const ResultDetailPage = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();

  const [request, setRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true);
  const [auditReport, setAuditReport] = useState(null);
  const [showLeadModal, setShowLeadModal] = useState(false);
  const [content, setContent] = useState(null);

  // Detect sales rep mode
  const isSalesRep = searchParams.get('rep') === 'true';

  const pollFailCountRef = useRef(0);

  const fetchRequestDetails = useCallback(async () => {
    try {
      const data = await getVisualizationRequestById(id);
      setRequest(data);
      setError(null);
      pollFailCountRef.current = 0; // Reset on success

      // Successfully fetched - can stop showing loading
      if (!isRegenerating) {
        setIsLoading(false);
      }

      // Load tenant-specific content
      if (data.tenant_id) {
        setContent(getTenantContent(data.tenant_id));
      }

      if (data.status === 'complete' || data.status === 'failed') {
        setIsRegenerating(false);

        // Fetch audit report if complete
        if (data.status === 'complete' && !auditReport) {
          try {
            const audit = await getAuditReport(id);
            setAuditReport(audit);
          } catch (auditErr) {
            // Audit may not exist yet, that's OK
            console.log('Audit not available:', auditErr);
          }
        }

        return true; // Stop polling
      }
    } catch (err) {
      console.error(`Error fetching visualization request #${id}:`, err);

      // Track consecutive failures
      pollFailCountRef.current += 1;

      // After 3 consecutive failures, stop polling and show error
      if (pollFailCountRef.current >= 3) {
        if (err.status === 401 || err.response?.status === 401) {
          setError('Session expired. Please refresh the page and log in again.');
        } else if (err.status === 404 || err.response?.status === 404) {
          setError(`Visualization request #${id} not found.`);
        } else {
          setError('Connection lost. Please refresh the page.');
        }
        setIsLoading(false);
        return true; // Stop polling on persistent errors
      }
      // Don't set isLoading=false on transient errors - keep skeleton visible while polling retries
    }
    return false; // Continue polling
  }, [id, isRegenerating, auditReport]);

  useEffect(() => {
    fetchRequestDetails();

    const pollInterval = setInterval(async () => {
      const shouldStop = await fetchRequestDetails();
      if (shouldStop) {
        clearInterval(pollInterval);
      }
    }, 3000);

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [fetchRequestDetails]);

  const handleRegenerate = async () => {
    try {
      setIsRegenerating(true);
      await regenerateVisualizationRequest(id);
      // Polling will pick up the status change
    } catch (err) {
      console.error('Failed to regenerate:', err);
      setError('Failed to start regeneration. Please try again.');
      setIsRegenerating(false);
    }
  };

  if (isLoading && !request) {
    return (
      <div className="result-detail-page">
        <div className="result-header">
          <div>
            <Skeleton variant="text" width={200} height={32} style={{ marginBottom: '10px' }} />
            <Skeleton variant="text" width={150} />
          </div>
          <Skeleton variant="rectangular" width={100} height={30} style={{ borderRadius: '15px' }} />
        </div>

        <div className="comparison-slider-container" style={{ backgroundColor: '#f0f0f0', border: 'none' }}>
          <Skeleton variant="rectangular" width="100%" height="100%" animation="wave" />
        </div>

        <div className="action-bar">
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-detail-page error">
        <h1>Error</h1>
        <div className="error-message">{error}</div>
        <Link to="/results" className="btn btn-secondary">Back to Results</Link>
      </div>
    );
  }

  // Guard against null request - show skeleton as fallback (should not normally reach here)
  if (!request) {
    return (
      <div className="result-detail-page">
        <div className="result-header">
          <div>
            <Skeleton variant="text" width={200} height={32} style={{ marginBottom: '10px' }} />
            <Skeleton variant="text" width={150} />
          </div>
          <Skeleton variant="rectangular" width={100} height={30} style={{ borderRadius: '15px' }} />
        </div>
        <div className="comparison-slider-container" style={{ backgroundColor: '#f0f0f0', border: 'none' }}>
          <Skeleton variant="rectangular" width="100%" height="100%" animation="wave" />
        </div>
        <div className="action-bar">
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
        </div>
      </div>
    );
  }

  const resultImage = request.results && request.results.length > 0 ? request.results[0] : null;
  const resultImageUrl = resultImage ? resultImage.generated_image_url : null;

  const currentProgress = request?.progress_percentage || 0;
  const currentStatusMessage = request?.status_message || '';

  // Show ProcessingScreen for pending/processing/failed states (failed has nice error UI)
  const showProcessingScreen = isRegenerating ||
    request.status === 'processing' ||
    request.status === 'pending' ||
    (request.status === 'failed' && !resultImageUrl);

  if (showProcessingScreen) {
    return (
      <ProcessingScreen
        visualizationId={id}
        originalImageUrl={request.clean_image_url || request.original_image_url}
        backendProgress={currentProgress}
        statusMessage={currentStatusMessage}
        status={request.status}
        onRetry={handleRegenerate}
      />
    );
  }

  // Get vulnerability count from audit
  const vulnerabilityCount = auditReport?.vulnerabilities?.length || 0;

  return (
    <div className="result-detail-page">
      <div className="result-header">
        <div>
          <h2>Visualization #{id}</h2>
          <span className="text-muted">{new Date(request.created_at).toLocaleString()}</span>
        </div>
        <div className={`status-badge status-${request.status}`}>
          {request.status}
        </div>
      </div>

      <div className="comparison-slider-container">
        {/* Press to Reveal Mode */}
        <div className="magic-flip-container">
          <div className={`image-layer ${showOriginal ? 'visible' : 'hidden'}`}>
            <img src={request.clean_image_url || request.original_image_url} alt="Original" />
            <span className="label before-label">Original</span>
          </div>
          <div className={`image-layer ${!showOriginal ? 'visible' : 'hidden'}`}>
            {resultImageUrl ? (
              <img src={resultImageUrl} alt="With Pool" />
            ) : (
              <div className="placeholder-image">Processing...</div>
            )}
            <span className="label after-label">{content?.results?.afterLabel || 'After'}</span>
          </div>

          <div className="toggle-button-container">
            <button
              className={`btn-toggle-view ${!showOriginal ? 'active' : ''}`}
              onClick={() => setShowOriginal(!showOriginal)}
            >
              {showOriginal ? (content?.results?.toggleShowResult || 'Show Result') : (content?.results?.toggleShowOriginal || 'Show Original')}
            </button>
          </div>
        </div>
      </div>

      {/* AI Enhancement Disclaimer */}
      {request.status === 'complete' && (
        <p className="ai-disclaimer">
          {content?.results?.aiDisclaimer || 'AI-enhanced visualization. Actual appearance may vary.'}
        </p>
      )}

      {/* Quote & Report CTA */}
      {request.status === 'complete' && (
        <div className="security-report-teaser">
          <div className="teaser-content">
            <Shield size={32} className="teaser-icon" />
            <div className="teaser-text">
              <h3>Your Quote & Review is Ready</h3>
              <p>
                We've generated a personalized quote and detailed review for you in a free PDF.
              </p>
            </div>
          </div>
          <button
            className="btn-download-report"
            onClick={() => {
              if (isSalesRep) {
                // Sales reps skip lead capture, go direct to PDF
                window.open(`/api/visualization/${id}/pdf/`, '_blank');
              } else {
                setShowLeadModal(true);
              }
            }}
          >
            <Download size={20} />
            Get Your Free Quote & Review
          </button>
        </div>
      )}

      {/* Pricing hidden - included in PDF only */}

      <div className="action-bar">
        <Link to="/results" className="btn btn-secondary">
          ← Back to Gallery
        </Link>

        <button onClick={handleRegenerate} className="btn btn-regenerate" disabled={isRegenerating}>
          ↻ Regenerate
        </button>

        <Link to="/upload" className="btn btn-primary">
          + New Upload
        </Link>
      </div>

      {/* Lead Capture Modal */}
      <LeadCaptureModal
        isOpen={showLeadModal}
        onClose={() => setShowLeadModal(false)}
        visualizationId={id}
        isSalesRep={isSalesRep}
      />
    </div>
  );
};

export default ResultDetailPage;
