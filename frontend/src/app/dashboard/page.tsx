'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
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
  PieChart,
  Brain,
  Globe,
  Target,
  Award,
  Percent,
  Calendar,
  Mail,
  Phone,
  Star,
  AlertCircle,
  Filter,
  Search,
  Download,
  Share2,
  Settings
} from 'lucide-react';
import Image from 'next/image';
import { ThemeToggle } from '@/components/ThemeToggle';
import DeclutterFlow from '@/components/DeclutterFlow';
import AIChatbot from '@/components/AIChatbot';
import ListingDetailModal from '@/components/ListingDetailModal';
import { AnimatePresence } from 'framer-motion';

type TabType = 'declutter' | 'listings' | 'offers' | 'sales' | 'analytics' | 'ai';

// Enhanced mock data with platform analytics
const mockPlatformStats = {
  facebook: {
    totalListings: 28,
    activeBuyers: 156,
    avgTimeToSell: 3.2,
    avgSalePrice: 180,
    successRate: 0.73,
    monthlyTrend: '+23%',
    topCategories: ['Electronics', 'Furniture', 'Clothing'],
    recentSales: [
      { item: 'iPhone 12', price: 450, date: '2 days ago' },
      { item: 'Gaming Chair', price: 125, date: '4 days ago' },
      { item: 'Laptop Stand', price: 35, date: '1 week ago' }
    ]
  },
  ebay: {
    totalListings: 34,
    activeBuyers: 89,
    avgTimeToSell: 5.8,
    avgSalePrice: 220,
    successRate: 0.68,
    monthlyTrend: '+15%',
    topCategories: ['Collectibles', 'Electronics', 'Books'],
    recentSales: [
      { item: 'Vintage Camera', price: 380, date: '1 day ago' },
      { item: 'Comic Books', price: 95, date: '3 days ago' },
      { item: 'Tablet', price: 280, date: '5 days ago' }
    ]
  },
  mercari: {
    totalListings: 15,
    activeBuyers: 45,
    avgTimeToSell: 4.1,
    avgSalePrice: 95,
    successRate: 0.61,
    monthlyTrend: '+8%',
    topCategories: ['Fashion', 'Beauty', 'Electronics'],
    recentSales: [
      { item: 'Designer Bag', price: 150, date: '6 days ago' },
      { item: 'Sneakers', price: 75, date: '1 week ago' }
    ]
  }
};

// Complex detected items with detailed analytics
const mockDetectedItems = [
  {
    id: 1,
    name: "Gaming Chair",
    image: "/vercel.svg",
    estimatedValue: 120,
    condition: "Good",
    category: "Furniture",
    confidence: 0.92,
    marketDemand: "High",
    priceRange: { min: 80, max: 150 },
    platformRecommendations: {
      facebook: { price: 125, timeToSell: 3 },
      ebay: { price: 135, timeToSell: 5 },
      mercari: { price: 110, timeToSell: 4 }
    },
    similarSold: 47,
    trendDirection: 'up',
    seasonality: 'neutral'
  },
  {
    id: 2,
    name: "MacBook Pro 13-inch",
    image: "/vercel.svg", 
    estimatedValue: 680,
    condition: "Like New",
    category: "Electronics",
    confidence: 0.96,
    marketDemand: "Very High",
    priceRange: { min: 600, max: 750 },
    platformRecommendations: {
      facebook: { price: 695, timeToSell: 2 },
      ebay: { price: 720, timeToSell: 3 },
      mercari: { price: 660, timeToSell: 4 }
    },
    similarSold: 134,
    trendDirection: 'up',
    seasonality: 'back-to-school-boost'
  },
  {
    id: 3,
    name: "Dining Table Set",
    image: "/vercel.svg",
    estimatedValue: 320,
    condition: "Used",
    category: "Furniture",
    confidence: 0.89,
    marketDemand: "Medium",
    priceRange: { min: 280, max: 380 },
    platformRecommendations: {
      facebook: { price: 340, timeToSell: 7 },
      ebay: { price: 360, timeToSell: 10 },
      mercari: { price: 300, timeToSell: 8 }
    },
    similarSold: 23,
    trendDirection: 'stable',
    seasonality: 'moving-season'
  },
  {
    id: 4,
    name: "4K Smart TV",
    image: "/vercel.svg",
    estimatedValue: 420,
    condition: "Good",
    category: "Electronics",
    confidence: 0.94,
    marketDemand: "High",
    priceRange: { min: 350, max: 500 },
    platformRecommendations: {
      facebook: { price: 435, timeToSell: 4 },
      ebay: { price: 465, timeToSell: 6 },
      mercari: { price: 395, timeToSell: 5 }
    },
    similarSold: 89,
    trendDirection: 'up',
    seasonality: 'holiday-prep'
  },
  {
    id: 5,
    name: "Wireless Mouse",
    image: "/vercel.svg",
    estimatedValue: 25,
    condition: "Like New",
    category: "Electronics",
    confidence: 0.87,
    marketDemand: "Medium",
    priceRange: { min: 18, max: 35 },
    platformRecommendations: {
      facebook: { price: 28, timeToSell: 5 },
      ebay: { price: 32, timeToSell: 7 },
      mercari: { price: 24, timeToSell: 6 }
    },
    similarSold: 156,
    trendDirection: 'stable',
    seasonality: 'work-from-home'
  },
  {
    id: 6,
    name: "iPhone 11",
    image: "/vercel.svg",
    estimatedValue: 280,
    condition: "Good",
    category: "Electronics",
    confidence: 0.98,
    marketDemand: "Very High",
    priceRange: { min: 250, max: 320 },
    platformRecommendations: {
      facebook: { price: 295, timeToSell: 1 },
      ebay: { price: 315, timeToSell: 2 },
      mercari: { price: 275, timeToSell: 3 }
    },
    similarSold: 312,
    trendDirection: 'up',
    seasonality: 'upgrade-cycle'
  }
];

// Enhanced listings with detailed platform data
const mockListings = [
  {
    id: 1,
    title: "Gaming Chair - Ergonomic Office Chair with Lumbar Support",
    price: 125,
    originalPrice: 135,
    description: "Comfortable gaming chair with lumbar support. Barely used, excellent condition. Perfect for long gaming or work sessions.",
    tags: ["Gaming", "Office", "Ergonomic", "Black"],
    status: "Active",
    platforms: [
      { name: "Facebook", status: "Active", views: 47, likes: 8, messages: 3, price: 125 },
      { name: "eBay", status: "Active", views: 23, watchers: 5, bids: 0, price: 135 },
      { name: "Mercari", status: "Pending", views: 0, likes: 0, messages: 0, price: 110 }
    ],
    analytics: {
      totalViews: 70,
      engagementRate: 0.18,
      timesSaved: 13,
      avgTimeOnListing: 45,
      topAgeGroup: "25-34",
      topLocation: "Urban areas"
    },
    offers: [
      { platform: "Facebook", amount: 110, buyer: "John D.", message: "Cash pickup today?" },
      { platform: "eBay", amount: 120, buyer: "gamer_mike", message: "Best I can do" }
    ]
  },
  {
    id: 2,
    title: "MacBook Pro 13-inch - 2021 M1 Chip, 256GB",
    price: 695,
    originalPrice: 720,
    description: "Lightly used MacBook Pro in excellent condition. Perfect for students or professionals. Includes original charger and box.",
    tags: ["Laptop", "Apple", "M1", "Professional"],
    status: "Active",
    platforms: [
      { name: "Facebook", status: "Active", views: 89, likes: 15, messages: 8, price: 695 },
      { name: "eBay", status: "Active", views: 67, watchers: 12, bids: 2, price: 720 },
      { name: "Mercari", status: "Sold", views: 34, likes: 7, messages: 4, price: 660 }
    ],
    analytics: {
      totalViews: 190,
      engagementRate: 0.22,
      timesSaved: 27,
      avgTimeOnListing: 67,
      topAgeGroup: "18-24",
      topLocation: "College towns"
    },
    offers: [
      { platform: "Facebook", amount: 650, buyer: "Sarah M.", message: "For my son's college" },
      { platform: "eBay", amount: 680, buyer: "tech_student", message: "Need for classes" },
      { platform: "Facebook", amount: 675, buyer: "Mike R.", message: "Can pickup immediately" }
    ]
  },
  {
    id: 3,
    title: "Vintage Camera Collection - Canon AE-1 Program",
    price: 185,
    originalPrice: 200,
    description: "Rare vintage cameras in excellent working condition. Perfect for collectors and photography enthusiasts. Includes original case.",
    tags: ["Vintage", "Camera", "Canon", "Collectible"],
    status: "Active",
    platforms: [
      { name: "eBay", status: "Active", views: 156, watchers: 18, bids: 5, price: 200 },
      { name: "Facebook", status: "Active", views: 43, likes: 9, messages: 2, price: 185 },
      { name: "Mercari", status: "Draft", views: 0, likes: 0, messages: 0, price: 175 }
    ],
    analytics: {
      totalViews: 199,
      engagementRate: 0.16,
      timesSaved: 27,
      avgTimeOnListing: 89,
      topAgeGroup: "35-44",
      topLocation: "Metropolitan areas"
    },
    offers: [
      { platform: "eBay", amount: 175, buyer: "vintage_collector", message: "Fair offer for quick sale" },
      { platform: "Facebook", amount: 160, buyer: "Photo_Phil", message: "Love old cameras!" }
    ]
  }
];

// Complex buyer messages with AI analysis
const mockBuyerMessages = [
  {
    id: 1,
    itemTitle: "Gaming Chair",
    buyerName: "John D.",
    platform: "Facebook",
    offerAmount: 110,
    originalPrice: 125,
    message: "Would you take $110 cash? I can pick up today!",
    timestamp: "2 hours ago",
    status: "pending",
    aiAnalysis: {
      sentiment: "positive",
      urgency: "high",
      negotiationLikelihood: 0.85,
      recommendedResponse: "counter_offer",
      suggestedPrice: 120,
      reasoning: "Buyer shows urgency with 'today pickup' - likely to accept small counter"
    },
    buyerHistory: {
      previousPurchases: 3,
      avgResponseTime: "15 minutes",
      cancellationRate: 0.1,
      rating: 4.8
    }
  },
  {
    id: 2,
    itemTitle: "MacBook Pro",
    buyerName: "Sarah M.",
    platform: "Facebook",
    offerAmount: 650,
    originalPrice: 695,
    message: "Is this still available? My son needs this for college. Can we work out a deal?",
    timestamp: "4 hours ago",
    status: "responded",
    aiAnalysis: {
      sentiment: "sincere",
      urgency: "medium",
      negotiationLikelihood: 0.72,
      recommendedResponse: "accept_or_small_counter",
      suggestedPrice: 670,
      reasoning: "Educational purpose + personal story suggests genuine buyer, moderate flexibility"
    },
    buyerHistory: {
      previousPurchases: 1,
      avgResponseTime: "45 minutes",
      cancellationRate: 0.05,
      rating: 5.0
    }
  },
  {
    id: 3,
    itemTitle: "Vintage Camera",
    buyerName: "vintage_collector",
    platform: "eBay",
    offerAmount: 175,
    originalPrice: 200,
    message: "Beautiful piece! I'm a serious collector. Would you consider $175 for a quick sale?",
    timestamp: "6 hours ago",
    status: "pending",
    aiAnalysis: {
      sentiment: "enthusiastic",
      urgency: "low",
      negotiationLikelihood: 0.65,
      recommendedResponse: "counter_offer",
      suggestedPrice: 190,
      reasoning: "Collector language suggests knowledge and patience - can negotiate higher"
    },
    buyerHistory: {
      previousPurchases: 47,
      avgResponseTime: "2 hours",
      cancellationRate: 0.02,
      rating: 4.9
    }
  },
  {
    id: 4,
    itemTitle: "4K Smart TV",
    buyerName: "TechBuyer2024",
    platform: "eBay",
    offerAmount: 380,
    originalPrice: 435,
    message: "What kind of condition is the screen in? Any dead pixels or scratches?",
    timestamp: "8 hours ago",
    status: "pending",
    aiAnalysis: {
      sentiment: "cautious",
      urgency: "low",
      negotiationLikelihood: 0.45,
      recommendedResponse: "provide_details",
      suggestedPrice: 420,
      reasoning: "Quality-focused buyer asking detailed questions - likely to pay fair price for good condition"
    },
    buyerHistory: {
      previousPurchases: 12,
      avgResponseTime: "3 hours",
      cancellationRate: 0.15,
      rating: 4.6
    }
  }
];

// Enhanced sales data with profitability analysis
const mockSalesData = [
  {
    id: 1,
    title: "iPhone 12 Pro Max - 256GB",
    image: "/vercel.svg",
    soldPrice: 650,
    originalAskingPrice: 699,
    costBasis: 100, // What you originally paid/valued it at
    netProfit: 515, // After fees
    platform: "Facebook",
    buyer: "Mike Johnson",
    saleDate: "2 days ago",
    daysListed: 3,
    totalViews: 89,
    offers: 8,
    negotiations: 3,
    finalDiscount: 0.07,
    platformFees: 35,
    shippingCost: 0,
    paymentMethod: "Cash",
    category: "Electronics",
    condition: "Like New"
  },
  {
    id: 2,
    title: "Designer Handbag - Louis Vuitton Speedy 30",
    image: "/vercel.svg",
    soldPrice: 480,
    originalAskingPrice: 520,
    costBasis: 200,
    netProfit: 245,
    platform: "eBay",
    buyer: "Lisa Chen",
    saleDate: "1 week ago",
    daysListed: 8,
    totalViews: 167,
    offers: 12,
    negotiations: 5,
    finalDiscount: 0.08,
    platformFees: 35,
    shippingCost: 15,
    paymentMethod: "PayPal",
    category: "Fashion",
    condition: "Good"
  },
  {
    id: 3,
    title: "Gaming Console - PlayStation 5",
    image: "/vercel.svg",
    soldPrice: 420,
    originalAskingPrice: 450,
    costBasis: 50,
    netProfit: 350,
    platform: "Facebook",
    buyer: "GameMaster2024",
    saleDate: "3 days ago",
    daysListed: 2,
    totalViews: 134,
    offers: 15,
    negotiations: 6,
    finalDiscount: 0.07,
    platformFees: 20,
    shippingCost: 0,
    paymentMethod: "Venmo",
    category: "Electronics",
    condition: "Good"
  },
  {
    id: 4,
    title: "Antique Wooden Desk",
    image: "/vercel.svg",
    soldPrice: 280,
    originalAskingPrice: 320,
    costBasis: 80,
    netProfit: 185,
    platform: "Facebook",
    buyer: "HomeDesigner",
    saleDate: "5 days ago",
    daysListed: 12,
    totalViews: 78,
    offers: 4,
    negotiations: 2,
    finalDiscount: 0.125,
    platformFees: 15,
    shippingCost: 0,
    paymentMethod: "Cash",
    category: "Furniture",
    condition: "Used"
  }
];

// Market intelligence data
const mockMarketIntelligence = {
  trending: {
    upCategories: [
      { name: "Gaming Equipment", growth: "+34%", avgPrice: 180 },
      { name: "Home Office", growth: "+28%", avgPrice: 95 },
      { name: "Vintage Electronics", growth: "+22%", avgPrice: 145 }
    ],
    downCategories: [
      { name: "Fast Fashion", growth: "-12%", avgPrice: 25 },
      { name: "Old Textbooks", growth: "-18%", avgPrice: 15 }
    ]
  },
  seasonality: {
    current: "Back-to-School",
    peakMonths: ["August", "September"],
    recommendations: [
      "Price electronics 15% higher during back-to-school season",
      "Focus on student-friendly items",
      "Emphasize 'perfect for dorm room' in descriptions"
    ]
  },
  competition: {
    avgListingTime: 6.4,
    yourAvgTime: 4.2,
    avgSuccessRate: 0.64,
    yourSuccessRate: 0.78
  }
};

const Card = ({ children, className = '', onClick }: { children: React.ReactNode; className?: string; onClick?: () => void }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className={`rounded-2xl border border-[#F6EFD9]/30 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300 ${className}`}
    onClick={onClick}
  >
    {children}
  </motion.div>
);

export default function ComplexDashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('declutter');
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [showDeclutterFlow, setShowDeclutterFlow] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [filterCategory, setFilterCategory] = useState('all');
  const [selectedListing, setSelectedListing] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [buyerMessages, setBuyerMessages] = useState(mockBuyerMessages);
  const [salesData, setSalesData] = useState(mockSalesData);
  const [newSaleNotification, setNewSaleNotification] = useState(false);
  
  // Calculate dynamic stats
  const totalEarnings = salesData.reduce((sum, sale) => sum + sale.netProfit, 0);
  const totalRevenue = salesData.reduce((sum, sale) => sum + sale.soldPrice, 0);
  const avgDaysToSell = Math.round(salesData.reduce((sum, sale) => sum + sale.daysListed, 0) / salesData.length);
  const totalListings = mockListings.length;
  const activeListings = mockListings.filter(l => l.status === 'Active').length;
  const successRate = Math.round((salesData.length / (salesData.length + activeListings)) * 100);

  const handleItemSelection = (itemId: number) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const openListingModal = (listing: any) => {
    setSelectedListing(listing);
    setIsModalOpen(true);
  };

  const closeListingModal = () => {
    setSelectedListing(null);
    setIsModalOpen(false);
  };

  const handleAcceptOffer = (messageId: number) => {
    // Find the message to accept (always use first message for demo)
    const messageToAccept = buyerMessages.find(msg => msg.id === messageId) || buyerMessages[0];
    
    if (messageToAccept) {
      // Remove from messages
      setBuyerMessages(prev => prev.filter(msg => msg.id !== messageId));
      
      // Add to sales (create new sale record)
      const newSale = {
        id: salesData.length + 1,
        title: messageToAccept.itemTitle,
        image: "/vercel.svg",
        soldPrice: messageToAccept.offerAmount,
        originalAskingPrice: messageToAccept.originalPrice,
        costBasis: Math.round(messageToAccept.offerAmount * 0.3), // 30% cost basis
        netProfit: Math.round(messageToAccept.offerAmount * 0.7), // 70% profit
        platform: messageToAccept.platform,
        buyer: messageToAccept.buyerName,
        saleDate: "Just now",
        daysListed: Math.floor(Math.random() * 5) + 1,
        totalViews: Math.floor(Math.random() * 100) + 50,
        offers: Math.floor(Math.random() * 10) + 1,
        negotiations: Math.floor(Math.random() * 5) + 1,
        finalDiscount: (messageToAccept.originalPrice - messageToAccept.offerAmount) / messageToAccept.originalPrice,
        platformFees: Math.round(messageToAccept.offerAmount * 0.08), // 8% platform fees
        shippingCost: messageToAccept.platform === 'eBay' ? 15 : 0,
        paymentMethod: messageToAccept.platform === 'Facebook' ? 'Cash' : 'PayPal',
        category: 'Electronics',
        condition: 'Good'
      };
      
      setSalesData(prev => [newSale, ...prev]);
      
      // Show success notification
      setNewSaleNotification(true);
      setTimeout(() => setNewSaleNotification(false), 3000);
    }
  };

  const renderDeclutterTab = () => (
    <div className="space-y-8">
      {/* Enhanced Hero Section */}
      <div className="relative -mx-6 overflow-hidden bg-gradient-to-br from-[#F6EFD9]/20 via-white to-[#5BAAA7]/5 py-20">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Floating elements with more variety */}
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className={`absolute w-${4 + (i % 4) * 4} h-${4 + (i % 4) * 4} bg-gradient-to-br from-[#5BAAA7]/${20 - i * 2} to-[#1A6A6A]/${15 - i * 2} rounded-full blur-sm`}
              style={{
                top: `${10 + (i * 13) % 80}%`,
                left: `${5 + (i * 17) % 90}%`,
              }}
              animate={{
                y: [0, -20 - (i % 3) * 10, 0],
                x: [0, 10 - (i % 2) * 20, 0],
                scale: [1, 1.1 + (i % 3) * 0.1, 1],
                rotate: [0, (i % 2) * 360, 0]
              }}
              transition={{
                duration: 8 + (i % 3) * 2,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.5
              }}
            />
          ))}
        </div>

        <div className="relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h1 className="text-4xl md:text-6xl font-extrabold text-[#0a1b2a] mb-6">
              AI-Powered Marketplace
              <span className="block bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
                Automation Platform
              </span>
            </h1>
            <p className="text-xl text-[#6b7b8c] mb-8 max-w-3xl mx-auto leading-relaxed">
              Identify, price, and list your items across Facebook Marketplace, eBay, and Mercari with AI-powered insights and automated buyer management.
            </p>
            
            {/* Key Stats Preview */}
            <div className="flex flex-wrap justify-center gap-6 mb-10">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl px-6 py-4 border border-[#F6EFD9]/40 shadow-lg">
                <div className="text-2xl font-bold text-[#5BAAA7]">${totalEarnings.toLocaleString()}</div>
                <div className="text-sm text-[#6b7b8c]">Total Profits</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl px-6 py-4 border border-[#F6EFD9]/40 shadow-lg">
                <div className="text-2xl font-bold text-[#5BAAA7]">{avgDaysToSell}</div>
                <div className="text-sm text-[#6b7b8c]">Avg Days to Sell</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl px-6 py-4 border border-[#F6EFD9]/40 shadow-lg">
                <div className="text-2xl font-bold text-[#5BAAA7]">{successRate}%</div>
                <div className="text-sm text-[#6b7b8c]">Success Rate</div>
              </div>
            </div>
          </motion.div>

          <motion.button
            onClick={() => setShowDeclutterFlow(true)}
            className="group relative inline-flex items-center gap-3 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] hover:from-[#1A6A6A] hover:to-[#5BAAA7] text-white px-10 py-5 rounded-2xl font-bold text-lg shadow-2xl hover:shadow-3xl transition-all duration-300"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            whileHover={{ scale: 1.05, y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <Camera className="w-7 h-7 group-hover:rotate-12 transition-transform duration-300" />
            Start AI Analysis
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            />
          </motion.button>
        </div>
      </div>

      {/* AI-Enhanced Item Detection Results */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-[#0a1b2a] flex items-center gap-3">
            <Brain className="w-8 h-8 text-[#5BAAA7]" />
            AI Detection Results
          </h2>
          <div className="flex items-center gap-4">
            <select 
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-[#F6EFD9]/40 rounded-xl bg-white text-sm"
            >
              <option value="all">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Furniture">Furniture</option>
              <option value="Fashion">Fashion</option>
            </select>
            <div className="text-sm text-[#6b7b8c] bg-[#F6EFD9]/30 px-4 py-2 rounded-full">
              {mockDetectedItems.length} items analyzed
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockDetectedItems.map((item) => (
            <Card key={item.id} className="group cursor-pointer hover:scale-[1.02] transition-all duration-300">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#F6EFD9]/30 to-[#5BAAA7]/20 rounded-2xl flex items-center justify-center">
                      <Package className="w-8 h-8 text-[#5BAAA7]" />
                    </div>
                    <div className="flex-1">
                      <div className={`text-xs font-medium px-2 py-1 rounded-full mb-2 ${
                        item.confidence >= 0.95 ? 'bg-green-100 text-green-700' :
                        item.confidence >= 0.85 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {Math.round(item.confidence * 100)}% Match
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleItemSelection(item.id)}
                    className="text-[#6b7b8c] hover:text-[#5BAAA7] transition-colors"
                  >
                    {selectedItems.includes(item.id) ? 
                      <CheckSquare className="w-6 h-6 text-[#5BAAA7]" /> : 
                      <Square className="w-6 h-6" />
                    }
                  </button>
                </div>
                
                <h3 className="font-bold text-[#0a1b2a] mb-2 text-lg">{item.name}</h3>
                <p className="text-sm text-[#6b7b8c] mb-4 flex items-center gap-4">
                  <span>{item.category} • {item.condition}</span>
                  <span className={`flex items-center gap-1 ${
                    item.marketDemand === 'Very High' ? 'text-green-600' :
                    item.marketDemand === 'High' ? 'text-blue-600' :
                    'text-yellow-600'
                  }`}>
                    <TrendingUp className="w-3 h-3" />
                    {item.marketDemand}
                  </span>
                </p>
                
                {/* Price Analysis */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-2xl font-bold bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
                      ${item.estimatedValue}
                    </div>
                    <div className="text-xs text-[#6b7b8c]">
                      ${item.priceRange.min}-${item.priceRange.max}
                    </div>
                  </div>
                  <div className="text-xs text-[#6b7b8c] mb-2">
                    Based on {item.similarSold} similar sold items
                  </div>
                </div>

                {/* Platform Recommendations */}
                <div className="space-y-2 mb-4">
                  <div className="text-sm font-semibold text-[#0a1b2a] mb-2">Platform Recommendations:</div>
                  {Object.entries(item.platformRecommendations).map(([platform, data]) => (
                    <div key={platform} className="flex items-center justify-between text-xs">
                      <span className="capitalize font-medium">{platform}:</span>
                      <span className="text-[#5BAAA7]">${data.price} ({data.timeToSell}d)</span>
                    </div>
                  ))}
                </div>

                {/* Market Indicators */}
                <div className="flex items-center justify-between pt-4 border-t border-[#F6EFD9]/30">
                  <div className="flex items-center gap-2">
                    <motion.div 
                      className={`w-2 h-2 rounded-full ${
                        item.trendDirection === 'up' ? 'bg-green-400' :
                        item.trendDirection === 'down' ? 'bg-red-400' :
                        'bg-yellow-400'
                      }`}
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    <span className="text-xs text-[#6b7b8c] capitalize">
                      {item.trendDirection} trend
                    </span>
                  </div>
                  <div className="text-xs text-[#6b7b8c]">
                    {item.seasonality.replace('-', ' ')}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {selectedItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 p-6 bg-gradient-to-r from-[#5BAAA7]/10 to-[#1A6A6A]/10 rounded-2xl border border-[#5BAAA7]/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-[#0a1b2a] mb-2 text-lg">
                  {selectedItems.length} items selected for listing
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-[#6b7b8c]">Est. total value:</span>
                    <div className="font-bold text-[#5BAAA7] text-lg">
                      ${mockDetectedItems
                        .filter(item => selectedItems.includes(item.id))
                        .reduce((sum, item) => sum + item.estimatedValue, 0)
                        .toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <span className="text-[#6b7b8c]">Best platform:</span>
                    <div className="font-bold text-[#5BAAA7]">Facebook</div>
                  </div>
                  <div>
                    <span className="text-[#6b7b8c]">Avg. time to sell:</span>
                    <div className="font-bold text-[#5BAAA7]">3.8 days</div>
                  </div>
                  <div>
                    <span className="text-[#6b7b8c]">Success probability:</span>
                    <div className="font-bold text-[#5BAAA7]">87%</div>
                  </div>
                </div>
              </div>
              <button className="bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Auto-Create Listings
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );

  const renderListingsTab = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-[#0a1b2a] flex items-center gap-3">
          <Tag className="w-8 h-8 text-[#5BAAA7]" />
          Active Listings
        </h2>
        <div className="flex items-center gap-4">
          <select className="px-4 py-2 border border-[#F6EFD9]/40 rounded-xl bg-white text-sm">
            <option>All Platforms</option>
            <option>Facebook Only</option>
            <option>eBay Only</option>
            <option>Mercari Only</option>
          </select>
          <button className="bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white px-4 py-2 rounded-xl font-semibold flex items-center gap-2 hover:shadow-lg transition-all">
            <Plus className="w-4 h-4" />
            New Listing
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {mockListings.map((listing) => (
          <Card 
            key={listing.id} 
            className="group hover:scale-[1.01] transition-transform duration-300 cursor-pointer"
            onClick={() => openListingModal(listing)}
          >
            {/* Image Header with Platform Status */}
            <div className="relative h-48 bg-gradient-to-br from-[#F6EFD9]/20 to-[#5BAAA7]/10 rounded-t-2xl overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <Package className="w-16 h-16 text-[#5BAAA7]/50" />
              </div>
              
              {/* Platform Status Indicators */}
              <div className="absolute top-4 left-4 flex flex-wrap gap-2">
                {listing.platforms.map((platform) => (
                  <span 
                    key={platform.name}
                    className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      platform.status === 'Active' ? 'bg-green-100 text-green-800 border border-green-200' :
                      platform.status === 'Pending' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                      platform.status === 'Sold' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                      'bg-gray-100 text-gray-800 border border-gray-200'
                    }`}
                  >
                    {platform.name}
                  </span>
                ))}
              </div>

              {/* Performance Badge */}
              <div className="absolute top-4 right-4">
                <div className="bg-white/90 backdrop-blur-sm rounded-xl px-3 py-2 text-xs">
                  <div className="font-bold text-[#5BAAA7]">{listing.analytics.totalViews}</div>
                  <div className="text-[#6b7b8c]">views</div>
                </div>
              </div>
            </div>

            {/* Card Content */}
            <div className="p-6">
              <h3 className="text-lg font-bold text-[#0a1b2a] mb-3 line-clamp-2 group-hover:text-[#5BAAA7] transition-colors">
                {listing.title}
              </h3>
              
              {/* Pricing */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <p className="text-2xl font-bold bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent">
                    ${listing.price}
                  </p>
                  {listing.originalPrice > listing.price && (
                    <span className="text-sm text-[#6b7b8c] line-through">
                      ${listing.originalPrice}
                    </span>
                  )}
                </div>
                <div className="text-sm text-[#6b7b8c]">
                  {listing.platforms.filter(p => p.status === 'Active').length} platforms • {listing.offers.length} offers
                </div>
              </div>

              {/* Analytics Summary */}
              <div className="bg-[#F6EFD9]/20 rounded-xl p-3 mb-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-[#6b7b8c]">Engagement</div>
                    <div className="font-bold text-[#5BAAA7]">
                      {Math.round(listing.analytics.engagementRate * 100)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[#6b7b8c]">Saved</div>
                    <div className="font-bold text-[#5BAAA7]">
                      {listing.analytics.timesSaved}
                    </div>
                  </div>
                  <div>
                    <div className="text-[#6b7b8c]">Top Age</div>
                    <div className="font-bold text-[#5BAAA7]">
                      {listing.analytics.topAgeGroup}
                    </div>
                  </div>
                  <div>
                    <div className="text-[#6b7b8c]">Location</div>
                    <div className="font-bold text-[#5BAAA7] text-xs">
                      {listing.analytics.topLocation}
                    </div>
                  </div>
                </div>
              </div>

              {/* Platform Performance */}
              <div className="mb-4">
                <div className="text-sm font-semibold text-[#0a1b2a] mb-2">Platform Performance:</div>
                <div className="space-y-2">
                  {listing.platforms.map((platform) => (
                    <div key={platform.name} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{platform.name}</span>
                        <span className={`w-2 h-2 rounded-full ${
                          platform.status === 'Active' ? 'bg-green-400' :
                          platform.status === 'Pending' ? 'bg-yellow-400' :
                          platform.status === 'Sold' ? 'bg-blue-400' :
                          'bg-gray-400'
                        }`} />
                      </div>
                      <div className="text-[#6b7b8c]">
                        {platform.views} views • {platform.likes || platform.watchers || 0} interested
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-[#F6EFD9]/30">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    openListingModal(listing);
                  }}
                  className="flex items-center gap-2 text-[#5BAAA7] hover:text-[#1A6A6A] font-semibold text-sm hover:bg-[#F6EFD9]/20 px-3 py-2 rounded-lg transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  View Analytics
                </button>
                
                <div className="flex items-center gap-2">
                  <button className="p-2 text-[#6b7b8c] hover:text-[#5BAAA7] hover:bg-[#F6EFD9]/20 rounded-lg transition-colors">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-[#6b7b8c] hover:text-[#5BAAA7] hover:bg-[#F6EFD9]/20 rounded-lg transition-colors">
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-[#6b7b8c] hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderOffersTab = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-[#0a1b2a] flex items-center gap-3">
          <MessageCircle className="w-8 h-8 text-[#5BAAA7]" />
          Buyer Messages & AI Analysis
        </h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-[#6b7b8c] bg-[#F6EFD9]/30 px-4 py-2 rounded-full">
            {buyerMessages.length} active conversations
          </div>
          <button className="bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white px-4 py-2 rounded-xl font-semibold flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Auto-Respond All
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {buyerMessages.length > 0 ? (
          buyerMessages.map((message) => (
            <Card key={message.id} className="overflow-hidden">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="font-bold text-[#0a1b2a] text-lg">{message.itemTitle}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      message.status === 'pending' 
                        ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' 
                        : 'bg-green-100 text-green-800 border border-green-200'
                    }`}>
                      {message.status}
                    </span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                      {message.platform}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-[#6b7b8c] mb-3">
                    <span>From {message.buyerName}</span>
                    <span>•</span>
                    <span>{message.timestamp}</span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span>{message.buyerHistory.rating}</span>
                      <span className="text-xs">({message.buyerHistory.previousPurchases} purchases)</span>
                    </div>
                  </div>
                  
                  {/* Message Content */}
                  <div className="bg-[#F6EFD9]/20 rounded-xl p-4 mb-4">
                    <p className="text-[#0a1b2a] mb-3">"{message.message}"</p>
                    <div className="flex items-center justify-between">
                      <div className="text-2xl font-bold text-[#5BAAA7]">
                        ${message.offerAmount}
                      </div>
                      <div className="text-sm text-[#6b7b8c]">
                        vs. ${message.originalPrice} asking
                        <span className={`ml-2 font-semibold ${
                          ((message.originalPrice - message.offerAmount) / message.originalPrice) < 0.1 
                            ? 'text-green-600' : 'text-red-600'
                        }`}>
                          ({Math.round(((message.originalPrice - message.offerAmount) / message.originalPrice) * 100)}% discount)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Analysis Section */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 mb-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">AI Analysis</span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                    {Math.round(message.aiAnalysis.negotiationLikelihood * 100)}% negotiation likelihood
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  <div>
                    <div className="text-xs text-blue-600 mb-1">Sentiment</div>
                    <div className={`font-semibold capitalize px-2 py-1 rounded-full text-xs ${
                      message.aiAnalysis.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                      message.aiAnalysis.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {message.aiAnalysis.sentiment}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-blue-600 mb-1">Urgency</div>
                    <div className={`font-semibold capitalize px-2 py-1 rounded-full text-xs ${
                      message.aiAnalysis.urgency === 'high' ? 'bg-red-100 text-red-700' :
                      message.aiAnalysis.urgency === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {message.aiAnalysis.urgency}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-blue-600 mb-1">Suggested Price</div>
                    <div className="font-bold text-green-600">${message.aiAnalysis.suggestedPrice}</div>
                  </div>
                </div>
                
                <div className="text-sm text-blue-800 mb-3">
                  <strong>Reasoning:</strong> {message.aiAnalysis.reasoning}
                </div>
              </div>

              {/* Buyer History */}
              <div className="bg-gray-50 rounded-xl p-4 mb-4">
                <div className="text-sm font-semibold text-gray-700 mb-2">Buyer History</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Purchases</div>
                    <div className="font-bold">{message.buyerHistory.previousPurchases}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Response Time</div>
                    <div className="font-bold">{message.buyerHistory.avgResponseTime}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Cancellation Rate</div>
                    <div className="font-bold">{Math.round(message.buyerHistory.cancellationRate * 100)}%</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Rating</div>
                    <div className="font-bold flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      {message.buyerHistory.rating}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 pt-4 border-t border-[#F6EFD9]/30">
                <button 
                  onClick={() => handleAcceptOffer(message.id)}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 hover:shadow-lg"
                >
                  <CheckCircle className="w-4 h-4" />
                  Accept ${message.offerAmount}
                </button>
                <button className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Counter ${message.aiAnalysis.suggestedPrice}
                </button>
                <button className="px-6 border-2 border-[#5BAAA7] text-[#5BAAA7] hover:bg-[#5BAAA7] hover:text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  Message
                </button>
                <button className="px-6 bg-gradient-to-r from-purple-500 to-purple-600 text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2">
                  <Zap className="w-4 h-4" />
                  AI Respond
                </button>
              </div>
            </div>
          </Card>
        ))
        ) : (
          <Card>
            <div className="p-12 text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-[#F6EFD9]/30 to-[#5BAAA7]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <MessageCircle className="w-12 h-12 text-[#5BAAA7]/50" />
              </div>
              <h3 className="text-xl font-bold text-[#0a1b2a] mb-3">All caught up! 🎉</h3>
              <p className="text-[#6b7b8c] mb-6">
                No pending messages. Great job managing your buyer conversations!
              </p>
              <div className="text-sm text-[#5BAAA7] bg-[#5BAAA7]/10 px-4 py-2 rounded-full inline-block">
                Check back later for new inquiries
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );

  const renderSalesTab = () => (
    <div className="space-y-8">
      {/* Enhanced Sales Overview */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-[#0a1b2a] mb-4 flex items-center justify-center gap-3">
          <BarChart3 className="w-8 h-8 text-[#5BAAA7]" />
          Sales Performance Dashboard
        </h2>
        <div className="text-5xl font-bold bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] bg-clip-text text-transparent mb-4">
          ${totalEarnings.toLocaleString()} Net Profit
        </div>
        <div className="text-lg text-[#6b7b8c] mb-6">
          ${totalRevenue.toLocaleString()} total revenue this month
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">${totalEarnings.toLocaleString()}</div>
            <div className="text-[#6b7b8c]">Net Profits</div>
            <div className="text-xs text-green-600 mt-2">+23% vs last month</div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Package className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">{salesData.length}</div>
            <div className="text-[#6b7b8c]">Items Sold</div>
            <div className="text-xs text-blue-600 mt-2">{activeListings} still active</div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Clock className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">{avgDaysToSell}</div>
            <div className="text-[#6b7b8c]">Avg Days to Sell</div>
            <div className="text-xs text-purple-600 mt-2">vs {Math.round(mockMarketIntelligence.competition.avgListingTime)} market avg</div>
          </div>
        </Card>

        <Card>
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Target className="w-8 h-8 text-white" />
            </div>
            <div className="text-3xl font-bold text-[#0a1b2a] mb-2">{successRate}%</div>
            <div className="text-[#6b7b8c]">Success Rate</div>
            <div className="text-xs text-orange-600 mt-2">vs {Math.round(mockMarketIntelligence.competition.avgSuccessRate * 100)}% market avg</div>
          </div>
        </Card>
      </div>

      {/* Platform Performance Breakdown */}
      <Card className="mb-8">
        <div className="p-6">
          <h3 className="text-xl font-bold text-[#0a1b2a] mb-6 flex items-center gap-2">
            <PieChart className="w-6 h-6 text-[#5BAAA7]" />
            Platform Performance Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(mockPlatformStats).map(([platform, stats]) => (
              <div key={platform} className="bg-gradient-to-br from-[#F6EFD9]/20 to-[#5BAAA7]/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-bold text-[#0a1b2a] capitalize text-lg">{platform}</h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    stats.monthlyTrend.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {stats.monthlyTrend}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-[#6b7b8c]">Active Listings:</span>
                    <span className="font-bold text-[#5BAAA7]">{stats.totalListings}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-[#6b7b8c]">Avg Sale Price:</span>
                    <span className="font-bold text-[#5BAAA7]">${stats.avgSalePrice}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-[#6b7b8c]">Avg Time to Sell:</span>
                    <span className="font-bold text-[#5BAAA7]">{stats.avgTimeToSell} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-[#6b7b8c]">Success Rate:</span>
                    <span className="font-bold text-[#5BAAA7]">{Math.round(stats.successRate * 100)}%</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-[#F6EFD9]/40">
                  <div className="text-xs text-[#6b7b8c] mb-2">Top Categories:</div>
                  <div className="flex flex-wrap gap-1">
                    {stats.topCategories.map((cat) => (
                      <span key={cat} className="px-2 py-1 bg-[#5BAAA7]/10 text-[#5BAAA7] rounded-full text-xs">
                        {cat}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Recent Sales with Detailed Analytics */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-[#0a1b2a] flex items-center gap-2">
            <Activity className="w-6 h-6 text-[#5BAAA7]" />
            Recent Sales Analysis
          </h3>
          <div className="flex items-center gap-4">
            <select 
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="px-4 py-2 border border-[#F6EFD9]/40 rounded-xl bg-white text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
            <button className="flex items-center gap-2 px-4 py-2 border border-[#5BAAA7] text-[#5BAAA7] rounded-xl hover:bg-[#5BAAA7] hover:text-white transition-all">
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </div>
        
        {salesData.map((sale) => (
          <Card key={sale.id} className="mb-4">
            <div className="p-6">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-gradient-to-br from-[#F6EFD9]/30 to-[#5BAAA7]/20 rounded-2xl flex items-center justify-center flex-shrink-0">
                  <Package className="w-10 h-10 text-[#5BAAA7]" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold text-[#0a1b2a] text-lg">{sale.title}</h3>
                    <div className="flex items-center gap-4">
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                        Sold
                      </span>
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                        {sale.platform}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm mb-4">
                    <div>
                      <div className="text-[#6b7b8c]">Sold Price</div>
                      <div className="text-xl font-bold text-[#5BAAA7]">${sale.soldPrice}</div>
                    </div>
                    <div>
                      <div className="text-[#6b7b8c]">Net Profit</div>
                      <div className="text-xl font-bold text-green-600">${sale.netProfit}</div>
                    </div>
                    <div>
                      <div className="text-[#6b7b8c]">Days Listed</div>
                      <div className="font-bold">{sale.daysListed}</div>
                    </div>
                    <div>
                      <div className="text-[#6b7b8c]">Total Views</div>
                      <div className="font-bold">{sale.totalViews}</div>
                    </div>
                    <div>
                      <div className="text-[#6b7b8c]">Offers</div>
                      <div className="font-bold">{sale.offers}</div>
                    </div>
                    <div>
                      <div className="text-[#6b7b8c]">Profit Margin</div>
                      <div className="font-bold text-green-600">
                        {Math.round((sale.netProfit / sale.soldPrice) * 100)}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-[#6b7b8c]">
                    <div>
                      Sold to {sale.buyer} • {sale.saleDate} • {sale.paymentMethod}
                    </div>
                    <div className="flex items-center gap-4">
                      <span>Condition: {sale.condition}</span>
                      <span>Discount: {Math.round(sale.finalDiscount * 100)}%</span>
                      <span>Fees: ${sale.platformFees}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-[#0a1b2a] mb-4 flex items-center justify-center gap-3">
          <TrendingUp className="w-8 h-8 text-[#5BAAA7]" />
          Market Intelligence & Analytics
        </h2>
        <p className="text-lg text-[#6b7b8c]">
          AI-powered insights to optimize your marketplace strategy
        </p>
      </div>

      {/* Market Trends */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-[#0a1b2a] mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-[#5BAAA7]" />
            Trending Categories & Market Dynamics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Trending Up */}
            <div>
              <h4 className="font-semibold text-green-600 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Trending Up
              </h4>
              <div className="space-y-3">
                {mockMarketIntelligence.trending.upCategories.map((cat) => (
                  <div key={cat.name} className="flex items-center justify-between p-4 bg-green-50 rounded-xl border border-green-200">
                    <div>
                      <div className="font-bold text-green-900">{cat.name}</div>
                      <div className="text-sm text-green-600">Avg Price: ${cat.avgPrice}</div>
                    </div>
                    <div className="text-lg font-bold text-green-600">{cat.growth}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Trending Down */}
            <div>
              <h4 className="font-semibold text-red-600 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 rotate-180" />
                Declining Categories
              </h4>
              <div className="space-y-3">
                {mockMarketIntelligence.trending.downCategories.map((cat) => (
                  <div key={cat.name} className="flex items-center justify-between p-4 bg-red-50 rounded-xl border border-red-200">
                    <div>
                      <div className="font-bold text-red-900">{cat.name}</div>
                      <div className="text-sm text-red-600">Avg Price: ${cat.avgPrice}</div>
                    </div>
                    <div className="text-lg font-bold text-red-600">{cat.growth}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Seasonality Insights */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-[#0a1b2a] mb-6 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-[#5BAAA7]" />
            Seasonality Intelligence
          </h3>
          
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 border border-amber-200">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-2xl font-bold text-amber-900">
                  Current Season: {mockMarketIntelligence.seasonality.current}
                </div>
                <div className="text-sm text-amber-600">
                  Peak months: {mockMarketIntelligence.seasonality.peakMonths.join(', ')}
                </div>
              </div>
              <div className="w-16 h-16 bg-amber-200 rounded-2xl flex items-center justify-center">
                <Calendar className="w-8 h-8 text-amber-600" />
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-semibold text-amber-900">AI Recommendations:</h4>
              {mockMarketIntelligence.seasonality.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-amber-800">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Performance Comparison */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-[#0a1b2a] mb-6 flex items-center gap-2">
            <Award className="w-6 h-6 text-[#5BAAA7]" />
            Your Performance vs Market
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-200">
              <h4 className="font-bold text-green-900 mb-4">Average Listing Time</h4>
              <div className="flex items-end gap-4 mb-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{mockMarketIntelligence.competition.yourAvgTime}</div>
                  <div className="text-sm text-green-700">Your Average</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-500">{mockMarketIntelligence.competition.avgListingTime}</div>
                  <div className="text-sm text-gray-600">Market Average</div>
                </div>
              </div>
              <div className="bg-green-200 rounded-full p-3 text-center">
                <span className="text-green-800 font-semibold">
                  {Math.round(((mockMarketIntelligence.competition.avgListingTime - mockMarketIntelligence.competition.yourAvgTime) / mockMarketIntelligence.competition.avgListingTime) * 100)}% faster than market
                </span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-200">
              <h4 className="font-bold text-blue-900 mb-4">Success Rate</h4>
              <div className="flex items-end gap-4 mb-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{Math.round(mockMarketIntelligence.competition.yourSuccessRate * 100)}%</div>
                  <div className="text-sm text-blue-700">Your Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-500">{Math.round(mockMarketIntelligence.competition.avgSuccessRate * 100)}%</div>
                  <div className="text-sm text-gray-600">Market Average</div>
                </div>
              </div>
              <div className="bg-blue-200 rounded-full p-3 text-center">
                <span className="text-blue-800 font-semibold">
                  {Math.round(((mockMarketIntelligence.competition.yourSuccessRate - mockMarketIntelligence.competition.avgSuccessRate) / mockMarketIntelligence.competition.avgSuccessRate) * 100)}% higher than market
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );

  const renderAITab = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl font-bold text-[#0a1b2a] mb-4 flex items-center justify-center gap-3">
            <Brain className="w-8 h-8 text-[#5BAAA7]" />
            AgentMail AI Assistant
          </h2>
          <p className="text-[#6b7b8c] max-w-3xl mx-auto text-lg">
            Connect with your AI marketplace assistant powered by AgentMail and LiveKit. 
            Get real-time insights about your listings, buyer messages, pricing optimization, 
            and automated email management across all platforms.
          </p>
        </motion.div>
      </div>
      
      {/* AgentMail AI Component */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <AIChatbot />
      </motion.div>
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
      {/* Enhanced Header */}
      <header className="sticky top-0 z-20 backdrop-blur-md border-b border-[#F6EFD9]/30 bg-white/95 shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              <span className="text-[#5BAAA7]">de</span>
              <span className="text-slate-900">Cluttered</span>
              <span className="text-[#5BAAA7]">.ai</span>
            </div>
            <div className="hidden md:flex items-center gap-2 text-sm">
              <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                Live
              </div>
              <span className="text-[#6b7b8c]">Real-time marketplace automation</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-6 text-sm">
              <div className="text-center">
                <div className="font-bold text-[#5BAAA7]">${totalEarnings.toLocaleString()}</div>
                <div className="text-xs text-[#6b7b8c]">Profit</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-[#5BAAA7]">{activeListings}</div>
                <div className="text-xs text-[#6b7b8c]">Active</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-[#5BAAA7]">{successRate}%</div>
                <div className="text-xs text-[#6b7b8c]">Success</div>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Enhanced Navigation Tabs */}
      <div className="sticky top-16 z-10 bg-white/90 backdrop-blur-md border-b border-[#F6EFD9]/30 shadow-sm">
        <div className="mx-auto max-w-7xl px-6">
          <nav className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'declutter', label: 'AI Detection', icon: Brain, count: mockDetectedItems.length },
              { id: 'listings', label: 'Active Listings', icon: Tag, count: activeListings },
              { id: 'offers', label: 'Messages', icon: MessageCircle, count: buyerMessages.length },
              { id: 'sales', label: 'Sales', icon: BarChart3, count: salesData.length },
              { id: 'analytics', label: 'Analytics', icon: TrendingUp, count: null },
              { id: 'ai', label: 'AI Assistant', icon: Brain, count: null }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center gap-3 px-4 py-4 border-b-2 font-semibold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-[#5BAAA7] text-[#5BAAA7] bg-[#5BAAA7]/5'
                    : 'border-transparent text-[#6b7b8c] hover:text-[#0a1b2a] hover:border-[#5BAAA7]/30'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                    activeTab === tab.id 
                      ? 'bg-[#5BAAA7] text-white' 
                      : 'bg-[#6b7b8c]/20 text-[#6b7b8c]'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Enhanced Main Content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {activeTab === 'declutter' && renderDeclutterTab()}
          {activeTab === 'listings' && renderListingsTab()}
          {activeTab === 'offers' && renderOffersTab()}
          {activeTab === 'sales' && renderSalesTab()}
          {activeTab === 'analytics' && renderAnalyticsTab()}
          {activeTab === 'ai' && renderAITab()}
        </motion.div>
      </main>

      {/* Success Notification */}
      <AnimatePresence>
        {newSaleNotification && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.9 }}
            className="fixed bottom-8 right-8 z-50 bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-2xl shadow-2xl border-2 border-green-300"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-lg">Sale Completed! 🎉</div>
                <div className="text-green-100">Check your Sales tab for details</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Listing Detail Modal */}
      <ListingDetailModal 
        listing={selectedListing}
        isOpen={isModalOpen}
        onClose={closeListingModal}
      />
    </div>
  );
}