import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  Eye, 
  MessageCircle, 
  Calendar,
  BarChart3,
  PieChart,
  Activity,
  Star,
  MapPin,
  Clock,
  Zap
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  PieChart as RechartsPieChart, 
  Cell,
  AreaChart,
  Area
} from 'recharts';

interface ListingDetailModalProps {
  listing: any;
  isOpen: boolean;
  onClose: () => void;
}

const ListingDetailModal = ({ listing, isOpen, onClose }: ListingDetailModalProps) => {
  if (!listing) return null;

  // Mock detailed analytics data for charts
  const priceHistoryData = [
    { day: 'Day 1', price: listing.originalPrice, views: 12, messages: 0 },
    { day: 'Day 2', price: listing.originalPrice, views: 28, messages: 1 },
    { day: 'Day 3', price: listing.price, views: 45, messages: 3 },
    { day: 'Day 4', price: listing.price, views: 52, messages: 5 },
    { day: 'Day 5', price: listing.price, views: 67, messages: 8 },
    { day: 'Today', price: listing.price, views: listing.analytics?.totalViews || 70, messages: listing.offers?.length || 2 }
  ];

  const platformPerformanceData = listing.platforms?.map((platform: any) => ({
    platform: platform.name,
    views: platform.views,
    engagement: platform.likes || platform.watchers || 0,
    messages: platform.messages || 0,
    price: platform.price
  })) || [];

  const offerDistributionData = listing.offers?.map((offer: any, index: number) => ({
    offer: `Offer ${index + 1}`,
    amount: offer.amount,
    platform: offer.platform,
    discount: Math.round(((listing.price - offer.amount) / listing.price) * 100)
  })) || [];

  const viewsOverTimeData = [
    { time: '9 AM', views: 5, messages: 0 },
    { time: '12 PM', views: 15, messages: 1 },
    { time: '3 PM', views: 32, messages: 2 },
    { time: '6 PM', views: 48, messages: 5 },
    { time: '9 PM', views: 63, messages: 6 },
    { time: 'Now', views: listing.analytics?.totalViews || 70, messages: listing.offers?.length || 8 }
  ];

  const COLORS = ['#5BAAA7', '#1A6A6A', '#F6EFD9', '#CDE7E2', '#8FBC8F'];

  const highestOffer = listing.offers?.reduce((max: any, offer: any) => 
    offer.amount > max.amount ? offer : max, listing.offers[0]) || null;

  const lowestOffer = listing.offers?.reduce((min: any, offer: any) => 
    offer.amount < min.amount ? offer : min, listing.offers[0]) || null;

  const avgOffer = listing.offers?.reduce((sum: number, offer: any) => sum + offer.amount, 0) / (listing.offers?.length || 1) || 0;

  const engagementRate = listing.analytics?.engagementRate || 0.18;
  const totalInterested = listing.analytics?.timesSaved || 13;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-[#5BAAA7]/10 to-[#1A6A6A]/10 p-6 border-b border-[#F6EFD9]/30">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-[#0a1b2a] mb-2">{listing.title}</h2>
                  <div className="flex items-center gap-4 text-sm text-[#6b7b8c]">
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      ${listing.price}
                    </span>
                    <span className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {listing.analytics?.totalViews || 70} views
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageCircle className="w-4 h-4" />
                      {listing.offers?.length || 0} offers
                    </span>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="w-10 h-10 bg-white/80 hover:bg-white rounded-xl flex items-center justify-center transition-colors shadow-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Left Column - Key Stats */}
                <div className="space-y-6">
                  {/* Offer Stats */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-200">
                    <h3 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Negotiation Analysis
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <div className="text-2xl font-bold text-green-600">
                          ${highestOffer?.amount || listing.price}
                        </div>
                        <div className="text-sm text-green-700">Highest Offer</div>
                        <div className="text-xs text-green-600">
                          {highestOffer ? `from ${highestOffer.buyer}` : 'No offers yet'}
                        </div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-green-500">
                          ${lowestOffer?.amount || listing.price}
                        </div>
                        <div className="text-sm text-green-700">Lowest Offer</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-green-500">
                          ${Math.round(avgOffer)}
                        </div>
                        <div className="text-sm text-green-700">Average Offer</div>
                      </div>
                    </div>
                  </div>

                  {/* People Talking */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
                    <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2">
                      <Users className="w-5 h-5" />
                      Active Conversations
                    </h3>
                    <div className="space-y-3">
                      {listing.offers?.slice(0, 3).map((offer: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-white rounded-xl border border-blue-100">
                          <div>
                            <div className="font-semibold text-blue-900">{offer.buyer}</div>
                            <div className="text-sm text-blue-600">{offer.platform}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-blue-600">${offer.amount}</div>
                            <div className="flex items-center gap-1 text-xs text-blue-500">
                              <Star className="w-3 h-3 fill-current" />
                              Active
                            </div>
                          </div>
                        </div>
                      )) || (
                        <div className="text-center text-blue-600 py-4">
                          No active conversations
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Engagement Stats */}
                  <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-2xl p-6 border border-purple-200">
                    <h3 className="font-bold text-purple-900 mb-4 flex items-center gap-2">
                      <Activity className="w-5 h-5" />
                      Engagement Metrics
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-purple-700">Engagement Rate</span>
                        <span className="font-bold text-purple-600">
                          {Math.round(engagementRate * 100)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-purple-700">Times Saved</span>
                        <span className="font-bold text-purple-600">{totalInterested}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-purple-700">Avg. View Time</span>
                        <span className="font-bold text-purple-600">
                          {listing.analytics?.avgTimeOnListing || 45}s
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-purple-700">Top Age Group</span>
                        <span className="font-bold text-purple-600">
                          {listing.analytics?.topAgeGroup || '25-34'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Middle Column - Charts */}
                <div className="lg:col-span-2 space-y-6">
                  
                  {/* Price & Views Timeline */}
                  <div className="bg-white rounded-2xl p-6 border border-[#F6EFD9]/40 shadow-sm">
                    <h3 className="font-bold text-[#0a1b2a] mb-4 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-[#5BAAA7]" />
                      Price & Engagement Timeline
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={priceHistoryData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#F6EFD9" />
                          <XAxis dataKey="day" stroke="#6b7b8c" fontSize={12} />
                          <YAxis stroke="#6b7b8c" fontSize={12} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: 'white', 
                              border: '1px solid #F6EFD9',
                              borderRadius: '12px',
                              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                            }}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="views" 
                            stroke="#5BAAA7" 
                            fill="#5BAAA7" 
                            fillOpacity={0.3}
                            name="Views"
                          />
                          <Area 
                            type="monotone" 
                            dataKey="messages" 
                            stroke="#1A6A6A" 
                            fill="#1A6A6A" 
                            fillOpacity={0.3}
                            name="Messages"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Platform Performance */}
                  <div className="bg-white rounded-2xl p-6 border border-[#F6EFD9]/40 shadow-sm">
                    <h3 className="font-bold text-[#0a1b2a] mb-4 flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-[#5BAAA7]" />
                      Platform Performance Comparison
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={platformPerformanceData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#F6EFD9" />
                          <XAxis dataKey="platform" stroke="#6b7b8c" fontSize={12} />
                          <YAxis stroke="#6b7b8c" fontSize={12} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: 'white', 
                              border: '1px solid #F6EFD9',
                              borderRadius: '12px',
                              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                            }}
                          />
                          <Bar dataKey="views" fill="#5BAAA7" name="Views" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="engagement" fill="#1A6A6A" name="Engagement" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Offer Distribution */}
                  {offerDistributionData.length > 0 && (
                    <div className="bg-white rounded-2xl p-6 border border-[#F6EFD9]/40 shadow-sm">
                      <h3 className="font-bold text-[#0a1b2a] mb-4 flex items-center gap-2">
                        <DollarSign className="w-5 h-5 text-[#5BAAA7]" />
                        Offer Distribution
                      </h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={offerDistributionData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#F6EFD9" />
                            <XAxis dataKey="offer" stroke="#6b7b8c" fontSize={12} />
                            <YAxis stroke="#6b7b8c" fontSize={12} />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'white', 
                                border: '1px solid #F6EFD9',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                              }}
                              formatter={(value: any, name: string) => [
                                name === 'amount' ? `$${value}` : `${value}%`, 
                                name === 'amount' ? 'Offer Amount' : 'Discount %'
                              ]}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="amount" 
                              stroke="#5BAAA7" 
                              strokeWidth={3}
                              dot={{ fill: '#5BAAA7', strokeWidth: 2, r: 6 }}
                              name="Offer Amount"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}

                  {/* Hourly Activity */}
                  <div className="bg-white rounded-2xl p-6 border border-[#F6EFD9]/40 shadow-sm">
                    <h3 className="font-bold text-[#0a1b2a] mb-4 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-[#5BAAA7]" />
                      Daily Activity Pattern
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={viewsOverTimeData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#F6EFD9" />
                          <XAxis dataKey="time" stroke="#6b7b8c" fontSize={12} />
                          <YAxis stroke="#6b7b8c" fontSize={12} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: 'white', 
                              border: '1px solid #F6EFD9',
                              borderRadius: '12px',
                              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                            }}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="views" 
                            stroke="#5BAAA7" 
                            fill="#5BAAA7" 
                            fillOpacity={0.4}
                            name="Cumulative Views"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex items-center justify-center gap-4 p-6 bg-gradient-to-r from-[#F6EFD9]/20 to-[#5BAAA7]/5 rounded-2xl">
                <button className="bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Boost Listing
                </button>
                <button className="border-2 border-[#5BAAA7] text-[#5BAAA7] hover:bg-[#5BAAA7] hover:text-white px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2">
                  <TrendingDown className="w-4 h-4" />
                  Adjust Price
                </button>
                <button className="border-2 border-[#6b7b8c] text-[#6b7b8c] hover:bg-[#6b7b8c] hover:text-white px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  Message All
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default ListingDetailModal;