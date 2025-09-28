'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { 
  Camera, 
  Clock, 
  Play, 
  Upload, 
  History, 
  Activity, 
  BarChart3, 
  DollarSign, 
  Eye, 
  Tag, 
  MessageCircle, 
  CheckCircle, 
  XCircle,
  ShoppingCart,
  TrendingUp,
  Users,
  Package,
  CheckSquare,
  Square,
  Edit3,
  Trash2,
  Plus,
  ArrowRight,
  Zap,
  PieChart
} from 'lucide-react';
import Image from 'next/image';
import { ThemeToggle } from '@/components/ThemeToggle';
import DeclutterFlow from '@/components/DeclutterFlow';

const Card = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className={`rounded-2xl border border-[#F6EFD9]/30 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300 ${className}`}
  >
    {children}
  </motion.div>
);

// Mock data for detected items
const mockDetectedItems = [
  {
    id: 1,
    name: "Gaming Chair",
    image: "/vercel.svg",
    estimatedValue: 120,
    condition: "Good",
    category: "Furniture"
  },
  {
    id: 2,
    name: "Laptop",
    image: "/vercel.svg", 
    estimatedValue: 450,
    condition: "Like New",
    category: "Electronics"
  },
  {
    id: 3,
    name: "Dining Table",
    image: "/vercel.svg",
    estimatedValue: 200,
    condition: "Used",
    category: "Furniture"
  },
  {
    id: 4,
    name: "TV",
    image: "/vercel.svg",
    estimatedValue: 300,
    condition: "Good",
    category: "Electronics"
  },
  {
    id: 5,
    name: "Mouse",
    image: "/vercel.svg",
    estimatedValue: 25,
    condition: "Like New",
    category: "Electronics"
  },
  {
    id: 6,
    name: "Cell Phone",
    image: "/vercel.svg",
    estimatedValue: 150,
    condition: "Good",
    category: "Electronics"
  }
];

// Mock data for listings
const mockListings = [
  {
    id: 1,
    title: "Gaming Chair - Ergonomic Office Chair",
    price: 120,
    description: "Comfortable gaming chair with lumbar support. Barely used, excellent condition.",
    tags: ["Gaming", "Office", "Ergonomic"],
    status: "Ready to Post",
    platform: null,
    originalLink: null
  },
  {
    id: 2,
    title: "MacBook Pro 13-inch - 2020 Model",
    price: 450,
    description: "Lightly used MacBook Pro in excellent condition. Perfect for students or professionals.",
    tags: ["Laptop", "Apple", "Professional"],
    status: "Posted",
    platform: "Facebook Marketplace",
    originalLink: "https://facebook.com/marketplace/item/123456"
  },
  {
    id: 3,
    title: "Vintage Camera Collection",
    price: 85,
    description: "Rare vintage cameras in excellent working condition. Perfect for collectors.",
    tags: ["Vintage", "Camera", "Collectible"],
    status: "Posted",
    platform: "eBay",
    originalLink: "https://ebay.com/itm/123456789"
  },
  {
    id: 4,
    title: "Designer Handbag - Louis Vuitton",
    price: 650,
    description: "Authentic designer handbag, gently used. Comes with original packaging.",
    tags: ["Fashion", "Luxury", "Handbag"],
    status: "Ready to Post",
    platform: null,
    originalLink: null
  },
  {
    id: 5,
    title: "Nike Air Jordan Sneakers",
    price: 180,
    description: "Limited edition Air Jordan 1s, size 10. Worn only a few times.",
    tags: ["Sneakers", "Nike", "Limited Edition"],
    status: "Posted",
    platform: "Facebook Marketplace",
    originalLink: "https://facebook.com/marketplace/item/789012"
  },
  {
    id: 6,
    title: "Vintage Vinyl Records",
    price: 65,
    description: "Collection of classic rock vinyl records from the 70s and 80s.",
    tags: ["Music", "Vintage", "Collectible"],
    status: "Posted",
    platform: "eBay",
    originalLink: "https://ebay.com/itm/987654321"
  }
];

// Mock data for offers
const mockOffers = [
  {
    id: 1,
    itemName: "Gaming Chair",
    buyer: "John D.",
    amount: 110,
    message: "Is this still available? Can you do $110?",
    isBestOffer: false,
    platform: "Facebook Marketplace"
  },
  {
    id: 2,
    itemName: "Gaming Chair", 
    buyer: "Sarah M.",
    amount: 125,
    message: "I can pick up today for $125",
    isBestOffer: true,
    platform: "eBay"
  },
  {
    id: 3,
    itemName: "Gaming Chair",
    buyer: "Mike R.",
    amount: 120,
    message: "Would you accept $120? I'm local.",
    isBestOffer: false,
    platform: "Craigslist"
  }
];

// Mock data for marketplace posting
const mockPostingStatus = [
  {
    id: 1,
    itemName: "Gaming Chair",
    platforms: [
      { name: "eBay", status: "Posted", progress: 100 },
      { name: "Facebook Marketplace", status: "Posting", progress: 75 },
      { name: "Craigslist", status: "Pending", progress: 0 }
    ]
  },
  {
    id: 2,
    itemName: "MacBook Pro",
    platforms: [
      { name: "eBay", status: "Posted", progress: 100 },
      { name: "Facebook Marketplace", status: "Posted", progress: 100 },
      { name: "Mercari", status: "Posting", progress: 50 }
    ]
  }
];

// Mock data for sales
const mockSales = [
  {
    id: 1,
    itemName: "Gaming Chair",
    soldPrice: 125,
    status: "Sold",
    date: "2024-01-15",
    platform: "eBay"
  },
  {
    id: 2,
    itemName: "Old Books",
    soldPrice: 0,
    status: "Listed",
    offers: 2,
    date: "2024-01-14",
    platform: "Facebook Marketplace"
  },
  {
    id: 3,
    itemName: "Lamp",
    soldPrice: 0,
    status: "Pending Listing",
    date: "2024-01-13",
    platform: "Pending"
  }
];

type TabType = 'declutter' | 'listings' | 'offers' | 'sales';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('declutter');
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [totalEarnings] = useState(450);
  const [showDeclutterFlow, setShowDeclutterFlow] = useState(false);

  const handleItemSelection = (itemId: number) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const renderDeclutterTab = () => (
    <div className="space-y-8">
      {/* Original Start Decluttering Section */}
      <div className="relative -mx-6 overflow-hidden bg-gradient-to-br from-[#F6EFD9]/20 via-white to-[#F6EFD9]/10 py-20 text-center">
        {/* Floating Bubbles */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute top-20 left-20 w-16 h-16 bg-gradient-to-br from-[#5BAAA7]/20 to-[#1A6A6A]/20 rounded-full blur-sm"
            animate={{
              y: [0, -20, 0],
              x: [0, 10, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute top-32 right-24 w-12 h-12 bg-gradient-to-br from-[#5BAAA7]/15 to-[#1A6A6A]/15 rounded-full blur-sm"
            animate={{
              y: [0, 15, 0],
              x: [0, -8, 0],
              scale: [1, 0.9, 1],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1,
            }}
          />
          <motion.div
            className="absolute bottom-24 left-32 w-20 h-20 bg-gradient-to-br from-[#5BAAA7]/10 to-[#1A6A6A]/10 rounded-full blur-sm"
            animate={{
              y: [0, -12, 0],
              x: [0, 15, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 2,
            }}
          />
          <motion.div
            className="absolute bottom-32 right-16 w-14 h-14 bg-gradient-to-br from-[#5BAAA7]/25 to-[#1A6A6A]/25 rounded-full blur-sm"
            animate={{
              y: [0, 18, 0],
              x: [0, -12, 0],
              scale: [1, 0.8, 1],
            }}
            transition={{
              duration: 9,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.5,
            }}
          />
          <motion.div
            className="absolute top-48 left-1/2 w-8 h-8 bg-gradient-to-br from-[#5BAAA7]/30 to-[#1A6A6A]/30 rounded-full blur-sm"
            animate={{
              y: [0, -25, 0],
              x: [0, 20, 0],
              scale: [1, 1.3, 1],
            }}
            transition={{
              duration: 11,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1.5,
            }}
          />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-4xl mx-auto px-6">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-5xl sm:text-6xl font-extrabold mb-4"
          >
            <span className="bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
              Declutter your space.
            </span>
          </motion.h1>
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-2xl sm:text-3xl font-semibold text-black mb-8"
          >
            Earn effortlessly.
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-lg text-gray-500 mb-10 max-w-2xl mx-auto text-center"
          >
            Scan your room and let AI detect what you can sell.
          </motion.p>
          
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            whileHover={{ 
              scale: 1.02,
              boxShadow: "0 0 30px rgba(91, 170, 167, 0.4)"
            }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowDeclutterFlow(true)}
            className="px-12 py-5 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-bold text-xl rounded-xl shadow-lg hover:shadow-[0_0_30px_rgba(91,170,167,0.4)] transition-all duration-300"
          >
            Start Decluttering
          </motion.button>
        </div>
      </div>

      {/* Curved Gradient Divider */}
      <div className="relative -mx-6 overflow-hidden">
        <svg 
          className="w-full h-24" 
          viewBox="0 0 1200 120" 
          preserveAspectRatio="none"
        >
          <path 
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" 
            fill="url(#gradient1)" 
            opacity="0.25"
          />
          <path 
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" 
            fill="url(#gradient2)" 
            opacity="0.5"
          />
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#5BAAA7" />
              <stop offset="100%" stopColor="#1A6A6A" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#F6EFD9" />
              <stop offset="100%" stopColor="#5BAAA7" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Analytics Section with Welcome */}
      <div className="relative -mx-6 bg-gradient-to-br from-[#F6EFD9]/5 via-white to-[#F6EFD9]/10 py-16">
        <div className="max-w-7xl mx-auto px-6">
          {/* Subtle Welcome Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <p className="text-sm text-gray-500 font-medium">
              Your journey so far:
            </p>
          </motion.div>

          {/* Analytics Grid - 3 Equal Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {/* Total Earnings Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              whileHover={{ scale: 1.02, y: -2, transition: { duration: 0.2 } }}
              onClick={() => setActiveTab('sales')}
              className="relative rounded-xl bg-white p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 group cursor-pointer"
            >
              <div className="absolute top-4 left-4 w-12 h-12 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center shadow-sm">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div className="pt-6 text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">${totalEarnings}</div>
                <h3 className="text-sm font-semibold text-gray-600 mb-1">Total Earnings</h3>
                <div className="text-xs text-gray-500">This month</div>
                <div className="mt-3 text-xs text-green-600 font-medium">+12% from last month</div>
              </div>
            </motion.div>

            {/* Active Listings Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              whileHover={{ scale: 1.02, y: -2, transition: { duration: 0.2 } }}
              onClick={() => setActiveTab('listings')}
              className="relative rounded-xl bg-white p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 group cursor-pointer"
            >
              <div className="absolute top-4 left-4 w-12 h-12 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center shadow-sm">
                <Package className="w-6 h-6 text-white" />
              </div>
              <div className="pt-6 text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">12</div>
                <h3 className="text-sm font-semibold text-gray-600 mb-1">Active Listings</h3>
                <div className="text-xs text-gray-500">Across 3 marketplaces</div>
                <div className="mt-3 text-xs text-blue-600 font-medium">8 new this week</div>
              </div>
            </motion.div>

            {/* Actions Awaiting Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              whileHover={{ scale: 1.02, y: -2, transition: { duration: 0.2 } }}
              onClick={() => setActiveTab('offers')}
              className="relative rounded-xl bg-white p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 group cursor-pointer"
            >
              <div className="absolute top-4 left-4 w-12 h-12 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center shadow-sm">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div className="absolute top-4 right-4 w-6 h-6 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] rounded-full flex items-center justify-center shadow-sm">
                <span className="text-white text-xs font-bold">4</span>
              </div>
              <div className="pt-6 text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">4</div>
                <h3 className="text-sm font-semibold text-gray-600 mb-1">Actions Awaiting</h3>
                <div className="text-xs text-gray-500">New offers pending</div>
                <div className="mt-3 text-xs text-orange-600 font-medium">2 urgent responses</div>
              </div>
            </motion.div>
          </div>
        </div>

          {/* Recent Activity Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-12"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Recent Declutter Progress</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { action: "Sold Gaming Chair", amount: "$125", platform: "eBay", time: "2 hours ago", status: "success" },
                { action: "Listed MacBook Pro", amount: "$450", platform: "Facebook", time: "1 day ago", status: "active" },
                { action: "Received offer on TV", amount: "$280", platform: "Craigslist", time: "2 days ago", status: "pending" },
                { action: "Sold Vintage Camera", amount: "$85", platform: "eBay", time: "3 days ago", status: "success" },
                { action: "Listed Designer Handbag", amount: "$650", platform: "Mercari", time: "4 days ago", status: "active" },
                { action: "Sold Nike Sneakers", amount: "$180", platform: "Facebook", time: "5 days ago", status: "success" }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300"
                >
                  <div className={`w-3 h-3 rounded-full ${
                    item.status === 'success' ? 'bg-green-500' :
                    item.status === 'active' ? 'bg-blue-500' :
                    'bg-orange-500'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.action}</p>
                    <p className="text-xs text-gray-500">{item.platform} • {item.time}</p>
                  </div>
                  <div className="text-sm font-semibold text-gray-900">{item.amount}</div>
                </motion.div>
              ))}
            </div>
        </motion.div>
      </div>
    </div>
  );

  const renderListingsTab = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-[#0a1b2a]">
          Approve your listings — AI has priced and described them for you
        </h2>
        <button className="px-6 py-3 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all inline-flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Add New Listing
        </button>
      </div>

      {/* 3-Column Card Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockListings.map((listing) => (
          <motion.div
            key={listing.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            whileHover={{ scale: 1.02, y: -5 }}
            className="group cursor-pointer"
          >
            <Card className="p-0 overflow-hidden max-w-sm mx-auto w-full">
              {/* Item Image */}
              <div className="relative h-48 bg-gradient-to-br from-[#F6EFD9]/30 to-[#5BAAA7]/20 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#5BAAA7]/10 to-[#1A6A6A]/10"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] rounded-xl flex items-center justify-center shadow-lg">
                    <Tag className="w-8 h-8 text-white" />
                  </div>
                </div>
                {/* Status Badge */}
                <div className="absolute top-3 right-3">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                    listing.status === 'Posted' 
                      ? 'bg-green-100 text-green-800 border border-green-200' 
                      : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                  }`}>
                    {listing.status}
                  </span>
                </div>
              </div>

              {/* Card Content */}
              <div className="p-6">
                {/* Title */}
                <h3 className="text-lg font-bold text-[#0a1b2a] mb-3 line-clamp-2 group-hover:text-[#5BAAA7] transition-colors">
                  {listing.title}
                </h3>
                
                {/* Price */}
                <div className="mb-4">
                  <p className="text-2xl font-bold bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
                    ${listing.price}
                  </p>
                  {listing.platform ? (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-[#6b7b8c]">{listing.platform}</span>
                      {listing.originalLink && (
                        <a 
                          href={listing.originalLink} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-[#5BAAA7] hover:text-[#1A6A6A] transition-colors"
                        >
                          <ArrowRight className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-[#6b7b8c]">Ready to post</p>
                  )}
                </div>

                {/* Description */}
                <p className="text-sm text-[#6b7b8c] mb-4 line-clamp-2">
                  {listing.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {listing.tags.slice(0, 2).map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-[#F6EFD9]/30 text-[#6b7b8c] rounded-full text-xs">
                      {tag}
                    </span>
                  ))}
                  {listing.tags.length > 2 && (
                    <span className="px-2 py-1 bg-[#F6EFD9]/30 text-[#6b7b8c] rounded-full text-xs">
                      +{listing.tags.length - 2}
                    </span>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-[#F6EFD9]/30">
                  {listing.status === 'Ready to Post' ? (
                    <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all">
                      <Tag className="w-4 h-4" />
                      Post Now
                    </button>
                  ) : (
                    <div className="flex items-center gap-2">
                      <a 
                        href={listing.originalLink || '#'} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all"
                      >
                        <ArrowRight className="w-4 h-4" />
                        View Post
                      </a>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <button className="p-2 text-[#6b7b8c] hover:text-[#5BAAA7] transition-colors">
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-[#6b7b8c] hover:text-red-500 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderOffersTab = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-[#0a1b2a]">
          All your buyer messages in one place. AI highlights the best deals.
        </h2>
        <div className="text-sm text-[#6b7b8c]">
          {mockOffers.length} new offers
        </div>
      </div>

      <div className="space-y-6">
        {mockOffers.map((offer) => (
          <Card key={offer.id} className={offer.isBestOffer ? 'ring-2 ring-[#0ecfba] bg-gradient-to-br from-[#0ecfba]/5 to-[#1dd2aa]/5' : ''}>
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-[#0a1b2a]">
                      {offer.itemName}
                    </h3>
                    {offer.isBestOffer && (
                      <span className="px-3 py-1 bg-[#0ecfba]/10 text-[#0ecfba] rounded-full text-sm font-medium">
                        Best Offer
                      </span>
                    )}
                  </div>
                  <div className="text-2xl font-bold text-[#0ecfba] mb-2">
                    ${offer.amount}
                  </div>
                  <div className="text-sm text-[#6b7b8c] mb-3">
                    from {offer.buyer} via {offer.platform}
                  </div>
                  <p className="text-[#0a1b2a]">
                    {offer.message}
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3 pt-4 border-t border-slate-200">
                <button className="px-4 py-2 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 transition-colors">
                  Accept
                </button>
                <button className="px-4 py-2 border border-[#0ecfba] text-[#0ecfba] font-semibold rounded-lg hover:bg-[#0ecfba] hover:text-white transition-colors">
                  Counteroffer
                </button>
                <button className="px-4 py-2 border border-slate-300 text-[#6b7b8c] font-semibold rounded-lg hover:bg-slate-100 transition-colors">
                  Wait
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderPostingTab = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#0a1b2a] mb-2">
          Marketplace Posting Progress
        </h2>
        <p className="text-[#6b7b8c]">
          Track where your items are being posted across platforms
        </p>
      </div>

      <div className="space-y-6">
        {mockPostingStatus.map((item) => (
          <Card key={item.id}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-[#0a1b2a]">
                  {item.itemName}
                </h3>
                <div className="text-sm text-[#6b7b8c]">
                  {item.platforms.filter(p => p.status === 'Posted').length} of {item.platforms.length} posted
                </div>
              </div>
              
              <div className="space-y-4">
                {item.platforms.map((platform, index) => (
                  <div key={index} className="flex items-center justify-between p-4 rounded-xl bg-slate-50">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-[#0ecfba] to-[#1dd2aa] rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-sm">{platform.name.charAt(0)}</span>
                      </div>
                      <div>
                        <div className="font-semibold text-[#0a1b2a]">{platform.name}</div>
                        <div className="text-sm text-[#6b7b8c]">
                          {platform.status === 'Posted' ? 'Live' : 
                           platform.status === 'Posting' ? 'Posting...' : 'Pending'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className="w-32 bg-slate-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-[#0ecfba] to-[#1dd2aa] h-2 rounded-full transition-all duration-500"
                          style={{ width: `${platform.progress}%` }}
                        />
                      </div>
                      <div className="text-sm font-medium text-[#6b7b8c]">
                        {platform.progress}%
                      </div>
                      <div className={`w-3 h-3 rounded-full ${
                        platform.status === 'Posted' ? 'bg-green-500' :
                        platform.status === 'Posting' ? 'bg-yellow-500 animate-pulse' :
                        'bg-slate-400'
                      }`} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderSalesTab = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#0a1b2a] mb-2">
          Your Clutter → Cash Journey
        </h2>
        <div className="text-4xl font-bold text-[#0ecfba] mb-4">
          Total Earnings: ${totalEarnings} this month
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#0ecfba] to-[#1dd2aa] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">${totalEarnings}</div>
            <div className="text-[#6b7b8c]">Total Earnings</div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#1dd2aa] to-[#e8fdfc] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Package className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">12</div>
            <div className="text-[#6b7b8c]">Items Listed</div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#e8fdfc] to-[#0ecfba] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">8</div>
            <div className="text-[#6b7b8c]">Items Sold</div>
          </div>
        </Card>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-4 mb-6">
          <button className="px-4 py-2 bg-[#0ecfba] text-white font-semibold rounded-lg">All</button>
          <button className="px-4 py-2 border border-slate-300 text-[#6b7b8c] font-semibold rounded-lg hover:bg-slate-100 transition-colors">Active</button>
          <button className="px-4 py-2 border border-slate-300 text-[#6b7b8c] font-semibold rounded-lg hover:bg-slate-100 transition-colors">Sold</button>
        </div>

        {mockSales.map((sale) => (
          <Card key={sale.id}>
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-[#0a1b2a] mb-2">
                    {sale.itemName}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-[#6b7b8c]">
                    <span>{sale.date}</span>
                    <span>•</span>
                    <span>{sale.platform}</span>
                  </div>
                </div>
                <div className="text-right">
                  {sale.status === 'Sold' ? (
                    <div className="text-2xl font-bold text-green-600">
                      ${sale.soldPrice}
                    </div>
                  ) : sale.status === 'Listed' ? (
                    <div className="text-lg font-semibold text-blue-600">
                      {sale.offers} offers
                    </div>
                  ) : (
                    <div className="text-lg font-semibold text-orange-600">
                      Pending
                    </div>
                  )}
                  <div className={`text-sm font-medium ${
                    sale.status === 'Sold' 
                      ? 'text-green-600'
                      : sale.status === 'Listed'
                      ? 'text-blue-600'
                      : 'text-orange-600'
                  }`}>
                    {sale.status}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  if (showDeclutterFlow) {
    return (
      <DeclutterFlow
        onComplete={() => setShowDeclutterFlow(false)}
        onBack={() => setShowDeclutterFlow(false)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F6EFD9]/10 via-white to-[#F6EFD9]/5">
      {/* Header */}
      <header className="sticky top-0 z-20 backdrop-blur-md border-b border-[#F6EFD9]/30 bg-white/95">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            <span className="text-[#5BAAA7]">de</span>
            <span className="text-slate-900">Cluttered</span>
            <span className="text-[#5BAAA7]">.ai</span>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="sticky top-16 z-10 bg-white/90 backdrop-blur-md border-b border-[#F6EFD9]/30">
        <div className="mx-auto max-w-7xl px-6">
          <nav className="flex space-x-8">
            {[
              { id: 'declutter', label: 'Declutter', icon: Eye },
              { id: 'listings', label: 'Listings', icon: Tag },
              { id: 'offers', label: 'Messages', icon: MessageCircle },
              { id: 'sales', label: 'Sales', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center gap-2 px-4 py-4 border-b-2 font-semibold transition-colors ${
                  activeTab === tab.id
                    ? 'border-[#5BAAA7] text-[#5BAAA7]'
                    : 'border-transparent text-[#6b7b8c] hover:text-[#0a1b2a]'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        {activeTab === 'declutter' && renderDeclutterTab()}
        {activeTab === 'listings' && renderListingsTab()}
        {activeTab === 'offers' && renderOffersTab()}
        {activeTab === 'sales' && renderSalesTab()}
      </main>
    </div>
  );
}
