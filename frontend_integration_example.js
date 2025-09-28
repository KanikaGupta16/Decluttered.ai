/**
 * Frontend Integration Example for Decluttered.ai Web API
 *
 * This example shows how to integrate the backend API with your Next.js frontend
 * Copy these functions into your frontend components
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8006';

// Utility function for API requests
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Health check function
export async function checkAPIHealth() {
  try {
    const health = await apiRequest('/health');
    return health;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
}

// File upload function
export async function uploadFiles(files) {
  const formData = new FormData();

  // Add all files to form data
  Array.from(files).forEach(file => {
    formData.append('files', file);
  });

  try {
    const result = await apiRequest('/upload', {
      method: 'POST',
      body: formData,
    });

    return result;
  } catch (error) {
    console.error('File upload failed:', error);
    throw error;
  }
}

// Session status monitoring
export async function getSessionStatus(sessionId) {
  try {
    const status = await apiRequest(`/session/${sessionId}`);
    return status;
  } catch (error) {
    console.error('Failed to get session status:', error);
    throw error;
  }
}

// Get processing results
export async function getSessionResults(sessionId) {
  try {
    const results = await apiRequest(`/session/${sessionId}/results`);
    return results;
  } catch (error) {
    console.error('Failed to get session results:', error);
    throw error;
  }
}

// Poll for completion with automatic retry
export async function pollForCompletion(sessionId, maxWaitTime = 300000, pollInterval = 3000) {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getSessionStatus(sessionId);

        if (status.status === 'completed') {
          const results = await getSessionResults(sessionId);
          resolve(results);
          return;
        }

        if (status.status === 'failed') {
          reject(new Error(status.error_message || 'Processing failed'));
          return;
        }

        // Check timeout
        if (Date.now() - startTime > maxWaitTime) {
          reject(new Error('Timeout waiting for processing to complete'));
          return;
        }

        // Continue polling
        setTimeout(poll, pollInterval);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

// React Hook for file processing
export function useDeclutteredAI() {
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [error, setError] = useState(null);

  const processFiles = async (files) => {
    try {
      setError(null);
      setIsUploading(true);

      // Upload files
      const uploadResult = await uploadFiles(files);
      setCurrentSessionId(uploadResult.session_id);
      setIsUploading(false);
      setIsProcessing(true);

      // Wait for completion
      const results = await pollForCompletion(uploadResult.session_id);
      setIsProcessing(false);

      return {
        sessionId: uploadResult.session_id,
        results,
      };
    } catch (err) {
      setError(err.message);
      setIsUploading(false);
      setIsProcessing(false);
      throw err;
    }
  };

  const reset = () => {
    setIsUploading(false);
    setIsProcessing(false);
    setCurrentSessionId(null);
    setError(null);
  };

  return {
    processFiles,
    reset,
    isUploading,
    isProcessing,
    currentSessionId,
    error,
  };
}

// React Component Example
export function FileUploadComponent() {
  const { processFiles, isUploading, isProcessing, error } = useDeclutteredAI();
  const [results, setResults] = useState(null);

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    try {
      const result = await processFiles(files);
      setResults(result.results);
    } catch (err) {
      console.error('Processing failed:', err);
    }
  };

  return (
    <div className="upload-component">
      <div className="upload-area">
        <input
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={handleFileUpload}
          disabled={isUploading || isProcessing}
        />

        {isUploading && <p>Uploading files...</p>}
        {isProcessing && <p>Processing with AI agents...</p>}
        {error && <p className="error">Error: {error}</p>}
      </div>

      {results && (
        <div className="results">
          <h3>Processing Results</h3>

          <div className="analysis-report">
            <h4>Analysis Report</h4>
            <pre>{results.analysis_report}</pre>
          </div>

          {results.cropped_objects.length > 0 && (
            <div className="cropped-objects">
              <h4>Resellable Items Found</h4>
              <div className="object-grid">
                {results.cropped_objects.map((obj, index) => (
                  <div key={index} className="object-item">
                    <img
                      src={`${API_BASE_URL}${obj.download_url}`}
                      alt={obj.filename}
                      className="object-image"
                    />
                    <p>{obj.filename}</p>
                    <p>{(obj.size / 1024).toFixed(1)} KB</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// CSS Styles (add to your CSS file)
const styles = `
.upload-component {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 10px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
}

.upload-area input[type="file"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.upload-area input[type="file"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
  font-weight: bold;
}

.results {
  margin-top: 20px;
}

.analysis-report pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.object-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 10px;
}

.object-item {
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
}

.object-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 5px;
}
`;

// Integration with your existing Next.js pages
export function integrateWithDashboard() {
  // Add this to your dashboard page.tsx file:

  /*
  import { FileUploadComponent } from '@/components/FileUpload';

  // In your dashboard component, add:
  <div className="upload-section">
    <h2>Upload Images or Videos</h2>
    <FileUploadComponent />
  </div>
  */
}

// Advanced usage with progress tracking
export async function uploadWithProgress(files, onProgress) {
  const formData = new FormData();
  Array.from(files).forEach(file => formData.append('files', file));

  const xhr = new XMLHttpRequest();

  return new Promise((resolve, reject) => {
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        onProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed'));
    });

    xhr.open('POST', `${API_BASE_URL}/upload`);
    xhr.send(formData);
  });
}

export default {
  checkAPIHealth,
  uploadFiles,
  getSessionStatus,
  getSessionResults,
  pollForCompletion,
  useDeclutteredAI,
  FileUploadComponent,
  uploadWithProgress,
};