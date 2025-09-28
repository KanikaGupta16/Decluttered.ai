'use client';

import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';

interface ProcessingJob {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
  results?: any;
  timestamp: string;
}

interface CroppedImage {
  filename: string;
  size: number;
  created: string;
  url: string;
}

const PipelineUpload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [processingJob, setProcessingJob] = useState<ProcessingJob | null>(null);
  const [croppedImages, setCroppedImages] = useState<CroppedImage[]>([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['facebook', 'ebay']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollInterval = useRef<NodeJS.Timeout | null>(null);

  // API base URL
  const API_BASE = 'http://localhost:3005';

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setUploadedFile(file);
        setError(null);
      } else {
        setError('Please upload an image file (PNG, JPG, GIF, etc.)');
      }
    }
  }, []);

  // File input handler
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setUploadedFile(files[0]);
      setError(null);
    }
  }, []);

  // Poll job status
  const pollJobStatus = useCallback(async (jobId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/status/${jobId}`);
      const data = await response.json();
      
      if (data.ok) {
        setProcessingJob(data);
        
        if (data.status === 'completed') {
          // Stop polling
          if (pollInterval.current) {
            clearInterval(pollInterval.current);
            pollInterval.current = null;
          }
          
          // Fetch cropped images
          fetchCroppedImages();
          
        } else if (data.status === 'error') {
          // Stop polling on error
          if (pollInterval.current) {
            clearInterval(pollInterval.current);
            pollInterval.current = null;
          }
          setError(data.message || 'Processing failed');
        }
      }
    } catch (err) {
      console.error('Error polling job status:', err);
    }
  }, []);

  // Start processing
  const startProcessing = useCallback(async () => {
    if (!uploadedFile) return;
    
    setIsLoading(true);
    setError(null);
    setProcessingJob(null);
    
    try {
      const formData = new FormData();
      formData.append('image', uploadedFile);
      selectedPlatforms.forEach(platform => {
        formData.append('platforms', platform);
      });
      
      const response = await fetch(`${API_BASE}/api/pipeline/process`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.ok) {
        setProcessingJob({
          job_id: data.job_id,
          status: data.status,
          progress: 0,
          message: data.message || 'Processing started...',
          timestamp: new Date().toISOString()
        });
        
        // Start polling for status updates
        pollInterval.current = setInterval(() => {
          pollJobStatus(data.job_id);
        }, 2000); // Poll every 2 seconds
        
      } else {
        setError(data.message || 'Failed to start processing');
      }
    } catch (err) {
      setError('Network error - make sure the API server is running on port 3005');
      console.error('Processing error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [uploadedFile, selectedPlatforms, pollJobStatus]);

  // Fetch cropped images
  const fetchCroppedImages = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/cropped-images`);
      const data = await response.json();
      
      if (data.ok) {
        setCroppedImages(data.images || []);
      }
    } catch (err) {
      console.error('Error fetching cropped images:', err);
    }
  }, []);

  // Reset form
  const resetForm = useCallback(() => {
    setUploadedFile(null);
    setProcessingJob(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (pollInterval.current) {
      clearInterval(pollInterval.current);
      pollInterval.current = null;
    }
  }, []);

  // Platform toggle
  const togglePlatform = useCallback((platform: string) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platform)) {
        return prev.filter(p => p !== platform);
      } else {
        return [...prev, platform];
      }
    });
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          🔥 Object Detection Pipeline
        </h2>
        <p className="text-gray-600">
          Upload an image to detect, identify, and list resellable objects automatically
        </p>
      </div>

      {/* Upload Area */}
      <motion.div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : uploadedFile
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        {uploadedFile ? (
          <div className="space-y-4">
            <div className="text-green-600 text-xl">✅ Image Ready</div>
            <p className="text-gray-700 font-medium">{uploadedFile.name}</p>
            <p className="text-gray-500 text-sm">
              {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
            {uploadedFile.type.startsWith('image/') && (
              <div className="mt-4">
                <img
                  src={URL.createObjectURL(uploadedFile)}
                  alt="Preview"
                  className="max-w-xs max-h-48 mx-auto rounded-lg shadow-md"
                />
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-gray-400 text-6xl">📸</div>
            <div>
              <p className="text-xl font-medium text-gray-700">
                Drop your image here or click to browse
              </p>
              <p className="text-gray-500 text-sm mt-1">
                Supports PNG, JPG, GIF, BMP, WebP (max 16MB)
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* Platform Selection */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          📋 Select Marketplaces
        </h3>
        <div className="flex gap-4">
          <motion.button
            onClick={() => togglePlatform('facebook')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
              selectedPlatforms.includes('facebook')
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            📘 Facebook Marketplace
          </motion.button>
          
          <motion.button
            onClick={() => togglePlatform('ebay')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
              selectedPlatforms.includes('ebay')
                ? 'bg-yellow-500 text-white shadow-md'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🔨 eBay
          </motion.button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center">
        <motion.button
          onClick={startProcessing}
          disabled={!uploadedFile || isLoading || (processingJob?.status === 'processing')}
          className={`px-8 py-3 rounded-lg font-semibold text-white transition-all ${
            !uploadedFile || isLoading || (processingJob?.status === 'processing')
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 shadow-lg hover:shadow-xl'
          }`}
          whileHover={{ scale: uploadedFile && !isLoading ? 1.05 : 1 }}
          whileTap={{ scale: uploadedFile && !isLoading ? 0.95 : 1 }}
        >
          {isLoading ? '🔄 Starting...' : '🚀 Start Processing'}
        </motion.button>
        
        <motion.button
          onClick={resetForm}
          className="px-6 py-3 rounded-lg font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-all"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🔄 Reset
        </motion.button>
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-red-50 border border-red-200 rounded-lg p-4"
          >
            <div className="flex items-center gap-2">
              <span className="text-red-500 text-xl">❌</span>
              <p className="text-red-700 font-medium">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Processing Status */}
      <AnimatePresence>
        {processingJob && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">
                  🔄 Processing Status
                </h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  processingJob.status === 'completed' 
                    ? 'bg-green-100 text-green-800'
                    : processingJob.status === 'error'
                    ? 'bg-red-100 text-red-800'
                    : processingJob.status === 'processing'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {processingJob.status}
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    processingJob.status === 'completed' 
                      ? 'bg-green-500'
                      : processingJob.status === 'error'
                      ? 'bg-red-500'
                      : 'bg-blue-500'
                  }`}
                  style={{ width: `${processingJob.progress}%` }}
                  initial={{ width: 0 }}
                  animate={{ width: `${processingJob.progress}%` }}
                />
              </div>
              
              <p className="text-gray-700">{processingJob.message}</p>
              
              <p className="text-sm text-gray-500">
                Job ID: {processingJob.job_id}
              </p>

              {/* Results Summary */}
              {processingJob.status === 'completed' && processingJob.results && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg"
                >
                  <h4 className="font-semibold text-green-800 mb-2">✅ Processing Complete!</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-green-700 font-medium">Objects Detected:</span>
                      <span className="ml-2">{processingJob.results.detected_objects || 0}</span>
                    </div>
                    <div>
                      <span className="text-green-700 font-medium">Listings Created:</span>
                      <span className="ml-2">{processingJob.results.listings_created?.length || 0}</span>
                    </div>
                    <div>
                      <span className="text-green-700 font-medium">Total Value:</span>
                      <span className="ml-2">${processingJob.results.total_estimated_value?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cropped Images Gallery */}
      {croppedImages.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            🖼️ Detected Objects ({croppedImages.length})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {croppedImages.slice(0, 12).map((image, index) => (
              <motion.div
                key={image.filename}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="relative group"
              >
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <Image
                    src={`${API_BASE}${image.url}`}
                    alt={`Detected object ${index + 1}`}
                    width={200}
                    height={200}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <div className="mt-2 text-xs text-gray-600 text-center">
                  <p className="truncate">{image.filename}</p>
                  <p>{(image.size / 1024).toFixed(1)} KB</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default PipelineUpload;