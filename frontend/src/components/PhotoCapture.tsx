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
  croppedImageUrl: string;
  estimatedValue: number;
}

interface PhotoCaptureProps {
  onObjectsSelected: (selectedObjects: DetectedObject[]) => void;
  onBack: () => void;
}

const PhotoCapture = ({ onObjectsSelected, onBack }: PhotoCaptureProps) => {
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
  const streamRef = useRef<MediaStream | null>(null);

  // Mock detected objects for demonstration
  const mockObjects: DetectedObject[] = [
    {
      id: '1',
      name: 'Gaming Chair',
      confidence: 0.95,
      boundingBox: { x: 100, y: 150, width: 200, height: 300 },
      croppedImageUrl: '/vercel.svg',
      estimatedValue: 120
    },
    {
      id: '2',
      name: 'MacBook Pro',
      confidence: 0.88,
      boundingBox: { x: 350, y: 200, width: 150, height: 100 },
      croppedImageUrl: '/vercel.svg',
      estimatedValue: 450
    },
    {
      id: '3',
      name: 'Dining Table',
      confidence: 0.92,
      boundingBox: { x: 50, y: 400, width: 300, height: 200 },
      croppedImageUrl: '/vercel.svg',
      estimatedValue: 200
    },
    {
      id: '4',
      name: 'Wireless Mouse',
      confidence: 0.85,
      boundingBox: { x: 500, y: 300, width: 80, height: 50 },
      croppedImageUrl: '/vercel.svg',
      estimatedValue: 25
    }
  ];

  useEffect(() => {
    startCamera();
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
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
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

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
          streamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
          }
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
    if (!videoRef.current || !canvasRef.current) return;

    setIsCapturing(true);

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (!context) throw new Error('Could not get canvas context');

      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob
      const blob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((blob) => {
          if (blob) resolve(blob);
        }, 'image/jpeg', 0.8);
      });

      // Create object URL for preview
      const photoURL = URL.createObjectURL(blob);
      setCapturedPhoto(photoURL);

      // Upload photo to Supabase
      await uploadPhotoToSupabase(blob);

    } catch (error) {
      console.error('Error capturing photo:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  const uploadPhotoToSupabase = async (photoBlob: Blob) => {
    try {
      setIsUploading(true);
      setUploadProgress(0);

      // Generate unique filename with timestamp
      const timestamp = Date.now();
      const fileName = `photo_${timestamp}.jpg`;

      // Create File object from Blob
      const photoFile = new File([photoBlob], fileName, { type: 'image/jpeg' });

      // Upload with progress tracking
      const uploadPromise = uploadPhoto(photoFile, fileName);
      
      // Simulate progress
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
      
      // Save photo metadata to database
      try {
        const photoData = await savePhotoMetadata({
          filename: fileName,
          url: publicUrl,
          size: photoBlob.size,
          user_id: 'anonymous'
        });
        
        console.log('Photo metadata saved to database:', photoData);
        setPhotoId(photoData[0].id);
        
        // Start AI processing
        processPhoto(photoData[0].id);
        
      } catch (dbError) {
        console.error('Error saving photo metadata to database:', dbError);
      }
      
      console.log('Photo uploaded successfully:', publicUrl);
    } catch (error) {
      console.error('Error uploading photo:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const processPhoto = async (photoId: string) => {
    setIsProcessing(true);
    
    // Simulate AI processing
    setTimeout(async () => {
      setIsProcessing(false);
      setDetectedObjects(mockObjects);
      
      // Save cropped objects to database
      try {
        for (const object of mockObjects) {
          await saveCroppedObject({
            photo_id: photoId,
            object_name: object.name,
            confidence: object.confidence,
            bounding_box: object.boundingBox,
            cropped_image_url: object.croppedImageUrl,
            estimated_value: object.estimatedValue
          });
        }
        console.log('Cropped objects saved to database');
      } catch (error) {
        console.error('Error saving cropped objects:', error);
      }
    }, 3000);
  };

  const toggleObjectSelection = (objectId: string) => {
    const newSelected = new Set(selectedObjects);
    if (newSelected.has(objectId)) {
      newSelected.delete(objectId);
    } else {
      newSelected.add(objectId);
    }
    setSelectedObjects(newSelected);
  };

  const handleContinue = () => {
    const selected = detectedObjects.filter(obj => selectedObjects.has(obj.id));
    onObjectsSelected(selected);
  };

  const retakePhoto = () => {
    setCapturedPhoto(null);
    setUploadedPhotoUrl(null);
    setUploadProgress(0);
    setIsProcessing(false);
    setDetectedObjects([]);
    setSelectedObjects(new Set());
    setPhotoId(null);
  };

  const totalValue = Array.from(selectedObjects).reduce((sum, objectId) => {
    const object = detectedObjects.find(obj => obj.id === objectId);
    return sum + (object?.estimatedValue || 0);
  }, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="flex items-center justify-between p-4 sm:p-6">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onBack}
            className="p-2 sm:p-3 bg-black/30 backdrop-blur-md border border-white/20 rounded-xl text-white hover:bg-black/50 transition-all"
          >
            <ArrowLeft className="w-5 h-5 sm:w-6 sm:h-6" />
          </motion.button>
          
          <div className="text-center">
            <h1 className="text-lg sm:text-xl font-bold text-white">
              {detectedObjects.length > 0 ? 'Select Items to Sell' : 'Capture Photo'}
            </h1>
            <p className="text-xs sm:text-sm text-white/80">
              {detectedObjects.length > 0 
                ? `${selectedObjects.size} of ${detectedObjects.length} items selected`
                : 'Point at objects to detect items'
              }
            </p>
          </div>
          
          <div className="w-10 sm:w-12" /> {/* Spacer */}
        </div>
      </div>

      <div className="p-4 sm:p-6">
        <div className="max-w-6xl mx-auto">
          {/* Camera Feed or Captured Photo */}
          {!capturedPhoto ? (
            <div className="relative bg-black rounded-2xl overflow-hidden aspect-video">
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
                        startCamera();
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
                  {/* Capture overlay */}
                  {isCapturing && (
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      <div className="text-center">
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 0.5 }}
                          className="w-20 h-20 border-4 border-white rounded-full flex items-center justify-center mb-4 mx-auto"
                        >
                          <Camera className="w-8 h-8 text-white" />
                        </motion.div>
                        <div className="text-white text-lg font-semibold">
                          Capturing photo...
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="mb-8">
              <h2 className="text-white text-lg font-semibold mb-4">Captured Photo</h2>
              <div className="relative bg-white/10 rounded-2xl p-4 backdrop-blur-sm">
                <img
                  src={capturedPhoto}
                  alt="Captured photo"
                  className="w-full max-w-2xl mx-auto rounded-xl shadow-2xl"
                />
              </div>
            </div>
          )}

          {/* Hidden canvas for photo capture */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Upload Progress */}
          {isUploading && (
            <div className="text-center mb-8">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full mx-auto mb-4"
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

          {/* Processing */}
          {isProcessing && (
            <div className="text-center mb-8">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 border-4 border-teal-400 border-t-transparent rounded-full mx-auto mb-4"
              />
              <p className="text-white text-sm sm:text-base">AI is analyzing your photo...</p>
            </div>
          )}

          {/* Detected Objects Grid */}
          {detectedObjects.length > 0 && (
            <div className="mb-8">
              <h2 className="text-white text-lg font-semibold mb-4">Detected Items</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <AnimatePresence>
                  {detectedObjects.map((object, index) => {
                    const isSelected = selectedObjects.has(object.id);
                    return (
                      <motion.div
                        key={object.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ delay: index * 0.1 }}
                        className={`relative bg-white/10 backdrop-blur-sm rounded-2xl p-4 border-2 transition-all duration-300 cursor-pointer ${
                          isSelected 
                            ? 'border-teal-400 bg-teal-400/20' 
                            : 'border-white/20 hover:border-white/40'
                        }`}
                        onClick={() => toggleObjectSelection(object.id)}
                      >
                        {/* Selection Indicator */}
                        <div className={`absolute top-3 right-3 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                          isSelected 
                            ? 'bg-teal-400 border-teal-400' 
                            : 'border-white/40'
                        }`}>
                          {isSelected && <Check className="w-4 h-4 text-white" />}
                        </div>

                        {/* Object Image */}
                        <div className="aspect-square bg-white/10 rounded-xl mb-3 flex items-center justify-center">
                          <img
                            src={object.croppedImageUrl}
                            alt={object.name}
                            className="w-full h-full object-cover rounded-xl"
                          />
                        </div>

                        {/* Object Info */}
                        <div className="space-y-2">
                          <h3 className="text-white font-semibold text-sm truncate">
                            {object.name}
                          </h3>
                          
                          <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1">
                              <Star className="w-3 h-3 text-yellow-400 fill-current" />
                              <span className="text-white/80 text-xs">
                                {(object.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-green-400" />
                            <span className="text-green-400 font-semibold">
                              ${object.estimatedValue}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </div>
          )}

          {/* Selection Summary */}
          {selectedObjects.size > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-teal-500/20 to-cyan-500/20 backdrop-blur-sm rounded-2xl p-6 border border-teal-400/30"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white text-lg font-semibold mb-1">
                    {selectedObjects.size} item{selectedObjects.size !== 1 ? 's' : ''} selected
                  </h3>
                  <p className="text-white/80 text-sm">
                    Total estimated value: <span className="text-green-400 font-semibold">${totalValue}</span>
                  </p>
                </div>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleContinue}
                  className="px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold rounded-xl shadow-2xl hover:shadow-3xl transition-all flex items-center gap-2"
                >
                  Continue
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Bottom Controls */}
          <div className="text-center mt-8">
            {!capturedPhoto && !isCapturing && !cameraError && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={capturePhoto}
                className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full shadow-2xl flex items-center justify-center text-white mb-4 mx-auto"
              >
                <Camera className="w-6 h-6 sm:w-8 sm:h-8" />
              </motion.button>
            )}
            
            {capturedPhoto && !isProcessing && !isUploading && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={retakePhoto}
                className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white font-semibold rounded-xl shadow-2xl hover:shadow-3xl transition-all text-sm sm:text-base flex items-center gap-2 mx-auto"
              >
                <RotateCcw className="w-4 h-4" />
                Retake Photo
              </motion.button>
            )}
            
            <p className="text-white/80 text-xs sm:text-sm px-4">
              {cameraError
                ? "Camera access is required to capture photos"
                : isCapturing
                  ? "Capturing photo..."
                  : isUploading
                    ? "Uploading photo to cloud storage..."
                    : isProcessing
                      ? "Analyzing photo for resellable items..."
                      : detectedObjects.length > 0
                        ? "Select items you want to sell"
                        : capturedPhoto
                          ? uploadedPhotoUrl 
                            ? "Photo uploaded! AI found items to sell."
                            : "Photo captured! Uploading to cloud..."
                          : "Capture a photo of your space"
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PhotoCapture;