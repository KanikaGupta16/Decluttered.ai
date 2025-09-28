'use client';

import { motion } from 'framer-motion';
import { Zap, Play } from 'lucide-react';

const bubble = (className: string, anim: any, delay = 0) => (
  <motion.div
    className={className}
    animate={anim}
    transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay }}
  />
);

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-[linear-gradient(135deg,#f8f6ff_0%,#eef7ff_100%)]">
      {/* Background: calm, airy bubbles */}
      <div className="absolute inset-0 overflow-hidden">
        {bubble(
          'absolute -top-40 -left-40 w-[26rem] h-[26rem] rounded-full blur-3xl bg-[radial-gradient(circle_at_30%_30%,rgba(255,183,148,0.35),rgba(255,129,122,0.25))]',
          { x: [0, 60, 0], y: [0, -35, 0], scale: [1, 1.08, 1] }
        )}
        {bubble(
          'absolute top-24 right-24 w-40 h-40 rounded-full blur-2xl bg-[radial-gradient(circle_at_70%_30%,rgba(186,144,255,0.35),rgba(129,140,248,0.28))]',
          { x: [0, -40, 0], y: [0, 25, 0], scale: [1, 0.94, 1] },
          1
        )}
        {bubble(
          'absolute -bottom-44 -left-16 w-[24rem] h-[24rem] rounded-full blur-3xl bg-[radial-gradient(circle_at_40%_60%,rgba(134,239,255,0.35),rgba(59,207,232,0.25))]',
          { x: [0, 40, 0], y: [0, -25, 0], scale: [1, 1.06, 1] },
          2
        )}
        {bubble(
          'absolute bottom-24 right-16 w-32 h-32 rounded-full blur-2xl bg-[radial-gradient(circle_at_50%_50%,rgba(98,247,208,0.35),rgba(34,197,154,0.25))]',
          { x: [0, -30, 0], y: [0, 18, 0], scale: [1, 0.9, 1] },
          3
        )}
        {bubble(
          'absolute top-40 right-52 w-24 h-24 rounded-full blur-xl bg-[radial-gradient(circle_at_60%_40%,rgba(255,170,197,0.35),rgba(244,114,182,0.25))]',
          { x: [0, 24, 0], y: [0, -14, 0], scale: [1, 1.15, 1] },
          4
        )}
      </div>

      {/* Content container */}
      <div className="relative z-10 mx-auto max-w-6xl px-6 lg:px-10 py-20">
        <div className="max-w-3xl mx-auto text-center">
          {/* Centered brand */}
          <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="mb-6">
            <h1 className="text-6xl sm:text-7xl font-extrabold tracking-tight">
              <span className="text-purple-700">de</span>
              <span className="text-orange-500">Cluttered</span>
              <span className="text-teal-500">.ai</span>
            </h1>
          </motion.div>

          {/* Tagline */}
          <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.05 }} className="mb-6">
            <div className="inline-flex items-center gap-2 text-purple-700 font-medium">
              <Zap className="w-5 h-5" />
              <span>AI-Powered Space Analysis</span>
            </div>
          </motion.div>

          {/* Headlines */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }} className="mb-4">
            <h2 className="text-6xl font-extrabold text-gray-900">See the change.</h2>
            <h2 className="text-6xl font-extrabold">
              <span className="text-orange-500">Clear</span>
              <span className="text-teal-500 ml-2">the clutter.</span>
            </h2>
          </motion.div>

          {/* Description */}
          <motion.p initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.15 }} className="text-xl text-gray-600 leading-relaxed mb-8">
            Transform your space with AI-powered computer vision. Detect changes, monitor clutter, and get intelligent insights about your environment.
          </motion.p>

          {/* CTAs */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }} className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <motion.button whileHover={{ scale: 1.03, y: -1 }} whileTap={{ scale: 0.98 }} className="px-6 py-3 bg-teal-500 text-white rounded-xl font-semibold shadow-md">
              []→ Start Detecting
            </motion.button>
            <motion.button whileHover={{ scale: 1.03, y: -1 }} whileTap={{ scale: 0.98 }} className="px-6 py-3 border-2 border-pink-500 text-pink-600 rounded-xl font-semibold bg-white/70 backdrop-blur-sm">
              <span className="inline-flex items-center gap-2"><Play className="w-5 h-5" /> Watch Demo</span>
            </motion.button>
          </motion.div>

          {/* Tags */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.25 }} className="flex flex-wrap gap-3 justify-center">
            {['Real-time Analysis', 'Gemini AI', 'Computer Vision', 'Smart Insights'].map((t) => (
              <span key={t} className="px-4 py-2 rounded-full bg-white/90 border border-gray-200 text-gray-700 text-sm shadow-sm">{t}</span>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  );
}