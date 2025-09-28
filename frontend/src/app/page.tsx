'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Zap, Play, Package, FileText, Coffee, BookOpen, Headphones, Camera, Smartphone, Shirt, Laptop, Gamepad2, Watch, TreePine, Sofa, Heart, DollarSign, Bot, Eye, Tag, Globe, MessageCircle, BarChart3 } from 'lucide-react';

const FloatingItem = ({ 
  icon: Icon, 
  className, 
  delay = 0, 
  x = 0, 
  y = 0,
  opacity = 1 
}: { 
  icon: any; 
  className: string; 
  delay?: number; 
  x?: number; 
  y?: number;
  opacity?: number;
}) => (
  <motion.div
    className={className}
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ 
      opacity: opacity,
      x: [0, x, 0], 
      y: [0, y, 0],
      scale: [1, 1.1, 1],
      rotate: [0, 2, -2, 0]
    }}
    transition={{ 
      duration: 8, 
      repeat: Infinity, 
      ease: 'easeInOut', 
      delay,
      opacity: { duration: 0.6, delay }
    }}
  >
    <Icon className="w-6 h-6 text-slate-600" />
  </motion.div>
);

const ScanBeam = () => (
  <motion.div
    className="absolute top-0 bottom-0 w-1 bg-gradient-to-b from-transparent via-teal-400 to-transparent opacity-60"
    animate={{ x: ['0%', '100%'] }}
    transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
  />
);

const MouseLight = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div
      className="fixed pointer-events-none z-30 mix-blend-screen"
      style={{
        left: mousePosition.x - 150,
        top: mousePosition.y - 150,
      }}
    >
      <div className="w-[300px] h-[300px] bg-gradient-radial from-[#F6EFD9]/20 via-[#F6EFD9]/10 to-transparent rounded-full blur-xl" />
    </div>
  );
};

export default function Home() {
  return (
    <div className="relative">
      {/* Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold">
                <span className="text-[#5BAAA7]">de</span>
                <span className="text-slate-900">Cluttered</span>
                <span className="text-[#5BAAA7]">.ai</span>
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#how-it-works" className="text-gray-700 hover:text-[#5BAAA7] font-medium transition-colors">How It Works</a>
              <a href="#features" className="text-gray-700 hover:text-[#5BAAA7] font-medium transition-colors">Features</a>
              <a href="#pricing" className="text-gray-700 hover:text-[#5BAAA7] font-medium transition-colors">Pricing</a>
              <button className="px-6 py-2 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-lg hover:shadow-lg transition-all">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="min-h-screen relative overflow-hidden group pt-16">
        {/* Mouse Light Effect */}
        <MouseLight />
        
        {/* AI Scanning beam */}
        <ScanBeam />
        
        {/* Background images with hover transition */}
        <div className="absolute inset-0">
          {/* Clutter image - default state */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-all duration-1000 ease-in-out opacity-50 group-hover:opacity-0 transform group-hover:scale-105"
            style={{
              backgroundImage: 'url(/clutter.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundAttachment: 'fixed'
            }}
          />
          
          {/* Declutter image - hover state */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-all duration-1000 ease-in-out opacity-0 group-hover:opacity-50 transform scale-105 group-hover:scale-100"
            style={{
              backgroundImage: 'url(/declutter.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundAttachment: 'fixed'
            }}
          />
          
          
          {/* Subtle animation overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-pulse opacity-10" />
        </div>

      {/* Content positioned higher up */}
      <div className="relative z-10 flex items-start justify-center min-h-screen px-4 sm:px-6 lg:px-10 pt-32">
        <div className="max-w-4xl mx-auto text-center">
          {/* Tagline */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1 }} className="mb-8">
            <div className="inline-flex items-center gap-2 text-black font-medium bg-[#F6EFD9]/20 backdrop-blur-sm rounded-full px-6 py-3 border border-[#F6EFD9]/30">
              <Zap className="w-5 h-5 text-black" />
              <span>AI Automated</span>
            </div>
          </motion.div>

          {/* Headlines */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: -20 }} transition={{ duration: 0.8, delay: 0.2 }} className="mb-8">
            <h2 className="text-5xl sm:text-6xl font-extrabold text-white mb-2 drop-shadow-lg">See the clutter.</h2>
              <h2 className="text-5xl sm:text-6xl font-extrabold drop-shadow-lg">
                <span className="text-white">Watch it</span>
                <span className="ml-2 text-[#F6EFD9] [text-shadow:_0_0_0_#000,_0_0_0_#000,_0_0_0_#000,_0_0_0_#000,_0_0_0_#000,_0_0_0_#000,_0_0_0_#000,_0_0_0_#000]">disappear.</span>
              </h2>
          </motion.div>

          {/* Description */}
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }} className="text-xl text-black leading-relaxed mb-8 max-w-2xl mx-auto bg-[#F6EFD9]/20 backdrop-blur-md rounded-2xl p-8 border border-[#F6EFD9]/30 shadow-xl">
            AI that scans your space, identifies what's resellable, and turns unused items into cash—automatically.
          </motion.p>

          {/* CTAs */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.35 }} className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <motion.button 
                whileHover={{ scale: 1.05, y: -2 }} 
                whileTap={{ scale: 0.95 }} 
                className="px-8 py-4 bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all backdrop-blur-sm border border-white/20"
              >
                Start Selling
              </motion.button>
              <motion.button 
                whileHover={{ scale: 1.05, y: -2 }} 
                whileTap={{ scale: 0.95 }} 
                className="px-8 py-4 border-2 border-black bg-[#F6EFD9] rounded-xl font-semibold text-black hover:bg-[#F6EFD9]/80 transition-all shadow-lg"
              >
                <span className="inline-flex items-center gap-2">
                  <Play className="w-5 h-5" /> Watch Demo
                </span>
              </motion.button>
          </motion.div>

          {/* Badges */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }} className="flex flex-wrap gap-3 justify-center">
            {['Detect Items Instantly', 'Auto-Price for Resale', 'Multi-Marketplace Listings', 'Hands-Free Sales'].map((text) => (
              <div key={text} className="rounded-full p-[2px] bg-gradient-to-r from-[#5BAAA7] to-[#1A6A6A] shadow-lg">
                <div className="px-4 py-2 rounded-full bg-white/95 backdrop-blur-sm text-slate-700 text-sm font-medium shadow-lg">
                  {text}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
      </div>

      {/* Section 1 - How It Works */}
      <section id="how-it-works" className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-[#0a1b2a] mb-4">How It Works</h2>
            <p className="text-xl text-[#6b7b8c]">Three simple steps to turn clutter into cash</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { 
                number: "01",
                title: "Snap & Detect", 
                desc: "Take a photo of your space, and AI finds clutter instantly.",
                gradient: "from-[#F6EFD9] to-[#CDE7E2]"
              },
              { 
                number: "02",
                title: "Auto-List & Price", 
                desc: "We create marketplace listings with fair prices and smart tags.",
                gradient: "from-[#CDE7E2] to-[#5BAAA7]"
              },
              { 
                number: "03",
                title: "Sell Hands-Free", 
                desc: "Declutter while our AI manages buyers, messages, and offers.",
                gradient: "from-[#5BAAA7] to-[#1A6A6A]"
              }
            ].map((step, index) => (
              <div
                key={index}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-slate-200/50 relative overflow-hidden group"
              >
                {/* Background gradient */}
                <div className={`absolute inset-0 bg-gradient-to-br ${step.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                
                {/* Step number */}
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${step.gradient} flex items-center justify-center mb-6 relative z-10`}>
                  <span className="text-2xl font-bold text-white">{step.number}</span>
                </div>
                
                <h3 className="text-2xl font-bold text-slate-900 mb-4 relative z-10">{step.title}</h3>
                <p className="text-slate-600 leading-relaxed relative z-10">{step.desc}</p>
                
                {/* Subtle border accent */}
                <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${step.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <button className="px-10 py-4 bg-gradient-to-r from-[#0ecfba] to-[#1dd2aa] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all">
              Start Selling Now
            </button>
          </div>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section id="features" className="py-16 bg-slate-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-[#0a1b2a] mb-4">Why Choose deCluttered.ai</h2>
            <p className="text-xl text-[#6b7b8c]">Powerful features that make decluttering effortless</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { 
                number: "01",
                title: "AI-Powered Detection", 
                desc: "Advanced computer vision instantly identifies and categorizes items in your space.",
                gradient: "from-[#F6EFD9] to-[#CDE7E2]"
              },
              { 
                number: "02",
                title: "Smart Pricing", 
                desc: "AI analyzes market data to suggest optimal prices for maximum resale value.",
                gradient: "from-[#CDE7E2] to-[#5BAAA7]"
              },
              { 
                number: "03",
                title: "Multi-Platform Listings", 
                desc: "Automatically posts to eBay, Facebook Marketplace, and other major platforms.",
                gradient: "from-[#5BAAA7] to-[#1A6A6A]"
              },
              { 
                number: "04",
                title: "Hands-Free Sales", 
                desc: "AI manages buyer communications, negotiations, and transactions for you.",
                gradient: "from-[#1A6A6A] to-[#F6EFD9]"
              }
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl border-2 border-slate-200/50 hover:border-[#5BAAA7]/50 hover:shadow-2xl transition-all duration-300 relative overflow-hidden group"
              >
                {/* Background gradient */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                
                {/* Feature number */}
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 relative z-10`}>
                  <span className="text-2xl font-bold text-white">{feature.number}</span>
                </div>
                
                <h3 className="text-2xl font-bold text-slate-900 mb-4 relative z-10">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed relative z-10">{feature.desc}</p>
                
                {/* Subtle border accent */}
                <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 bg-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-extrabold text-slate-900 mb-6">Decluttering made effortless.</h2>
              <div className="space-y-6">
                <div className="flex items-start gap-4 bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-slate-200/50">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#F6EFD9] to-[#CDE7E2] flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Zap className="w-6 h-6 text-[#1A6A6A]" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Save Time</h3>
                    <p className="text-slate-600">Save hours of manual listing & pricing.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-slate-200/50">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#CDE7E2] to-[#5BAAA7] flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Heart className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Peace of Mind</h3>
                    <p className="text-slate-600">Enjoy a cleaner, stress-free space.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-slate-200/50">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#5BAAA7] to-[#1A6A6A] flex items-center justify-center flex-shrink-0 shadow-lg">
                    <DollarSign className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Extra Income</h3>
                    <p className="text-slate-600">Turn forgotten items into extra income.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-slate-200/50">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#1A6A6A] to-[#F6EFD9] flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Bot className="w-6 h-6 text-[#1A6A6A]" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">AI Automation</h3>
                    <p className="text-slate-600">All managed automatically by AI.</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-white to-slate-100 relative overflow-hidden border-2 border-slate-300 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-white/80 to-transparent"></div>
                
                {/* Clean house illustration */}
                <div className="absolute inset-8 flex items-center justify-center">
                  <div className="w-64 h-64 relative">
                    {/* House structure */}
                    <div className="absolute inset-0 bg-white rounded-lg border-4 border-slate-400 shadow-xl">
                      {/* Roof */}
                      <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[60px] border-r-[60px] border-b-[40px] border-l-transparent border-r-transparent border-b-teal-400"></div>
                      
                      {/* Windows */}
                      <div className="absolute top-8 left-8 w-12 h-12 bg-cyan-200 rounded-lg border-2 border-cyan-400 shadow-lg"></div>
                      <div className="absolute top-8 right-8 w-12 h-12 bg-cyan-200 rounded-lg border-2 border-cyan-400 shadow-lg"></div>
                      
                      {/* Door */}
                      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-16 h-20 bg-teal-200 rounded-t-lg border-2 border-teal-400 shadow-lg"></div>
                      
                      {/* Clean lines */}
                      <div className="absolute top-1/2 left-4 right-4 h-px bg-slate-300"></div>
                    </div>
                    
                    {/* Clean decorative elements */}
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-teal-400 rounded-full shadow-lg"></div>
                    <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-cyan-400 rounded-full shadow-lg"></div>
                    <div className="absolute top-4 -left-4 w-4 h-4 bg-emerald-400 rounded-full shadow-lg"></div>
                  </div>
                </div>
                
                {/* Status indicators */}
                <div className="absolute top-6 right-6">
                  <div className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-bold shadow-xl">
                    ✓ Clean
                  </div>
                </div>
                <div className="absolute bottom-6 left-6">
                  <div className="bg-teal-500 text-white px-4 py-2 rounded-full text-sm font-bold shadow-xl">
                    Organized
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2 - Features Grid */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-[#0a1b2a] mb-4">Smart Assistant Powers</h2>
            <p className="text-xl text-[#6b7b8c]">AI that handles everything, so you don't have to</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: Eye, gradient: "from-[#F6EFD9] to-[#CDE7E2]", title: "Object Identification", desc: "Detect items instantly with computer vision." },
              { icon: DollarSign, gradient: "from-[#CDE7E2] to-[#5BAAA7]", title: "Sellability Check", desc: "Know what's worth selling vs. donating." },
              { icon: Tag, gradient: "from-[#5BAAA7] to-[#1A6A6A]", title: "Automatic Listings", desc: "AI creates complete product listings." },
              { icon: Globe, gradient: "from-[#1A6A6A] to-[#F6EFD9]", title: "Marketplace Integration", desc: "Post across eBay, Facebook, Craigslist." },
              { icon: MessageCircle, gradient: "from-[#F6EFD9] to-[#CDE7E2]", title: "Buyer Management", desc: "Auto-handle messages, negotiations, offers." },
              { icon: BarChart3, gradient: "from-[#CDE7E2] to-[#5BAAA7]", title: "Seller Dashboard", desc: "One hub to track all sales, offers, and earnings." }
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl border-2 border-slate-200/50 hover:border-[#5BAAA7]/50 hover:shadow-2xl transition-all duration-300"
              >
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-[#0a1b2a] mb-4">{feature.title}</h3>
                <p className="text-[#6b7b8c] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 3 - Integrations */}
      <section className="py-20 bg-slate-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-[#0a1b2a] mb-4">Trusted Marketplaces</h2>
            <p className="text-xl text-[#6b7b8c]">Your listings go live where buyers are already searching.</p>
          </div>
          
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60 hover:opacity-100 transition-opacity">
            {["eBay", "Facebook Marketplace", "Craigslist", "OfferUp", "Mercari", "Poshmark"].map((platform, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 0.6, scale: 1 }}
                whileHover={{ opacity: 1, scale: 1.05 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="px-6 py-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-md text-slate-600 font-semibold hover:text-[#5BAAA7] transition-colors border border-slate-200/50"
              >
                {platform}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 7 - Final CTA */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#5BAAA7] via-[#1A6A6A] to-[#CDE7E2]">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-pulse"></div>
        </div>
        
        <div className="relative z-10 max-w-4xl mx-auto px-6 lg:px-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-5xl font-extrabold text-white mb-6">Turn clutter into cash. Hands-free.</h2>
            <p className="text-xl text-white/90 mb-12">Start today and let AI do the heavy lifting.</p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-white text-teal-600 font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all"
              >
                ➡️ Start Selling
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-teal-600 transition-all"
              >
                ▶️ Watch Demo
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}