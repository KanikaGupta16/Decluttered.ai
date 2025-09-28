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
  Tag
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

interface ItemSelectionProps {
  detectedObjects: DetectedObject[];
  onBack: () => void;
  onItemsSelected: (selectedItems: DetectedObject[]) => void;
}

const ItemSelection = ({ detectedObjects, onBack, onItemsSelected }: ItemSelectionProps) => {
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [showDetailModal, setShowDetailModal] = useState<string | null>(null);

  const toggleItemSelection = (itemId: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
  };

  const handleContinue = () => {
    const selected = detectedObjects.filter(item => selectedItems.has(item.id));
    onItemsSelected(selected);
  };

  const totalValue = Array.from(selectedItems).reduce((sum, itemId) => {
    const item = detectedObjects.find(obj => obj.id === itemId);
    return sum + (item?.estimatedValue || 0);
  }, 0);

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
            <h1 className="text-lg sm:text-xl font-bold text-black">Select Items to Sell</h1>
            <p className="text-xs sm:text-sm text-black/70">
              {selectedItems.size} of {detectedObjects.length} items selected
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
                <h2 className="text-black text-xl font-semibold mb-2">Choose Items to Sell</h2>
                <p className="text-black/70 text-sm mb-4">
                  Select the items you want to sell. We'll help you create optimized listings for each platform.
                </p>
                <div className="flex items-center justify-center gap-4 text-sm text-black/60">
                  <div className="flex items-center gap-1">
                    <Check className="w-4 h-4 text-green-500" />
                    <span>AI Detected</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-4 h-4 text-green-500" />
                    <span>Price Estimated</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Tag className="w-4 h-4 text-blue-500" />
                    <span>Auto-Tagged</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Items Grid */}
          <div className="mb-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              <AnimatePresence>
                {detectedObjects.map((item, index) => {
                  const isSelected = selectedItems.has(item.id);
                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ delay: index * 0.1 }}
                      className={`relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 border-2 transition-all duration-300 cursor-pointer shadow-lg ${
                        isSelected 
                          ? 'border-teal-400 bg-teal-400/20 shadow-lg shadow-teal-400/20' 
                          : 'border-[#F6EFD9]/30 hover:border-[#F6EFD9]/50 hover:bg-white/90'
                      }`}
                      onClick={() => toggleItemSelection(item.id)}
                    >
                      {/* Selection Indicator */}
                      <div className={`absolute top-4 right-4 w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                        isSelected 
                          ? 'bg-teal-400 border-teal-400 shadow-lg' 
                          : 'border-white/40 hover:border-white/60'
                      }`}>
                        {isSelected && <Check className="w-5 h-5 text-white" />}
                      </div>

                      {/* Item Image */}
                      <div className="aspect-square bg-white/10 rounded-xl mb-4 flex items-center justify-center overflow-hidden">
                        <img
                          src={item.croppedImageUrl}
                          alt={item.name}
                          className="w-full h-full object-cover rounded-xl"
                        />
                      </div>

                      {/* Item Info */}
                      <div className="space-y-3">
                        <h3 className="text-black font-semibold text-lg truncate">
                          {item.name}
                        </h3>
                        
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                            <span className="text-black/70 text-sm">
                              {(item.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <DollarSign className="w-5 h-5 text-green-500" />
                            <span className="text-green-500 font-bold text-xl">
                              ${item.estimatedValue}
                            </span>
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-2 pt-2">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setShowDetailModal(item.id);
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
          {selectedItems.size > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-teal-500/20 to-cyan-500/20 backdrop-blur-sm rounded-2xl p-6 border border-teal-400/30 mb-8"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white text-lg font-semibold mb-1">
                    {selectedItems.size} items selected
                  </h3>
                  <p className="text-white/70 text-sm">
                    Estimated total value: <span className="text-green-400 font-semibold">${totalValue}</span>
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleContinue}
                  className="px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                >
                  <ShoppingBag className="w-5 h-5" />
                  Prepare Listings
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Empty State */}
          {selectedItems.size === 0 && (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShoppingBag className="w-10 h-10 text-white/60" />
              </div>
              <h3 className="text-white text-lg font-semibold mb-2">No items selected</h3>
              <p className="text-white/60 text-sm">
                Select items above to create your listings
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
              className="bg-white/10 backdrop-blur-md rounded-2xl p-6 max-w-md w-full border border-white/20"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white text-lg font-semibold">Item Preview</h3>
                <button
                  onClick={() => setShowDetailModal(null)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-all"
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="aspect-square bg-white/10 rounded-xl overflow-hidden">
                  <img
                    src={detectedObjects.find(item => item.id === showDetailModal)?.croppedImageUrl}
                    alt="Item preview"
                    className="w-full h-full object-cover"
                  />
                </div>
                
                <div className="text-center">
                  <h4 className="text-white font-semibold text-lg mb-2">
                    {detectedObjects.find(item => item.id === showDetailModal)?.name}
                  </h4>
                  <p className="text-green-400 font-bold text-xl">
                    ${detectedObjects.find(item => item.id === showDetailModal)?.estimatedValue}
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ItemSelection;
