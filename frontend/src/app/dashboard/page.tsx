'use client';

import { motion } from 'framer-motion';
import { Camera, Clock, Play, Upload, History, Activity, BarChart3 } from 'lucide-react';
import Image from 'next/image';
import { ThemeToggle } from '@/components/ThemeToggle';

const Card = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className={`rounded-2xl border border-gray-200/60 dark:border-gray-700/60 bg-white/80 dark:bg-slate-900/60 backdrop-blur-sm shadow-sm hover:shadow-md transition-shadow ${className}`}
  >
    {children}
  </motion.div>
);

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[linear-gradient(135deg,#fafaff_0%,#eff7ff_100%)] dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-20 backdrop-blur-md border-b border-gray-200/60 dark:border-gray-800 bg-white/70 dark:bg-slate-900/60">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            <span className="text-purple-700">de</span>
            <span className="text-orange-500">Cluttered</span>
            <span className="text-teal-500">.ai</span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8 grid gap-8 lg:grid-cols-12">
        {/* Analytics Section */}
        <section className="lg:col-span-8 space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[{
              title: 'Clutter Events', value: '28', accent: 'from-teal-400/30 to-emerald-400/30'
            },{
              title: 'Weekly Trend', value: '+12%', accent: 'from-purple-400/30 to-indigo-400/30'
            },{
              title: 'Avg. Time to Clear', value: '3.2h', accent: 'from-orange-400/30 to-pink-400/30'
            }].map((item) => (
              <Card key={item.title}>
                <div className={`p-5 rounded-2xl bg-gradient-to-br ${item.accent}`}>
                  <div className="text-sm text-gray-600 dark:text-gray-300">{item.title}</div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{item.value}</div>
                </div>
              </Card>
            ))}
          </div>

          {/* Detection Cards */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2"><Camera className="w-5 h-5" /> Detections</h2>
              <button className="text-sm text-teal-600 hover:underline">View all</button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1,2,3,4,5,6].map((i) => (
                <Card key={i}>
                  <div className="p-3">
                    <div className="relative rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 aspect-video">
                      <Image src="/vercel.svg" alt="thumb" fill className="object-contain p-6 opacity-40" />
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300 mt-3">
                      <span className="inline-flex items-center gap-1"><Clock className="w-4 h-4" /> 2:14 PM</span>
                      <span className="inline-flex items-center gap-1 text-purple-600 dark:text-purple-300"><Activity className="w-4 h-4" /> Moderate clutter</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Right column: Quick actions and chart placeholder */}
        <aside className="lg:col-span-4 space-y-6">
          <Card>
            <div className="p-5">
              <h3 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button className="px-4 py-3 rounded-xl bg-teal-500 text-white font-medium shadow hover:shadow-md active:scale-[0.98] transition-all inline-flex items-center justify-center gap-2"><Play className="w-4 h-4" /> Start Monitoring</button>
                <button className="px-4 py-3 rounded-xl border-2 border-purple-500 text-purple-600 dark:text-purple-300 font-medium hover:bg-purple-500 hover:text-white transition-all inline-flex items-center justify-center gap-2"><Upload className="w-4 h-4" /> Upload Snapshot</button>
                <button className="px-4 py-3 rounded-xl border-2 border-cyan-500 text-cyan-600 dark:text-cyan-300 font-medium hover:bg-cyan-500 hover:text-white transition-all inline-flex items-center justify-center gap-2"><History className="w-4 h-4" /> View History</button>
                <button className="px-4 py-3 rounded-xl border-2 border-rose-400 text-rose-500 dark:text-rose-300 font-medium hover:bg-rose-400 hover:text-white transition-all inline-flex items-center justify-center gap-2"><BarChart3 className="w-4 h-4" /> Open Analytics</button>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-5">
              <h3 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-3">Trends</h3>
              <div className="h-40 rounded-xl bg-gradient-to-br from-purple-200/40 to-teal-200/40 dark:from-purple-900/40 dark:to-teal-900/30" />
            </div>
          </Card>
        </aside>
      </main>

      {/* Floating live widget */}
      <Card>
        <div className="fixed bottom-6 right-6 w-[320px] rounded-2xl overflow-hidden shadow-2xl border border-gray-200/70 dark:border-gray-700/60 bg-white/80 dark:bg-slate-900/70 backdrop-blur-md">
          <div className="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-200">Live Monitoring</div>
          <div className="relative aspect-video bg-gradient-to-br from-cyan-200/40 to-purple-200/40 dark:from-cyan-900/30 dark:to-purple-900/30" />
        </div>
      </Card>
    </div>
  );
}
