'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ObjectSelection from './ObjectSelection';
import ItemSelection from './ItemSelection';
import PreparedPosts from './PreparedPosts';
import PostQueue from './PostQueue';

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
  category?: string;
  condition?: string;
  description?: string;
  tags?: string[];
  timestamp: number;
  frameImage: string;
}

interface QueuedItem {
  id: string;
  name: string;
  price: number;
  description: string;
  tags: string[];
  status: 'ready' | 'posting' | 'posted' | 'error';
  platforms: string[];
  thumbnail: string;
  timestamp: number;
  frameImage: string;
}

type FlowStep = 'camera' | 'selection' | 'item-selection' | 'prepared-posts' | 'queue' | 'complete';

interface DeclutterFlowProps {
  onComplete: () => void;
  onBack: () => void;
}

const DeclutterFlow = ({ onComplete, onBack }: DeclutterFlowProps) => {
  const [currentStep, setCurrentStep] = useState<FlowStep>('selection');
  const [detectedObjects, setDetectedObjects] = useState<DetectedObject[]>([]);
  const [selectedItems, setSelectedItems] = useState<DetectedObject[]>([]);
  const [preparedPosts, setPreparedPosts] = useState<any[]>([]);
  const [queuedItems, setQueuedItems] = useState<QueuedItem[]>([]);

  const handleScanComplete = (objects: DetectedObject[]) => {
    console.log('DeclutterFlow: Received objects:', objects);
    setDetectedObjects(objects);
    setCurrentStep('item-selection');
  };

  const handleItemSelection = (items: DetectedObject[]) => {
    setSelectedItems(items);
    setCurrentStep('prepared-posts');
  };

  const handlePreparedPosts = (posts: any[]) => {
    setPreparedPosts(posts);
    
    // Convert prepared posts to queued items
    const items: QueuedItem[] = posts.map(post => ({
      id: post.id,
      name: post.item.name,
      price: post.price,
      description: post.description,
      tags: post.tags,
      status: 'ready' as const,
      platforms: [post.platform],
      thumbnail: post.item.croppedImageUrl,
      timestamp: Date.now(),
      frameImage: post.item.croppedImageUrl
    }));
    
    setQueuedItems(items);
    setCurrentStep('queue');
  };

  const handlePostComplete = () => {
    setCurrentStep('complete');
    // After a brief delay, complete the flow
    setTimeout(() => {
      onComplete();
    }, 2000);
  };

  const handleBack = () => {
    switch (currentStep) {
      case 'selection':
        onBack(); // Go back to dashboard since we're skipping camera
        break;
      case 'item-selection':
        setCurrentStep('selection');
        break;
      case 'prepared-posts':
        setCurrentStep('item-selection');
        break;
      case 'queue':
        setCurrentStep('prepared-posts');
        break;
      default:
        onBack();
    }
  };

  return (
    <div className="relative w-full h-screen overflow-y-auto">
      <AnimatePresence mode="wait">
        {currentStep === 'selection' && (
          <motion.div
            key="selection"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <ObjectSelection
              photoId="mock-photo-id"
              originalPhotoUrl="/vercel.svg"
              onObjectsSelected={handleScanComplete}
              onBack={handleBack}
            />
          </motion.div>
        )}

        {currentStep === 'item-selection' && (
          <motion.div
            key="item-selection"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <ItemSelection
              detectedObjects={detectedObjects}
              onBack={handleBack}
              onItemsSelected={handleItemSelection}
            />
          </motion.div>
        )}

        {currentStep === 'prepared-posts' && (
          <motion.div
            key="prepared-posts"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <PreparedPosts
              selectedItems={selectedItems}
              onBack={handleBack}
              onContinue={handlePreparedPosts}
            />
          </motion.div>
        )}

        {currentStep === 'queue' && (
          <motion.div
            key="queue"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <PostQueue
              items={queuedItems}
              onBack={handleBack}
              onPostComplete={handlePostComplete}
            />
          </motion.div>
        )}

        {currentStep === 'complete' && (
          <motion.div
            key="complete"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-[#F6EFD9]/10 via-white to-[#F6EFD9]/5"
          >
            <div className="text-center">
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-24 h-24 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-12 h-12 border-4 border-white border-t-transparent rounded-full"
                />
              </motion.div>
              
              <h2 className="text-3xl font-bold text-[#1A6A6A] mb-4">
                Flow Complete!
              </h2>
              <p className="text-lg text-[#6b7b8c]">
                Redirecting to dashboard...
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DeclutterFlow;
