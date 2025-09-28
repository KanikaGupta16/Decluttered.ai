'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { 
  ArrowLeft, 
  Check, 
  X, 
  Edit3, 
  Trash2,
  DollarSign,
  Tag,
  Upload,
  Globe,
  CheckCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react';

interface QueuedItem {
  id: string;
  name: string;
  price: number;
  description: string;
  tags: string[];
  status: 'ready' | 'posting' | 'posted' | 'error';
  platforms: string[];
  croppedImageUrl: string;
  timestamp: number;
  frameImage: string;
}

interface PostQueueProps {
  items: QueuedItem[];
  onBack: () => void;
  onPostComplete: () => void;
}

const PostQueue = ({ items, onBack, onPostComplete }: PostQueueProps) => {
  const [postingItems, setPostingItems] = useState<Set<string>>(new Set());
  const [postedItems, setPostedItems] = useState<Set<string>>(new Set());
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  const handlePostItem = async (itemId: string) => {
    setPostingItems(prev => new Set([...prev, itemId]));
    
    // Simulate posting delay
    setTimeout(() => {
      setPostingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
      setPostedItems(prev => new Set([...prev, itemId]));
    }, 2000);
  };

  const handlePostAll = async () => {
    const readyItems = items.filter(item => item.status === 'ready');
    setPostingItems(new Set(readyItems.map(item => item.id)));
    
    // Simulate posting all items
    setTimeout(() => {
      setPostingItems(new Set());
      setPostedItems(new Set(readyItems.map(item => item.id)));
      setShowSuccessModal(true);
    }, 3000);
  };

  const handleRemoveItem = (itemId: string) => {
    // Remove item from queue
  };

  const totalValue = items.reduce((sum, item) => sum + item.price, 0);
  const postedCount = postedItems.size;
  const postingCount = postingItems.size;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F6EFD9]/10 via-white to-[#F6EFD9]/5">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-[#F6EFD9]/30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onBack}
              className="flex items-center gap-2 text-[#5BAAA7] hover:text-[#1A6A6A] transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </motion.button>
            
            <div className="text-center">
              <h1 className="text-2xl font-bold text-[#1A6A6A]">Ready to Post</h1>
              <p className="text-sm text-[#6b7b8c]">Review and post your listings</p>
            </div>
            
            <div className="w-20" /> {/* Spacer */}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8"
        >
          <div className="bg-gradient-to-br from-white to-[#F6EFD9]/20 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-[#F6EFD9]/30 shadow-lg">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-xl flex items-center justify-center">
                <Tag className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h3 className="text-sm sm:text-lg font-semibold text-[#1A6A6A]">Total Items</h3>
            </div>
            <div className="text-2xl sm:text-3xl font-bold text-[#5BAAA7]">{items.length}</div>
            <div className="text-xs sm:text-sm text-[#6b7b8c]">Ready to post</div>
          </div>
          
          <div className="bg-gradient-to-br from-white to-[#F6EFD9]/20 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-[#F6EFD9]/30 shadow-lg">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-xl flex items-center justify-center">
                <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h3 className="text-sm sm:text-lg font-semibold text-[#1A6A6A]">Total Value</h3>
            </div>
            <div className="text-2xl sm:text-3xl font-bold text-[#5BAAA7]">${totalValue}</div>
            <div className="text-xs sm:text-sm text-[#6b7b8c]">Potential earnings</div>
          </div>
          
          <div className="bg-gradient-to-br from-white to-[#F6EFD9]/20 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-[#F6EFD9]/30 shadow-lg">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h3 className="text-sm sm:text-lg font-semibold text-[#1A6A6A]">Posted</h3>
            </div>
            <div className="text-2xl sm:text-3xl font-bold text-green-500">{postedCount}</div>
            <div className="text-xs sm:text-sm text-[#6b7b8c]">Successfully posted</div>
          </div>
          
          <div className="bg-gradient-to-br from-white to-[#F6EFD9]/20 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-[#F6EFD9]/30 shadow-lg">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center">
                <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h3 className="text-sm sm:text-lg font-semibold text-[#1A6A6A]">Posting</h3>
            </div>
            <div className="text-2xl sm:text-3xl font-bold text-yellow-500">{postingCount}</div>
            <div className="text-xs sm:text-sm text-[#6b7b8c]">In progress</div>
          </div>
        </motion.div>

        {/* Post All Button */}
        {items.filter(item => item.status === 'ready').length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handlePostAll}
              className="w-full px-8 py-4 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-xl shadow-2xl hover:shadow-3xl transition-all flex items-center justify-center gap-3"
            >
              <Upload className="w-6 h-6" />
              Post All {items.filter(item => item.status === 'ready').length} Items
            </motion.button>
          </motion.div>
        )}

        {/* Items Queue */}
        <div className="space-y-4">
          {items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="bg-gradient-to-br from-white to-[#F6EFD9]/20 backdrop-blur-sm rounded-2xl p-6 border border-[#F6EFD9]/30 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <div className="flex items-center gap-6">
                {/* Item Image */}
                <div className="relative w-20 h-20 bg-gradient-to-br from-[#F6EFD9]/30 to-[#5BAAA7]/20 rounded-xl overflow-hidden flex-shrink-0">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#5BAAA7]/10 to-[#1A6A6A]/10"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-8 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-lg flex items-center justify-center">
                      <Tag className="w-4 h-4 text-white" />
                    </div>
                  </div>
                </div>

                {/* Item Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-bold text-[#1A6A6A] truncate">
                      {item.name}
                    </h3>
                    <div className="text-2xl font-bold bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
                      ${item.price}
                    </div>
                  </div>
                  
                  <p className="text-sm text-[#6b7b8c] mb-3 line-clamp-2">
                    {item.description}
                  </p>
                  
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-[#6b7b8c]" />
                      <span className="text-sm text-[#6b7b8c]">
                        {item.platforms.join(', ')}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-1">
                      {item.tags.slice(0, 2).map((tag, tagIndex) => (
                        <span key={tagIndex} className="px-2 py-1 bg-[#F6EFD9]/30 text-[#6b7b8c] rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                      {item.tags.length > 2 && (
                        <span className="px-2 py-1 bg-[#F6EFD9]/30 text-[#6b7b8c] rounded-full text-xs">
                          +{item.tags.length - 2}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Status & Actions */}
                <div className="flex items-center gap-3">
                  {postingItems.has(item.id) ? (
                    <div className="flex items-center gap-2 text-yellow-600">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-yellow-500 border-t-transparent rounded-full"
                      />
                      <span className="text-sm font-medium">Posting...</span>
                    </div>
                  ) : postedItems.has(item.id) ? (
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="w-5 h-5" />
                      <span className="text-sm font-medium">Posted</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handlePostItem(item.id)}
                        className="px-4 py-2 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
                      >
                        <Upload className="w-4 h-4" />
                        Post Now
                      </motion.button>
                      
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        className="p-2 text-[#6b7b8c] hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Success Modal */}
      <AnimatePresence>
        {showSuccessModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
            onClick={() => {
              setShowSuccessModal(false);
              onPostComplete();
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full text-center"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Confetti Animation */}
              <div className="relative mb-6">
                <motion.div
                  animate={{ 
                    scale: [1, 1.2, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{ duration: 0.6 }}
                  className="w-20 h-20 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center mx-auto mb-4"
                >
                  <Sparkles className="w-10 h-10 text-white" />
                </motion.div>
                
                {/* Confetti particles */}
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ 
                      opacity: [0, 1, 0],
                      scale: [0, 1, 0],
                      x: [0, (Math.random() - 0.5) * 200],
                      y: [0, (Math.random() - 0.5) * 200]
                    }}
                    transition={{ 
                      duration: 1.5,
                      delay: i * 0.1,
                      ease: "easeOut"
                    }}
                    className="absolute w-2 h-2 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] rounded-full"
                    style={{
                      left: '50%',
                      top: '50%',
                    }}
                  />
                ))}
              </div>

              <h2 className="text-2xl font-bold text-[#1A6A6A] mb-4">
                Successfully Posted!
              </h2>
              
              <div className="space-y-4 mb-6">
                <div className="text-3xl font-bold text-[#5BAAA7]">
                  Posted {postedCount} items
                </div>
                <div className="text-lg text-[#6b7b8c]">
                  Estimated Earnings: <span className="font-bold text-[#5BAAA7]">${totalValue}</span>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setShowSuccessModal(false);
                  onPostComplete();
                }}
                className="w-full px-6 py-3 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-xl hover:shadow-lg transition-all"
              >
                View Active Listings
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PostQueue;
