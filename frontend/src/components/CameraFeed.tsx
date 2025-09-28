'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import { 
  ArrowLeft, 
  Camera, 
  Check, 
  X, 
  RotateCcw,
  Sparkles,
  Upload,
  Cloud,
  DollarSign,
  Star,
  ShoppingBag,
  ArrowRight
} from 'lucide-react';
import { uploadPhoto, getPhotoUrl, savePhotoMetadata, saveCroppedObject } from '../config/supabase';

interface DetectedObject {
  id: string;
  name: string;
  confidence: number;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  thumbnail: string;
  estimatedValue: number;
  timestamp: number; // Time in video when detected
  frameImage: string; // Frame from video
}

interface CameraFeedProps {
  onObjectsSelected: (selectedObjects: DetectedObject[]) => void;
  onBack: () => void;
}

const CameraFeed = ({ onObjectsSelected, onBack }: CameraFeedProps) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [detectedObjects, setDetectedObjects] = useState<DetectedObject[]>([]);
  const [selectedObjects, setSelectedObjects] = useState<Set<string>>(new Set());
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedPhotoUrl, setUploadedPhotoUrl] = useState<string | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
  const [photoId, setPhotoId] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Mock detected objects for demonstration
  const mockObjects: DetectedObject[] = [
    {
      id: '1',
      name: 'Gaming Chair',
      confidence: 0.95,
      boundingBox: { x: 100, y: 150, width: 200, height: 300 },
      thumbnail: '/vercel.svg',
      estimatedValue: 120,
      timestamp: 2.5,
      frameImage: '/vercel.svg'
    },
    {
      id: '2',
      name: 'Laptop',
      confidence: 0.88,
      boundingBox: { x: 350, y: 200, width: 150, height: 100 },
      thumbnail: '/vercel.svg',
      estimatedValue: 450,
      timestamp: 4.2,
      frameImage: '/vercel.svg'
    },
    {
      id: '3',
      name: 'Dining Table',
      confidence: 0.92,
      boundingBox: { x: 50, y: 400, width: 300, height: 200 },
      thumbnail: '/vercel.svg',
      estimatedValue: 200,
      timestamp: 6.8,
      frameImage: '/vercel.svg'
    }
  ];

  const startCapturing = async () => {
    try {
      setCameraError(null);
      
      // Check if we're on HTTPS or localhost
      if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
        setCameraError('Camera access requires HTTPS or localhost. Please use HTTPS or run locally.');
        return;
      }

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraError('Camera access is not supported in this browser.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false 
      });
      
      setHasCameraPermission(true);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setIsCapturing(true);
      
      // Take photo after a brief delay
      setTimeout(() => {
        capturePhoto();
      }, 1000);

    } catch (error: any) {
      console.error('Error accessing camera:', error);
      
      if (error.name === 'NotAllowedError') {
        setCameraError('Camera permission denied. Please allow camera access and try again.');
      } else if (error.name === 'NotFoundError') {
        setCameraError('No camera found. Please connect a camera and try again.');
      } else if (error.name === 'NotReadableError') {
        setCameraError('Camera is already in use by another application.');
      } else if (error.name === 'OverconstrainedError') {
        setCameraError('Camera constraints cannot be satisfied. Trying with default settings...');
        // Try again with default settings
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true,
            audio: false 
          });
          setHasCameraPermission(true);
          // Continue with the rest of the logic...
        } catch (retryError) {
          setCameraError('Unable to access camera. Please check your camera settings.');
        }
      } else {
        setCameraError('Unable to access camera. Please check your camera settings.');
      }
      setHasCameraPermission(false);
    }
  };

  const capturePhoto = async () => {
    console.log('capturePhoto called');
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const context = canvas.getContext('2d');
      
      if (context) {
        console.log('Canvas context found, capturing photo...');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const photoDataUrl = canvas.toDataURL('image/jpeg');
        console.log('Photo captured, setting state...');
        setCapturedPhoto(photoDataUrl);
        setIsCapturing(false);
        
        // Stop camera stream
        if (video.srcObject) {
          const stream = video.srcObject as MediaStream;
          stream.getTracks().forEach(track => track.stop());
        }
        
        console.log('Starting photo upload...');
        // Upload photo to Supabase
        try {
          await uploadPhotoToSupabase(photoDataUrl);
        } catch (error) {
          console.error('Upload failed, continuing with analysis anyway:', error);
        }
        
        console.log('Starting photo analysis...');
        // Start backend pipeline analysis (runs OD.py via pipeline API)
        try {
          await sendToPipeline(photoDataUrl);
        } catch (e) {
          console.error('Pipeline analysis failed, falling back to local analyzePhoto:', e);
          analyzePhoto();
        }
      } else {
        console.error('Canvas context not found');
      }
    } else {
      console.error('Video ref or canvas ref not found');
    }
  };

  const stopCapturing = () => {
    setIsCapturing(false);
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
  };

  // Minimal stub to avoid needing Supabase bucket checks during capture step.
  // Returns false so the upload is skipped and the code falls back to analysis.
  const checkBucketExists = async (): Promise<boolean> => {
    return false;
  };

  const uploadPhotoToSupabase = async (photoDataUrl: string) => {
    try {
      console.log('uploadPhotoToSupabase called');
      setIsUploading(true);
      setUploadProgress(0);

      // Check if bucket exists first
      const bucketExists = await checkBucketExists();
      if (!bucketExists) {
        throw new Error('Cannot access photo bucket. Please ensure:\n1. A "photos" bucket exists in Supabase Storage\n2. The bucket is set to "Public"\n3. Proper storage policies are configured\n4. Your API key has storage permissions');
      }

      // Generate unique filename with timestamp
      const timestamp = Date.now();
      const fileName = `photo_${timestamp}.jpg`;

      // Convert data URL to blob
      const response = await fetch(photoDataUrl);
      const blob = await response.blob();
      const photoFile = new File([blob], fileName, { type: 'image/jpeg' });

      // Upload with progress tracking
      const uploadPromise = uploadPhoto(photoFile, fileName);
      
      // Simulate progress (since Supabase doesn't provide progress callbacks)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      await uploadPromise;
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Get the public URL
      const publicUrl = getPhotoUrl(fileName);
      setUploadedPhotoUrl(publicUrl);
      
      // Photo uploaded successfully - no database metadata needed
      
      console.log('Photo uploaded successfully:', publicUrl);
    } catch (error) {
      console.error('Error uploading photo:', error);
      // You might want to show an error message to the user here
    } finally {
      console.log('Upload process finished, setting isUploading to false');
      setIsUploading(false);
    }
  };

  const analyzePhoto = () => {
    console.log('analyzePhoto called, starting analysis...');
    setIsProcessing(true);
    
    // Simulate AI analysis
    setTimeout(() => {
      console.log('Analysis complete, setting detected objects...');
      setIsProcessing(false);
      setDetectedObjects(mockObjects);
      console.log('Detected objects set:', mockObjects);
    }, 3000);
  };

  // ----- New: send captured image to backend pipeline API -----
  const PIPELINE_API_BASE = (process.env.NEXT_PUBLIC_PIPELINE_API_URL as string) || 'http://localhost:3005';

  const sendToPipeline = async (photoDataUrl: string) => {
    console.log('sendToPipeline called');
    setIsProcessing(true);

    try {
      // Convert data URL to blob
      const resp = await fetch(photoDataUrl);
      const blob = await resp.blob();
      const timestamp = Date.now();
      const fileName = `photo_${timestamp}.jpg`;

      const file = new File([blob], fileName, { type: 'image/jpeg' });

      const form = new FormData();
      form.append('image', file);
      // ask backend to run asynchronously and return a job id
      form.append('sync', 'false');

      const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/process`, {
        method: 'POST',
        body: form
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Pipeline API returned ${res.status}: ${text}`);
      }

      const data = await res.json();
      console.log('Pipeline upload response:', data);

      if (data && data.job_id) {
        // Poll job status until completion
        await pollJobStatus(data.job_id);
      } else if (data && data.status === 'completed' && data.results) {
        // synchronous response with results
        const mapped = mapPipelineResultsToDetectedObjects(data.results);
        setDetectedObjects(mapped);
      } else {
        throw new Error('Unexpected pipeline API response');
      }

    } catch (error) {
      console.error('sendToPipeline error:', error);
      // Fallback to local mocked analysis so UX is not blocked
      analyzePhoto();
    } finally {
      setIsProcessing(false);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    console.log('pollJobStatus for', jobId);
    const statusUrl = `${PIPELINE_API_BASE}/api/pipeline/status/${jobId}`;

    return new Promise<void>((resolve, reject) => {
      let attempts = 0;
      const maxAttempts = 60; // ~60 seconds timeout

      const interval = setInterval(async () => {
        attempts += 1;
        try {
          const r = await fetch(statusUrl);
          if (!r.ok) {
            throw new Error(`Status request failed: ${r.status}`);
          }
          const j = await r.json();
          console.log('Job status:', j);

          if (j.status === 'completed') {
            clearInterval(interval);
            if (j.results) {
              const mapped = mapPipelineResultsToDetectedObjects(j.results);
              setDetectedObjects(mapped);
            }
            resolve();
          } else if (j.status === 'error') {
            clearInterval(interval);
            reject(new Error(j.message || 'Processing error'));
          } else {
            // still processing or queued
            if (attempts >= maxAttempts) {
              clearInterval(interval);
              reject(new Error('Pipeline polling timed out'));
            }
          }

        } catch (e) {
          clearInterval(interval);
          reject(e);
        }
      }, 1000);
    });
  };

  const mapPipelineResultsToDetectedObjects = (results: any): DetectedObject[] => {
    // Try common shapes for results coming from the backend pipeline.
    // If the pipeline returns an objects/detected_objects array, map it; otherwise return mock fallback.
    const src = results?.detected_objects || results?.objects || results?.items || null;

    if (!Array.isArray(src)) {
      console.warn('Unrecognized pipeline results shape, using mock objects');
      return mockObjects;
    }

    return src.map((o: any, idx: number) => ({
      id: o.id?.toString() || `${Date.now()}_${idx}`,
      name: o.name || o.label || o.class || 'Unknown',
      confidence: typeof o.confidence === 'number' ? o.confidence : (o.score || 0.5),
      boundingBox: {
        x: o.bbox?.x ?? o.bbox?.[0] ?? 0,
        y: o.bbox?.y ?? o.bbox?.[1] ?? 0,
        width: o.bbox?.width ?? o.bbox?.[2] ?? 100,
        height: o.bbox?.height ?? o.bbox?.[3] ?? 100,
      },
      thumbnail: o.thumbnail || o.thumb || '/vercel.svg',
      estimatedValue: o.estimated_value || o.estimatedValue || 0,
      timestamp: o.timestamp || Date.now(),
      frameImage: o.frame_image || o.frameImage || '/vercel.svg'
    }));
  };

  const handleObjectApprove = (objectId: string) => {
    setDetectedObjects(prev => prev.filter(obj => obj.id !== objectId));
  };

  const handleObjectRemove = (objectId: string) => {
    setDetectedObjects(prev => prev.filter(obj => obj.id !== objectId));
  };

  const finishScanning = () => {
    console.log('Finishing scan with objects:', detectedObjects);
    onObjectsSelected(detectedObjects);
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* Camera Feed */}
      {!capturedPhoto ? (
        <div className="absolute inset-0">
          {cameraError ? (
            <div className="w-full h-full bg-gray-900 flex items-center justify-center">
              <div className="text-center p-8 max-w-md">
                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <X className="w-8 h-8 text-red-400" />
                </div>
                <h3 className="text-white text-lg font-semibold mb-2">Camera Access Error</h3>
                <p className="text-white/80 text-sm mb-4">{cameraError}</p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setCameraError(null);
                    setHasCameraPermission(null);
                  }}
                  className="px-4 py-2 bg-teal-500 text-white rounded-lg text-sm font-medium"
                >
                  Try Again
                </motion.button>
              </div>
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                className="w-full h-full object-cover"
                muted
                playsInline
              />
               {/* Capturing overlay */}
               {isCapturing && (
                <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-20 h-20 border-4 border-red-500 rounded-full flex items-center justify-center mb-4 mx-auto">
                      <div className="w-8 h-8 bg-red-500 rounded"></div>
                    </div>
                     <div className="text-white text-2xl font-bold mb-2">
                       Capturing...
                     </div>
                     <div className="text-white/80 text-sm">
                       Taking photo of your space...
                     </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        ) : (
        <div className="absolute inset-0">
          <img
            src={capturedPhoto}
            className="w-full h-full object-cover"
            alt="Captured space"
          />
        </div>
      )}

      {/* Top Bar */}
      <div className="absolute top-0 left-0 right-0 z-20 p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onBack}
            className="p-2 sm:p-3 bg-black/30 backdrop-blur-md border border-white/20 rounded-xl text-white hover:bg-black/50 transition-all"
          >
            <ArrowLeft className="w-5 h-5 sm:w-6 sm:h-6" />
          </motion.button>
          
          <div className="text-center">
            <h1 className="text-lg sm:text-xl font-bold text-white">Scan Room</h1>
            <p className="text-xs sm:text-sm text-white/80">Point at objects to detect items</p>
          </div>
          
          <div className="w-10 sm:w-12" /> {/* Spacer */}
        </div>
      </div>


      {/* Detected Objects Overlay */}
      <AnimatePresence>
        {detectedObjects.length > 0 && !isProcessing && (
          <div className="absolute inset-0 z-10">
            {detectedObjects.map((object) => (
              <motion.div
                key={object.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="absolute"
                style={{
                  left: object.boundingBox.x,
                  top: object.boundingBox.y,
                  width: object.boundingBox.width,
                  height: object.boundingBox.height,
                }}
              >
                {/* Bounding Box */}
                <div className="absolute inset-0 border-2 border-teal-400 rounded-lg bg-teal-400/10 backdrop-blur-sm">
                  {/* Object Info */}
                  <div className="absolute -top-12 left-0 bg-black/80 backdrop-blur-md rounded-lg px-3 py-2 text-white text-sm">
                    <div className="font-semibold">{object.name}</div>
                    <div className="text-teal-400">${object.estimatedValue}</div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="absolute -bottom-12 left-0 flex gap-2">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => handleObjectApprove(object.id)}
                      className="p-2 bg-green-500 rounded-full text-white shadow-lg"
                    >
                      <Check className="w-4 h-4" />
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => handleObjectRemove(object.id)}
                      className="p-2 bg-red-500 rounded-full text-white shadow-lg"
                    >
                      <X className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 z-20 p-4 sm:p-6">
        {/* Bubbles Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />
        
        <div className="relative z-10 text-center">
          {!capturedPhoto && !isCapturing && (
            <div className="flex flex-col items-center gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startCapturing}
                className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full shadow-2xl flex items-center justify-center text-white mb-4"
              >
                <Upload className="w-6 h-6 sm:w-8 sm:h-8" />
              </motion.button>
              
              {/* Test button to bypass photo capture */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  console.log('Test button clicked - bypassing photo capture');
                  setDetectedObjects(mockObjects);
                }}
                className="px-4 py-2 bg-yellow-500 text-white text-sm rounded-lg"
              >
                Test: Skip to Results
              </motion.button>
            </div>
          )}
          
          {isCapturing && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={stopCapturing}
              className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-red-500 to-red-600 rounded-full shadow-2xl flex items-center justify-center text-white mb-4 mx-auto"
            >
              <X className="w-6 h-6 sm:w-8 sm:h-8" />
            </motion.button>
          )}
          
          {isUploading && (
            <div className="text-center mb-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 sm:w-20 sm:h-20 border-4 border-blue-400 border-t-transparent rounded-full mx-auto mb-4"
              />
              <div className="w-full max-w-xs mx-auto bg-white/20 rounded-full h-2 mb-2">
                <div 
                  className="bg-blue-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
               <p className="text-white text-sm sm:text-base">
                 Uploading photo... {uploadProgress}%
               </p>
            </div>
          )}
          
          {isProcessing && (
            <div className="text-center mb-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 sm:w-20 sm:h-20 border-4 border-teal-400 border-t-transparent rounded-full mx-auto mb-4"
              />
               <p className="text-white text-sm sm:text-base">AI is analyzing your photo...</p>
            </div>
          )}
          
          {detectedObjects.length > 0 && (
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={finishScanning}
              className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold rounded-xl shadow-2xl hover:shadow-3xl transition-all mb-4 text-sm sm:text-base"
            >
              Continue with {detectedObjects.length} items
            </motion.button>
          )}
          
          {/* Debug info */}
          {detectedObjects.length > 0 && (
            <div className="text-white/60 text-xs mb-2">
              Debug: {detectedObjects.length} objects detected
            </div>
          )}
          
          {capturedPhoto && detectedObjects.length === 0 && !isUploading && (
            <div className="flex flex-col items-center gap-3 mb-4">
              {uploadedPhotoUrl && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-400/30 rounded-lg text-green-400 text-sm"
                >
                  <Cloud className="w-4 h-4" />
                  Photo uploaded successfully
                </motion.div>
              )}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setCapturedPhoto(null);
                  setDetectedObjects([]);
                  setUploadedPhotoUrl(null);
                  setUploadProgress(0);
                }}
                className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white font-semibold rounded-xl shadow-2xl hover:shadow-3xl transition-all text-sm sm:text-base flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Take Another Photo
              </motion.button>
            </div>
          )}
          
          <p className="text-white/80 text-xs sm:text-sm px-4">
            {cameraError
              ? "Camera access is required to take photos"
              : isCapturing 
                ? "Capturing your space for AI analysis..." 
                : isUploading
                  ? "Uploading photo to cloud storage..."
                  : isProcessing
                    ? "Analyzing photo for clutter items..."
                    : detectedObjects.length > 0
                      ? "Review detected items above"
                      : capturedPhoto
                        ? uploadedPhotoUrl 
                          ? "Photo uploaded! AI found items to sell."
                          : "Photo captured! Uploading to cloud..."
                        : "Take a photo of your space"
            }
          </p>
        </div>
      </div>

    </div>
  );
};

export default CameraFeed;
