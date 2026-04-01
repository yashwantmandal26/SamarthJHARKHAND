import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)] mt-20 pb-20">
      
      {/* Hero Section */}
      <section className="relative px-6 pt-16 pb-24 md:pt-32 md:pb-40 overflow-hidden flex flex-col items-center text-center">
        {/* Glow Effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-500/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-teal-500/10 blur-[100px] rounded-full pointer-events-none"></div>

        <div className="relative z-10 max-w-4xl mx-auto stagger-1 page-enter opacity-0">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/50 mb-8 backdrop-blur-sm">
             <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
             </span>
             <span className="text-xs font-medium text-slate-300">Beta Version 1.0 Live</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            Find the right schemes.<br />
            <span className="text-gradient">For You, For Jharkhand.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Samarth is an AI-powered assistant designed to help citizens of Jharkhand discover, understand, and apply for government schemes effortlessly.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link 
              href="/chat" 
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold text-lg hover:shadow-[0_0_25px_rgba(245,158,11,0.5)] transition-all transform hover:-translate-y-1 w-full sm:w-auto text-center"
            >
              Start AI Assistant
            </Link>
            <Link 
              href="/explore" 
              className="px-8 py-4 rounded-xl glass hover:bg-slate-800 text-white font-bold text-lg transition-all w-full sm:w-auto text-center"
            >
              Explore Schemes Manually
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 w-full max-w-6xl mx-auto px-6 mb-24 stagger-3 page-enter opacity-0" style={{ animationDelay: '400ms' }}>
         <div className="glass-card rounded-3xl p-8 md:p-12 flex flex-col md:flex-row items-center justify-around gap-8 md:gap-4">
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">25+</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">Active Schemes</div>
            </div>
            <div className="hidden md:block w-px h-16 bg-slate-700/50"></div>
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">6</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">Key Categories</div>
            </div>
            <div className="hidden md:block w-px h-16 bg-slate-700/50"></div>
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">100%</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">Deterministic Accuracy</div>
            </div>
         </div>
      </section>

      {/* How it works */}
      <section className="max-w-7xl mx-auto px-6 mb-32 w-full">
         <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">How Samarth Works</h2>
            <p className="text-slate-400">Discover your eligibility in three simple steps</p>
         </div>

         <div className="grid md:grid-cols-3 gap-8">
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300">
               <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                  👋
               </div>
               <h3 className="text-xl font-bold text-white mb-3">1. Tell us about you</h3>
               <p className="text-slate-400">Chat with Samarth in your preferred language. Share basic details like your occupation, age, or income.</p>
            </div>
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300">
               <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                  🧠
               </div>
               <h3 className="text-xl font-bold text-white mb-3">2. AI Matches Schemes</h3>
               <p className="text-slate-400">Our deterministic engine scans all active government schemes to find the ones you explicitly qualify for.</p>
            </div>
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300 flex flex-col justify-between">
               <div>
                 <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                    ✅
                 </div>
                 <h3 className="text-xl font-bold text-white mb-3">3. Apply with Confidence</h3>
                 <p className="text-slate-400 mb-6">Get step-by-step guidance, required document lists, and direct links to official application portals.</p>
               </div>
               <Link href="/chat" className="text-orange-400 font-medium hover:text-orange-300 transition-colors inline-block mt-auto">Try it out →</Link>
            </div>
         </div>
      </section>

    </div>
  );
}
