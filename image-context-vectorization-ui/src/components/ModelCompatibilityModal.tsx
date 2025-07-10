import React, { useState } from 'react';
import './ModelCompatibilityModal.css';

interface ModelInfo {
  name: string;
  dimension: number;
}

interface ModelCompatibilityModalProps {
  isVisible: boolean;
  message: string;
  currentModel?: ModelInfo;
  newModel?: ModelInfo;
  onConfirmClear: () => Promise<void>;
}

const ModelCompatibilityModal: React.FC<ModelCompatibilityModalProps> = ({
  isVisible,
  message,
  currentModel,
  newModel,
  onConfirmClear
}) => {
  const [isClearing, setIsClearing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClearDatabase = async () => {
    setIsClearing(true);
    setError(null);
    
    try {
      await onConfirmClear();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear database');
      setIsClearing(false);
    }
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="model-compatibility-modal-overlay">
      <div className="model-compatibility-modal">
        <div className="modal-header">
          <h2>🔄 Model Configuration Changed</h2>
          <p className="modal-subtitle">Database compatibility check required</p>
        </div>

        <div className="modal-content">
          <div className="compatibility-message">
            <p><strong>Issue:</strong> {message}</p>
          </div>

          {currentModel && newModel && (
            <div className="model-comparison">
              <div className="model-info current-model">
                <h3>Previous Model</h3>
                <div className="model-details">
                  <p><strong>Name:</strong> {currentModel.name}</p>
                  <p><strong>Dimensions:</strong> {currentModel.dimension}</p>
                </div>
              </div>

              <div className="arrow">→</div>

              <div className="model-info new-model">
                <h3>New Model</h3>
                <div className="model-details">
                  <p><strong>Name:</strong> {newModel.name}</p>
                  <p><strong>Dimensions:</strong> {newModel.dimension}</p>
                </div>
              </div>
            </div>
          )}

          <div className="warning-section">
            <div className="warning-icon">⚠️</div>
            <div className="warning-text">
              <h4>Action Required</h4>
              <p>
                The embedding dimensions of your sentence transformer model have changed. 
                This requires clearing the existing database to prevent compatibility errors.
              </p>
              <p><strong>All existing image data will be lost.</strong></p>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">❌</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="modal-actions">
          <button
            className="clear-database-btn"
            onClick={handleClearDatabase}
            disabled={isClearing}
          >
            {isClearing ? (
              <>
                <span className="spinner"></span>
                Clearing Database...
              </>
            ) : (
              'Clear Database & Continue'
            )}
          </button>
          
          <p className="action-note">
            You must clear the database to continue using the application.
            There is no option to cancel this action.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ModelCompatibilityModal;