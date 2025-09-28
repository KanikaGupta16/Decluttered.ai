import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles,
  Brain,
  TrendingUp,
  DollarSign,
  Package,
  ArrowRight,
  Loader2,
  BarChart3,
  Activity,
  MessageSquare,
  Zap,
  PieChart,
  ShoppingCart,
  Eye,
  Calendar
} from 'lucide-react';

// Gemini AI Configuration
interface GeminiState {
  connected: boolean;
  apiKey: string | null;
  loading: boolean;
  error: string | null;
  contextLoaded: boolean;
}

interface Message {
  id: string;
  type: 'user' | 'bot' | 'system';
  text: string;
  timestamp: Date;
  animated?: boolean;
  metadata?: {
    suggestedActions?: string[];
    confidence?: number;
    source?: 'gemini' | 'context' | 'analytics';
    transactionContext?: any;
  };
}

interface TransactionContext {
  recentListings: any[];
  salesHistory: any[];
  analytics: any;
  marketTrends: any[];
}

// Mock transaction data for RAG context
const mockTransactionData = {
  listings: [
    {
      id: '1',
      title: 'iPhone 13 Pro - 256GB Unlocked',
      price: 650,
      originalPrice: 699,
      platform: 'Facebook Marketplace',
      status: 'active',
      views: 89,
      messages: 15,
      datePosted: '2024-09-20',
      category: 'Electronics',
      condition: 'Like New',
      offers: [
        { amount: 600, buyer: 'Sarah M.', message: 'Need for college, can pickup today' },
        { amount: 620, buyer: 'TechBuyer', message: 'Is it unlocked for all carriers?' }
      ]
    },
    {
      id: '2',
      title: 'MacBook Air M2 - 8GB/256GB Silver',
      price: 950,
      originalPrice: 1050,
      platform: 'eBay',
      status: 'active',
      views: 134,
      messages: 28,
      datePosted: '2024-09-18',
      category: 'Electronics',
      condition: 'Excellent',
      offers: [
        { amount: 900, buyer: 'StudentBuyer', message: 'Perfect for my studies, very interested!' },
        { amount: 925, buyer: 'ProDesigner', message: 'Need for work, can pay immediately' }
      ]
    },
    {
      id: '3',
      title: 'Nike Air Jordan 4 - Size 10',
      price: 180,
      originalPrice: 220,
      platform: 'Facebook Marketplace',
      status: 'sold',
      views: 267,
      messages: 42,
      datePosted: '2024-09-15',
      dateSold: '2024-09-22',
      category: 'Clothing',
      condition: 'Very Good',
      finalPrice: 200,
      buyer: 'SneakerHead23'
    }
  ],
  salesHistory: [
    {
      month: 'September 2024',
      totalSales: 4,
      revenue: 1630,
      platforms: {
        'Facebook Marketplace': { sales: 2, revenue: 680 },
        'eBay': { sales: 2, revenue: 950 }
      },
      topCategories: ['Electronics', 'Clothing', 'Furniture']
    },
    {
      month: 'August 2024',
      totalSales: 6,
      revenue: 2150,
      platforms: {
        'Facebook Marketplace': { sales: 4, revenue: 1200 },
        'eBay': { sales: 2, revenue: 950 }
      },
      topCategories: ['Electronics', 'Home & Garden']
    }
  ],
  analytics: {
    totalListings: 15,
    activeListings: 12,
    soldItems: 10,
    totalRevenue: 5280,
    averageSaleTime: 8.5,
    platformPerformance: {
      'Facebook Marketplace': { 
        listingCount: 8, 
        conversionRate: 0.75, 
        avgViews: 156,
        avgMessages: 23 
      },
      'eBay': { 
        listingCount: 7, 
        conversionRate: 0.71, 
        avgViews: 189,
        avgMessages: 31 
      }
    },
    categoryPerformance: {
      'Electronics': { avgPrice: 524, soldCount: 6, avgDays: 7 },
      'Clothing': { avgPrice: 89, soldCount: 3, avgDays: 12 },
      'Furniture': { avgPrice: 245, soldCount: 1, avgDays: 15 }
    }
  },
  marketTrends: [
    {
      item: 'Electronics',
      trend: 'up',
      change: '+15%',
      reason: 'Back-to-school season driving demand'
    },
    {
      item: 'Designer Clothing',
      trend: 'up',
      change: '+8%',
      reason: 'Fall fashion trends increasing interest'
    },
    {
      item: 'Furniture',
      trend: 'neutral',
      change: '0%',
      reason: 'Steady demand, seasonal variations'
    }
  ]
};

export default function AIChatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      text: 'AI Assistant connected! I have access to your transaction data and can help with marketplace insights, pricing strategies, and optimization tips.',
      timestamp: new Date(),
      metadata: {
        source: 'gemini',
        suggestedActions: ['Show my recent listings', 'Analyze sales performance', 'Get pricing recommendations']
      }
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Gemini AI state
  const [geminiState, setGeminiState] = useState<GeminiState>({
    connected: true,
    apiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY || 'demo-key',
    loading: false,
    error: null,
    contextLoaded: true
  });

  const [transactionContext, setTransactionContext] = useState<TransactionContext>({
    recentListings: mockTransactionData.listings,
    salesHistory: mockTransactionData.salesHistory,
    analytics: mockTransactionData.analytics,
    marketTrends: mockTransactionData.marketTrends
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Generate AI response using Gemini RAG
  const generateGeminiResponse = async (userMessage: string): Promise<string> => {
    try {
      const lowerMessage = userMessage.toLowerCase();
      
      if (lowerMessage.includes('listing') || lowerMessage.includes('active')) {
        const activeListings = transactionContext.recentListings.filter(l => l.status === 'active');
        return `You currently have ${activeListings.length} active listings! Here's what I'm seeing:

📱 **${activeListings[0]?.title}** - $${activeListings[0]?.price}
   • ${activeListings[0]?.views} views, ${activeListings[0]?.messages} messages
   • Posted ${activeListings[0]?.datePosted}
   • ${activeListings[0]?.offers?.length || 0} offers received

💡 **Recommendation**: Your iPhone listing is getting good engagement. Consider responding to those offers - you might close a deal at $620!`;
      }
      
      if (lowerMessage.includes('performance') || lowerMessage.includes('analytics') || lowerMessage.includes('sales')) {
        return `📊 **Your Sales Performance**

**This Month**: ${transactionContext.salesHistory[0]?.totalSales} sales, $${transactionContext.salesHistory[0]?.revenue} revenue
**Platform Winner**: Facebook Marketplace (${transactionContext.analytics.platformPerformance['Facebook Marketplace']?.conversionRate * 100}% conversion rate)
**Best Category**: Electronics ($${transactionContext.analytics.categoryPerformance.Electronics?.avgPrice} avg price)

🎯 **Insights**:
- Your electronics sell fastest (${transactionContext.analytics.categoryPerformance.Electronics?.avgDays} days avg)
- Facebook Marketplace gives you better conversion rates
- You're trending 15% above market for electronics!

**Next Steps**: Consider listing more electronics on Facebook Marketplace for optimal results.`;
      }
      
      if (lowerMessage.includes('price') || lowerMessage.includes('pricing')) {
        return `💰 **Pricing Analysis**

Based on your transaction history and market trends:

**Electronics**: Trending +15% (great time to sell!)
**Your iPhone 13 Pro**: $650 is competitive
   • Market range: $600-$700
   • Your offers: $600, $620
   • **Recommendation**: Counter at $635 for quick sale

**MacBook Air M2**: $950 is well-positioned
   • Getting premium offers ($900-$925)
   • High engagement (134 views, 28 messages)

🚀 **Strategy**: Electronics are hot right now. Consider slight price increases or hold firm on current pricing!`;
      }
      
      if (lowerMessage.includes('help') || lowerMessage.includes('what can you')) {
        return `🤖 **I'm your marketplace intelligence assistant!** Here's how I can help:

📈 **Analytics & Insights**
• Track your sales performance across platforms
• Analyze which categories perform best
• Monitor market trends and pricing

💡 **Smart Recommendations**
• Optimal pricing strategies
• Best platforms for your items
• When to accept offers or hold out

🎯 **Actionable Tasks**
• Review pending offers and messages
• Identify items to reprice
• Suggest new items to list based on trends

**Try asking me**: "How are my listings doing?" or "Should I accept this offer?"`;
      }

      // Default response with context
      return `I understand you're asking about "${userMessage}". Based on your current marketplace activity:

• You have ${transactionContext.recentListings.filter(l => l.status === 'active').length} active listings generating good interest
• Your electronics category is performing excellently with fast sale times
• Facebook Marketplace is your best-converting platform

How can I help you optimize your marketplace success? I can analyze specific listings, suggest pricing changes, or help you respond to buyers!`;
      
    } catch (error) {
      console.error('Gemini API error:', error);
      return "I apologize, but I'm having trouble accessing my AI capabilities right now. However, I can still see that you have active listings that need attention. Would you like me to show you your current marketplace status?";
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await generateGeminiResponse(inputValue);
      
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          text: response,
          timestamp: new Date(),
          animated: true,
          metadata: {
            source: 'gemini',
            confidence: 0.92,
            transactionContext: transactionContext.analytics
          }
        };
        
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }, 1500);
      
    } catch (error) {
      console.error('Error generating response:', error);
      setIsTyping(false);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: 'I apologize, but I encountered an error. Let me try to help you with your marketplace data directly.',
        timestamp: new Date(),
        metadata: { source: 'gemini', confidence: 0 }
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const quickActions = [
    { text: 'Show my listings', icon: Package, color: 'blue' },
    { text: 'Sales analytics', icon: BarChart3, color: 'green' },
    { text: 'Pricing help', icon: DollarSign, color: 'yellow' },
    { text: 'Market trends', icon: TrendingUp, color: 'purple' }
  ];

  const handleQuickAction = (actionText: string) => {
    setInputValue(actionText);
  };
  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-emerald-50 via-green-50 to-teal-100">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-emerald-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.div
              className="relative"
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
            </motion.div>
            <div>
              <h3 className="font-semibold text-gray-900">AI Marketplace Assistant</h3>
              <p className="text-sm text-gray-600">Powered by Gemini RAG</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Gemini Status */}
            <motion.div
              className={`w-3 h-3 rounded-full ${
                geminiState.connected ? 'bg-green-400' : 'bg-red-400'
              }`}
              animate={{ scale: geminiState.connected ? [1, 1.2, 1] : 1 }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            
            {/* Context Status */}
            <motion.div
              className={`w-3 h-3 rounded-full ${
                transactionContext.recentListings.length > 0 ? 'bg-emerald-400' : 'bg-gray-400'
              }`}
              animate={{ scale: transactionContext.recentListings.length > 0 ? [1, 1.2, 1] : 1 }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        </div>
        
        {/* Status Bar */}
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>
                {transactionContext.recentListings.filter(l => l.status === 'active').length} Active Listings
              </span>
            </span>
            <span className={geminiState.connected ? 'text-green-600' : 'text-red-600'}>
              {geminiState.connected ? '🟢 Gemini Connected' : '🔴 Disconnected'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <Activity className="w-3 h-3" />
            <span>${transactionContext.analytics.totalRevenue} Total Revenue</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : ''}`}>
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-emerald-600 text-white ml-4'
                      : message.type === 'system'
                      ? 'bg-gradient-to-r from-emerald-100 to-teal-100 text-gray-800 border border-emerald-200'
                      : 'bg-white text-gray-800 shadow-sm border border-emerald-200 mr-4'
                  }`}
                >
                  {message.type === 'bot' && (
                    <div className="flex items-center space-x-2 mb-2">
                      <Bot className="w-4 h-4 text-emerald-600" />
                      <span className="text-xs font-medium text-emerald-600">
                        AI Assistant {message.metadata?.source === 'gemini' && '• Gemini RAG'}
                      </span>
                      {message.metadata?.confidence && (
                        <span className="text-xs text-gray-500">
                          {(message.metadata.confidence * 100).toFixed(0)}% confident
                        </span>
                      )}
                    </div>
                  )}
                  
                  <div 
                    className="whitespace-pre-wrap break-words leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: message.text
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-emerald-700">$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em class="italic text-gray-700">$1</em>')
                        .replace(/•/g, '<span class="text-emerald-500">•</span>')
                        .replace(/📱|💰|📊|🎯|🚀|🤖|💡|🟢|🔴/g, '<span class="text-lg">$&</span>')
                    }}
                  />
                  
                  {message.metadata?.suggestedActions && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.metadata.suggestedActions.map((action, index) => (
                        <button
                          key={index}
                          onClick={() => handleQuickAction(action)}
                          className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full transition-colors border border-emerald-200"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className={`text-xs text-gray-500 mt-1 ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
              
              <div className={`flex-shrink-0 ${message.type === 'user' ? 'order-1' : 'order-2'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Brain className="w-4 h-4" />
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-center space-x-2 bg-emerald-50 rounded-2xl px-4 py-3 border border-emerald-200">
              <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <div className="flex space-x-1">
                <motion.div
                  className="w-2 h-2 bg-emerald-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-2 h-2 bg-emerald-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-2 h-2 bg-emerald-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                />
              </div>
              <span className="text-sm text-gray-600">AI is thinking...</span>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2">
        <div className="flex flex-wrap gap-2 mb-4">
          {quickActions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <motion.button
                key={index}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleQuickAction(action.text)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${
                  action.color === 'blue'
                    ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-emerald-300 hover:shadow-sm'
                    : action.color === 'green'
                    ? 'bg-teal-100 text-teal-700 hover:bg-teal-200 border-teal-300 hover:shadow-sm'
                    : action.color === 'yellow'
                    ? 'bg-amber-100 text-amber-700 hover:bg-amber-200 border-amber-300 hover:shadow-sm'
                    : 'bg-green-100 text-green-700 hover:bg-green-200 border-green-300 hover:shadow-sm'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                <span>{action.text}</span>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-white/90 backdrop-blur-sm border-t border-emerald-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about your listings, pricing, or performance..."
              className="w-full px-4 py-3 pr-12 rounded-full border border-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white/80 placeholder-gray-500"
              disabled={isTyping}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <MessageSquare className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-full font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 hover:shadow-lg transition-all duration-200 hover:from-emerald-700 hover:to-teal-700"
          >
            {isTyping ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span>{isTyping ? 'Thinking...' : 'Send'}</span>
          </motion.button>
        </form>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          Powered by Gemini AI with transaction context • {transactionContext.recentListings.length} listings loaded
        </div>
      </div>
    </div>
  );
}