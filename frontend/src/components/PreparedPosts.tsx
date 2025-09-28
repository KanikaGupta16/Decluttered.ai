'use client';

import { motion, AnimatePresence } from 'framer-motion';
import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Check, 
  X, 
  DollarSign,
  Star,
  ShoppingBag,
  ArrowRight,
  Edit3,
  Eye,
  Tag,
  ExternalLink,
  Copy,
  Share2,
  Settings
} from 'lucide-react';

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

interface PreparedPost {
  id: string;
  item: DetectedObject;
  platform: string;
  title: string;
  description: string;
  price: number;
  tags: string[];
  status: 'ready' | 'draft' | 'published';
}

interface PreparedPostsProps {
  selectedItems: DetectedObject[];
  onBack: () => void;
  onContinue: (posts: PreparedPost[]) => void;
}

const PreparedPosts = ({ selectedItems, onBack, onContinue }: PreparedPostsProps) => {
  const [preparedPosts, setPreparedPosts] = useState<PreparedPost[]>([]);
  const [selectedPosts, setSelectedPosts] = useState<Set<string>>(new Set());
  const [showDetailModal, setShowDetailModal] = useState<string | null>(null);

  // Generate prepared posts for each selected item
  React.useEffect(() => {
    const posts: PreparedPost[] = selectedItems.flatMap(item => [
      {
        id: `${item.id}-ebay`,
        item,
        platform: 'eBay',
        title: `${item.name} - Excellent Condition`,
        description: `Selling my ${item.name} in excellent condition. Perfect for anyone looking for quality items. Item has been well-maintained and is ready for immediate use.`,
        price: item.estimatedValue,
        tags: ['furniture', 'home', 'quality'],
        status: 'ready' as const
      },
      {
        id: `${item.id}-facebook`,
        item,
        platform: 'Facebook Marketplace',
        title: `${item.name} - Great Deal!`,
        description: `Great ${item.name} for sale! Perfect condition, well-maintained. Great addition to any home. Contact me for more details!`,
        price: item.estimatedValue * 0.9, // Slightly lower for Facebook
        tags: ['local', 'home', 'furniture'],
        status: 'ready' as const
      }
    ]);
    setPreparedPosts(posts);
  }, [selectedItems]);

  const togglePostSelection = (postId: string) => {
    const newSelected = new Set(selectedPosts);
    if (newSelected.has(postId)) {
      newSelected.delete(postId);
    } else {
      newSelected.add(postId);
    }
    setSelectedPosts(newSelected);
  };

  const handleContinue = () => {
    const selected = preparedPosts.filter(post => selectedPosts.has(post.id));
    onContinue(selected);
  };

  const totalValue = Array.from(selectedPosts).reduce((sum, postId) => {
    const post = preparedPosts.find(p => p.id === postId);
    return sum + (post?.price || 0);
  }, 0);

  const platformColors = {
    'eBay': 'from-blue-500 to-blue-600',
    'Facebook Marketplace': 'from-blue-600 to-blue-700',
    'Craigslist': 'from-green-500 to-green-600',
    'OfferUp': 'from-purple-500 to-purple-600'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F6EFD9] via-white to-[#F6EFD9] overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-[#F6EFD9]/30">
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
            <h1 className="text-lg sm:text-xl font-bold text-black">Prepared Listings</h1>
            <p className="text-xs sm:text-sm text-black/70">
              {selectedPosts.size} of {preparedPosts.length} posts selected
            </p>
          </div>
          
          <div className="w-10 sm:w-12" /> {/* Spacer */}
        </div>
      </div>

      <div className="p-4 sm:p-6">
        <div className="max-w-6xl mx-auto">
          {/* Instructions */}
          <div className="mb-8">
            <div className="bg-white/80 rounded-2xl p-6 backdrop-blur-sm border border-[#F6EFD9]/30 shadow-lg">
              <div className="text-center">
                <h2 className="text-black text-xl font-semibold mb-2">Review Your Listings</h2>
                <p className="text-black/70 text-sm mb-4">
                  We've prepared optimized listings for each platform. Review and select which ones to post.
                </p>
                <div className="flex items-center justify-center gap-4 text-sm text-black/60">
                  <div className="flex items-center gap-1">
                    <Tag className="w-4 h-4 text-blue-500" />
                    <span>Auto-Optimized</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-4 h-4 text-green-500" />
                    <span>Price Optimized</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Check className="w-4 h-4 text-green-500" />
                    <span>Ready to Post</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Posts Grid */}
          <div className="mb-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AnimatePresence>
                {preparedPosts.map((post, index) => {
                  const isSelected = selectedPosts.has(post.id);
                  return (
                    <motion.div
                      key={post.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ delay: index * 0.1 }}
                      className={`relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 border-2 transition-all duration-300 cursor-pointer shadow-lg ${
                        isSelected 
                          ? 'border-teal-400 bg-teal-400/20 shadow-lg shadow-teal-400/20' 
                          : 'border-[#F6EFD9]/30 hover:border-[#F6EFD9]/50 hover:bg-white/90'
                      }`}
                      onClick={() => togglePostSelection(post.id)}
                    >
                      {/* Selection Indicator */}
                      <div className={`absolute top-4 right-4 w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                        isSelected 
                          ? 'bg-teal-400 border-teal-400 shadow-lg' 
                          : 'border-white/40 hover:border-white/60'
                      }`}>
                        {isSelected && <Check className="w-5 h-5 text-white" />}
                      </div>

                      {/* Platform Badge */}
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold text-white mb-4 bg-gradient-to-r ${platformColors[post.platform as keyof typeof platformColors] || 'from-gray-500 to-gray-600'}`}>
                        <ExternalLink className="w-3 h-3" />
                        {post.platform}
                      </div>

                      {/* Item Image */}
                      <div className="aspect-video bg-white/10 rounded-xl mb-4 flex items-center justify-center overflow-hidden">
                        <img
                          src={post.item.croppedImageUrl}
                          alt={post.item.name}
                          className="w-full h-full object-cover rounded-xl"
                        />
                      </div>

                      {/* Post Details */}
                      <div className="space-y-3">
                        <h3 className="text-black font-semibold text-lg line-clamp-2">
                          {post.title}
                        </h3>
                        
                        <p className="text-black/70 text-sm line-clamp-3">
                          {post.description}
                        </p>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <DollarSign className="w-5 h-5 text-green-500" />
                            <span className="text-green-500 font-bold text-xl">
                              ${post.price}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                            <span className="text-black/60 text-sm">Ready</span>
                          </div>
                        </div>

                        {/* Tags */}
                        <div className="flex flex-wrap gap-1">
                          {post.tags.map((tag, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-[#F6EFD9]/30 text-black/80 text-xs rounded-full"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-2 pt-2">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setShowDetailModal(post.id);
                            }}
                            className="flex-1 px-3 py-2 bg-[#F6EFD9]/30 text-black text-sm rounded-lg hover:bg-[#F6EFD9]/50 transition-all flex items-center justify-center gap-1"
                          >
                            <Eye className="w-4 h-4" />
                            Preview
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              // Edit functionality
                            }}
                            className="flex-1 px-3 py-2 bg-[#F6EFD9]/30 text-black text-sm rounded-lg hover:bg-[#F6EFD9]/50 transition-all flex items-center justify-center gap-1"
                          >
                            <Edit3 className="w-4 h-4" />
                            Edit
                          </motion.button>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          </div>

          {/* Selection Summary */}
          {selectedPosts.size > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-teal-500/20 to-cyan-500/20 backdrop-blur-sm rounded-2xl p-6 border border-teal-400/30 mb-8"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white text-lg font-semibold mb-1">
                    {selectedPosts.size} listings ready
                  </h3>
                  <p className="text-white/70 text-sm">
                    Total estimated value: <span className="text-green-400 font-semibold">${totalValue}</span>
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleContinue}
                  className="px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                >
                  <ShoppingBag className="w-5 h-5" />
                  Post to Queue
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Empty State */}
          {selectedPosts.size === 0 && (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShoppingBag className="w-10 h-10 text-white/60" />
              </div>
              <h3 className="text-white text-lg font-semibold mb-2">No listings selected</h3>
              <p className="text-white/60 text-sm">
                Select listings above to add them to your posting queue
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {showDetailModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setShowDetailModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white/10 backdrop-blur-md rounded-2xl p-6 max-w-2xl w-full border border-white/20 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white text-lg font-semibold">Listing Preview</h3>
                <button
                  onClick={() => setShowDetailModal(null)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-all"
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>
              
              {(() => {
                const post = preparedPosts.find(p => p.id === showDetailModal);
                if (!post) return null;
                
                return (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`px-3 py-1 rounded-full text-xs font-semibold text-white bg-gradient-to-r ${platformColors[post.platform as keyof typeof platformColors] || 'from-gray-500 to-gray-600'}`}>
                        {post.platform}
                      </div>
                      <div className="text-green-400 font-semibold text-lg">
                        ${post.price}
                      </div>
                    </div>
                    
                    <div className="aspect-video bg-white/10 rounded-xl overflow-hidden mb-4">
                      <img
                        src={post.item.croppedImageUrl}
                        alt={post.item.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    
                    <div>
                      <h4 className="text-white font-semibold text-lg mb-2">{post.title}</h4>
                      <p className="text-white/70 text-sm mb-4">{post.description}</p>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        {post.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-white/20 text-white/80 text-xs rounded-full"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                      
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="flex-1 px-4 py-2 bg-white/20 text-white text-sm rounded-lg hover:bg-white/30 transition-all flex items-center justify-center gap-2"
                        >
                          <Copy className="w-4 h-4" />
                          Copy Text
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="flex-1 px-4 py-2 bg-white/20 text-white text-sm rounded-lg hover:bg-white/30 transition-all flex items-center justify-center gap-2"
                        >
                          <Share2 className="w-4 h-4" />
                          Share
                        </motion.button>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PreparedPosts;
