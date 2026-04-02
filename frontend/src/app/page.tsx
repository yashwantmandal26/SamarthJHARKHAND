"use client";

import React from 'react';
import Link from 'next/link';
import { useLanguage } from '@/context/LanguageContext';

export default function Home() {
  const { t, lang } = useLanguage();

  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)] mt-20 pb-0">
      
      {/* ═══════════════════ HERO SECTION ═══════════════════ */}
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
             <span className="text-xs font-medium text-slate-300">{t('home.badge')}</span>
          </div>

          {/* BILINGUAL HERO — always show both English & Hindi */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-2">
            Find the right schemes.<br />
            <span className="text-gradient">For You, For Jharkhand.</span>
          </h1>
          <p className="text-xl md:text-2xl font-hindi text-orange-400/80 font-semibold mb-8">
            सही योजनाएँ खोजें। आपके लिए, झारखंड के लिए।
          </p>
          
          <p className="text-lg md:text-xl text-slate-400 mb-4 max-w-2xl mx-auto leading-relaxed">
            {t('home.hero.desc')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
            <Link 
              href="/chat" 
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold text-lg hover:shadow-[0_0_25px_rgba(245,158,11,0.5)] transition-all transform hover:-translate-y-1 w-full sm:w-auto text-center"
            >
              {t('home.cta.assistant')}
            </Link>
            <Link 
              href="/explore" 
              className="px-8 py-4 rounded-xl glass hover:bg-slate-800 text-white font-bold text-lg transition-all w-full sm:w-auto text-center"
            >
              {t('home.cta.explore')}
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════════════ STATS SECTION ═══════════════════ */}
      <section className="relative z-10 w-full max-w-6xl mx-auto px-6 mb-24 stagger-3 page-enter opacity-0" style={{ animationDelay: '400ms' }}>
         <div className="glass-card rounded-3xl p-8 md:p-12 flex flex-col md:flex-row items-center justify-around gap-8 md:gap-4">
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">25+</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">{t('home.stats.schemes')}</div>
            </div>
            <div className="hidden md:block w-px h-16 bg-slate-700/50"></div>
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">6</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">{t('home.stats.categories')}</div>
            </div>
            <div className="hidden md:block w-px h-16 bg-slate-700/50"></div>
            <div className="text-center">
               <div className="text-4xl font-bold text-white mb-2">100%</div>
               <div className="text-sm font-medium text-slate-400 uppercase tracking-wider">{t('home.stats.accuracy')}</div>
            </div>
         </div>
      </section>

      {/* ═══════════════════ HOW IT WORKS ═══════════════════ */}
      <section className="max-w-7xl mx-auto px-6 mb-32 w-full">
         <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">{t('home.how.title')}</h2>
            <p className="text-slate-400">{t('home.how.subtitle')}</p>
         </div>

         <div className="grid md:grid-cols-3 gap-8">
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300">
               <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                  👋
               </div>
               <h3 className="text-xl font-bold text-white mb-3">{t('home.how.step1.title')}</h3>
               <p className="text-slate-400">{t('home.how.step1.desc')}</p>
            </div>
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300">
               <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                  🧠
               </div>
               <h3 className="text-xl font-bold text-white mb-3">{t('home.how.step2.title')}</h3>
               <p className="text-slate-400">{t('home.how.step2.desc')}</p>
            </div>
            <div className="glass p-8 rounded-3xl text-center hover:-translate-y-2 transition-transform duration-300 flex flex-col justify-between">
               <div>
                 <div className="w-16 h-16 mx-auto bg-slate-800 rounded-2xl flex items-center justify-center mb-6 shadow-inner text-2xl border border-slate-700">
                    ✅
                 </div>
                 <h3 className="text-xl font-bold text-white mb-3">{t('home.how.step3.title')}</h3>
                 <p className="text-slate-400 mb-6">{t('home.how.step3.desc')}</p>
               </div>
               <Link href="/chat" className="text-orange-400 font-medium hover:text-orange-300 transition-colors inline-block mt-auto">{t('home.how.tryit')}</Link>
            </div>
         </div>
      </section>

      {/* ═══════════════════ ABOUT / PROJECT DESCRIPTION ═══════════════════ */}
      <section className="relative w-full overflow-hidden">
        {/* Top gradient divider */}
        <div className="w-full h-px bg-gradient-to-r from-transparent via-orange-500/40 to-transparent"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-24 md:py-32">
          {/* Background glow */}
          <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-orange-500/5 blur-[120px] rounded-full pointer-events-none"></div>
          <div className="absolute top-0 right-1/4 w-[400px] h-[400px] bg-teal-500/5 blur-[100px] rounded-full pointer-events-none"></div>

          <div className="relative z-10">
            {/* Section header */}
            <div className="text-center mb-16">
              <span className="inline-block px-4 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/50 text-xs font-semibold text-orange-400 uppercase tracking-widest mb-6">
                {t('home.footer.made')}
              </span>
              <h2 className="text-3xl md:text-5xl font-bold mb-4 tracking-tight">
                {t('home.about.title')}
              </h2>
              <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                {t('home.about.subtitle')}
              </p>
            </div>

            {/* Description paragraphs */}
            <div className="max-w-4xl mx-auto mb-20 space-y-6">
              <p className="text-slate-300 text-lg leading-relaxed text-center">
                {t('home.about.p1')}
              </p>
              <p className="text-slate-400 text-base leading-relaxed text-center">
                {t('home.about.p2')}
              </p>
            </div>

            {/* Feature cards grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
              {/* Feature 1 */}
              <div className="glass p-6 rounded-2xl hover:-translate-y-1 transition-transform duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500/20 to-amber-500/10 flex items-center justify-center mb-4 text-xl border border-orange-500/20 group-hover:border-orange-500/40 transition-colors">
                  🤖
                </div>
                <h3 className="text-base font-bold text-white mb-2">{t('home.about.feature1.title')}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{t('home.about.feature1.desc')}</p>
              </div>

              {/* Feature 2 */}
              <div className="glass p-6 rounded-2xl hover:-translate-y-1 transition-transform duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/10 flex items-center justify-center mb-4 text-xl border border-teal-500/20 group-hover:border-teal-500/40 transition-colors">
                  🌐
                </div>
                <h3 className="text-base font-bold text-white mb-2">{t('home.about.feature2.title')}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{t('home.about.feature2.desc')}</p>
              </div>

              {/* Feature 3 */}
              <div className="glass p-6 rounded-2xl hover:-translate-y-1 transition-transform duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-indigo-500/10 flex items-center justify-center mb-4 text-xl border border-blue-500/20 group-hover:border-blue-500/40 transition-colors">
                  🔒
                </div>
                <h3 className="text-base font-bold text-white mb-2">{t('home.about.feature3.title')}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{t('home.about.feature3.desc')}</p>
              </div>

              {/* Feature 4 */}
              <div className="glass p-6 rounded-2xl hover:-translate-y-1 transition-transform duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500/20 to-rose-500/10 flex items-center justify-center mb-4 text-xl border border-pink-500/20 group-hover:border-pink-500/40 transition-colors">
                  📋
                </div>
                <h3 className="text-base font-bold text-white mb-2">{t('home.about.feature4.title')}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{t('home.about.feature4.desc')}</p>
              </div>
            </div>

            {/* Tech stack banner */}
            <div className="glass-card rounded-2xl p-6 md:p-8 text-center max-w-3xl mx-auto mb-16 border-orange-500/10">
              <h3 className="text-sm font-bold text-orange-400 uppercase tracking-widest mb-3">{t('home.about.tech.title')}</h3>
              <p className="text-slate-400 text-sm leading-relaxed font-mono">
                {t('home.about.tech.desc')}
              </p>
            </div>

            {/* CTA */}
            <div className="text-center mb-16">
              <Link
                href="/chat"
                className="inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold text-lg hover:shadow-[0_0_30px_rgba(245,158,11,0.5)] transition-all transform hover:-translate-y-1 hover:scale-105"
              >
                {t('home.cta.assistant')}
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════ FOOTER ═══════════════════ */}
      <footer className="w-full border-t border-slate-800/60 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <p className="text-center text-xs text-slate-500 leading-relaxed max-w-3xl mx-auto">
            {t('home.footer.disclaimer')}
          </p>
          <div className="flex justify-center items-center gap-3 mt-6">
            <span className="text-sm font-bold text-gradient">समर्थ</span>
            <span className="text-slate-600">|</span>
            <span className="text-xs text-slate-500">{t('home.footer.made')}</span>
            <span className="text-slate-600">|</span>
            <span className="text-xs text-slate-500">© {new Date().getFullYear()}</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
