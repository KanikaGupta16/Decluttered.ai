'use client';

import { motion, AnimatePresence } from 'framer-motion';
import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  X, 
  Upload,
  Camera
} from 'lucide-react';
import { getCroppedObjects } from '../config/supabase';

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

interface ObjectSelectionProps {
  photoId: string;
  originalPhotoUrl: string;
  onObjectsSelected: (selectedObjects: DetectedObject[]) => void;
  onBack: () => void;
}

const ObjectSelection = ({ photoId, originalPhotoUrl, onObjectsSelected, onBack }: ObjectSelectionProps) => {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);


  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // Use back camera on mobile
      });
      setStream(mediaStream);
      setShowCamera(true);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Unable to access camera. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setShowCamera(false);
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0);

    // Convert to blob and upload
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
      await handleImageUpload({ target: { files: [file] } } as any);
      stopCamera();
    }, 'image/jpeg', 0.8);
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // Create a preview URL
      const previewUrl = URL.createObjectURL(file);
      setUploadedImage(previewUrl);
      
      // Here you would upload to Supabase and get the photo ID
      // For now, we'll simulate the upload
      console.log('Uploading image:', file.name);
      
      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate processing
      setIsProcessing(true);
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Auto-navigate to next step after processing
      setTimeout(() => {
        // Get the latest detected objects and auto-select all for demo
        const mockObjects = [
          {
            id: '1',
            name: 'Gaming Chair',
            confidence: 0.95,
            boundingBox: { x: 100, y: 150, width: 200, height: 300 },
            croppedImageUrl: '/clutter.png',
            estimatedValue: 120
          },
          {
            id: '2',
            name: 'MacBook Pro',
            confidence: 0.88,
            boundingBox: { x: 350, y: 200, width: 150, height: 100 },
            croppedImageUrl: '/declutter.png',
            estimatedValue: 450
          },
          {
            id: '3',
            name: 'Dining Table',
            confidence: 0.92,
            boundingBox: { x: 50, y: 400, width: 300, height: 200 },
            croppedImageUrl: '/clutter.png',
            estimatedValue: 200
          },
          {
            id: '4',
            name: 'Wireless Mouse',
            confidence: 0.85,
            boundingBox: { x: 500, y: 300, width: 80, height: 50 },
            croppedImageUrl: '/declutter.png',
            estimatedValue: 25
          },
          {
            id: '5',
            name: 'Coffee Table',
            confidence: 0.90,
            boundingBox: { x: 200, y: 500, width: 250, height: 150 },
            croppedImageUrl: '/clutter.png',
            estimatedValue: 80
          },
          {
            id: '6',
            name: 'Bookshelf',
            confidence: 0.87,
            boundingBox: { x: 600, y: 100, width: 120, height: 400 },
            croppedImageUrl: '/declutter.png',
            estimatedValue: 150
          }
        ];
        onObjectsSelected(mockObjects);
      }, 1000);
      
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsUploading(false);
      setIsProcessing(false);
    }
  };


  // Camera Interface
  if (showCamera) {
    return (
      <div className="fixed inset-0 z-50 bg-black">
        <div className="relative w-full h-full">
          {/* Camera Header */}
          <div className="absolute top-0 left-0 right-0 z-10 bg-black/50 backdrop-blur-md p-4">
            <div className="flex items-center justify-between">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={stopCamera}
                className="p-3 bg-black/50 backdrop-blur-md border border-white/20 rounded-xl text-white hover:bg-black/70 transition-all"
              >
                <X className="w-6 h-6" />
              </motion.button>
              
              <h2 className="text-white text-lg font-semibold">Take Photo</h2>
              
              <div className="w-12" /> {/* Spacer */}
            </div>
          </div>

          {/* Video Stream */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />

          {/* Camera Controls */}
          <div className="absolute bottom-0 left-0 right-0 z-10 bg-black/50 backdrop-blur-md p-6">
            <div className="flex justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={capturePhoto}
                className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-2xl"
              >
                <div className="w-16 h-16 bg-white border-4 border-gray-300 rounded-full"></div>
              </motion.button>
            </div>
          </div>

          {/* Hidden canvas for photo capture */}
          <canvas ref={canvasRef} className="hidden" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F6EFD9]/10 via-white to-[#F6EFD9]/5 flex items-center justify-center">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-white/80 backdrop-blur-md border-b border-[#F6EFD9]/30">
        <div className="flex items-center justify-between p-4 sm:p-6">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onBack}
            className="p-2 sm:p-3 bg-white/80 backdrop-blur-md border border-[#F6EFD9]/30 rounded-xl text-black hover:bg-white/90 transition-all shadow-lg"
          >
            <ArrowLeft className="w-5 h-5 sm:w-6 sm:h-6" />
          </motion.button>
          
          <div className="text-center">
            <h1 className="text-lg sm:text-xl font-bold text-black">Start Decluttering</h1>
            <p className="text-xs sm:text-sm text-black/70">
              Upload a photo or take a picture to begin
            </p>
          </div>
          
          <div className="w-10 sm:w-12" /> {/* Spacer */}
        </div>
      </div>

      {/* Main Content - Centered */}
      <div className="w-full max-w-md mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          {/* Hero Icon */}
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="w-24 h-24 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center mx-auto mb-8 shadow-2xl"
          >
            <Camera className="w-12 h-12 text-white" />
          </motion.div>

          {/* Title */}
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-3xl font-bold text-black mb-4"
          >
            Ready to declutter?
          </motion.h2>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-lg text-black/70 mb-12"
          >
            Take a photo or upload an image of your space to detect items you can sell
          </motion.p>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="space-y-4"
          >
            {/* Upload Button */}
            <label className="block cursor-pointer">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              <motion.div
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="w-full px-8 py-4 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3"
              >
                <Upload className="w-6 h-6" />
                Upload Photo
              </motion.div>
            </label>

            {/* Camera Button */}
            <motion.button
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={startCamera}
              className="w-full px-8 py-4 bg-white border-2 border-[#5BAAA7] text-[#5BAAA7] font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3"
            >
              <Camera className="w-6 h-6" />
              Take Photo
            </motion.button>
          </motion.div>

          {/* Processing States */}
          {(isUploading || isProcessing) && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-8 p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-[#F6EFD9]/30 shadow-lg"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-12 h-12 border-4 border-[#5BAAA7] border-t-transparent rounded-full mx-auto mb-4"
              />
              <p className="text-black font-medium">
                {isUploading ? 'Uploading your photo...' : 'Processing your image...'}
              </p>
              <p className="text-black/60 text-sm mt-1">
                {isUploading ? 'Please wait while we upload your image' : 'AI is analyzing your space for sellable items'}
              </p>
            </motion.div>
          )}

          {/* Uploaded Image Preview */}
          {uploadedImage && !isUploading && !isProcessing && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-8"
            >
              <div className="relative">
                <img
                  src={uploadedImage}
                  alt="Uploaded photo"
                  className="w-full max-w-sm mx-auto rounded-2xl shadow-2xl"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-2xl"></div>
              </div>
              <p className="text-black/70 text-sm mt-4">
                Processing your image to detect items...
              </p>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default ObjectSelection;