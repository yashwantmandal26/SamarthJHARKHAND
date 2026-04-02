"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useLanguage } from '@/context/LanguageContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SchemeDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const { t, lang } = useLanguage();
  
  const [scheme, setScheme] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    
    async function fetchScheme() {
      try {
        const res = await fetch(`${API_URL}/api/schemes/${id}`);
        if (res.ok) {
          const data = await res.json();
          setScheme(data);
        }
      } catch (err) {
        console.error("Failed to fetch scheme", err);
      } finally {
        setLoading(false);
      }
    }
    fetchScheme();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="w-12 h-12 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="flex justify-center items-center h-screen flex-col">
        <h1 className="text-3xl font-bold mb-4">{t('detail.not_found')}</h1>
        <Link href="/explore" className="text-orange-500 underline">{t('detail.return')}</Link>
      </div>
    );
  }

  // Translate category
  const catKey = `cat.${scheme.category}`;
  const translatedCategory = t(catKey) !== catKey ? t(catKey) : scheme.category.replace(/_/g, ' ');

  // Name display based on language
  const primaryName = lang === 'hi' ? scheme.name_hindi : scheme.name;
  const secondaryName = lang === 'hi' ? scheme.name : scheme.name_hindi;

  return (
    <div className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 py-20 page-enter">
      
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm font-medium">
        <ol className="list-none p-0 inline-flex items-center text-slate-400">
          <li className="flex items-center">
            <Link href="/explore" className="text-orange-500 hover:text-orange-400">{t('explore.title')}</Link>
            <span className="mx-2 text-slate-600">/</span>
          </li>
          <li className="flex items-center">
            <Link href={`/explore/${scheme.category}`} className="text-orange-500 hover:text-orange-400 capitalize">
              {translatedCategory}
            </Link>
            <span className="mx-2 text-slate-600">/</span>
          </li>
          <li className="text-slate-200 truncate max-w-[200px] sm:max-w-none">
            {primaryName}
          </li>
        </ol>
      </nav>

      {/* Header Banner */}
      <div className="relative glass-card rounded-3xl p-8 sm:p-12 mb-12 overflow-hidden border-orange-500/20">
        <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500/10 blur-[80px] rounded-full pointer-events-none"></div>
        <div className="relative z-10">
          <span className="inline-block px-3 py-1 bg-slate-800 text-orange-400 text-xs font-bold uppercase tracking-wider rounded-full border border-orange-500/30 mb-6">
            {scheme.department}
          </span>
          <h1 className="text-3xl sm:text-5xl font-bold text-white mb-3 tracking-tight">{primaryName}</h1>
          <h2 className="text-xl sm:text-2xl text-orange-400 font-hindi mb-6">{secondaryName}</h2>
          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl leading-relaxed">
            {scheme.description}
          </p>
          
          <div className="mt-8 flex flex-wrap gap-2">
            {scheme.tags.map((tag: string) => (
              <span key={tag} className="px-3 py-1 bg-slate-800/50 text-slate-300 rounded border border-slate-700/50 text-sm">
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Content (Left, 2/3) */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Eligibility Section */}
          <section className="glass p-8 rounded-3xl border-slate-800">
             <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
               <span className="text-orange-500">🎯</span> {t('detail.eligibility')}
             </h3>
             <ul className="space-y-4">
                {Object.entries(scheme.eligibility?.hard_constraints || {}).map(([rule, val]: [string, any]) => {
                   let displayVal = JSON.stringify(val);
                   let displayRule = rule.replace(/_/g, ' ').toUpperCase();
                   
                   if (Array.isArray(val)) displayVal = val.join(', ');
                   if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
                      displayVal = Object.entries(val).map(([k,v]) => `${k}: ${v}`).join(' | ');
                   }
                   
                   return (
                     <li key={rule} className="flex gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                        <div className="text-emerald-400 mt-0.5">✓</div>
                        <div>
                          <p className="text-xs font-bold text-slate-500 mb-1">{displayRule}</p>
                          <p className="text-slate-200 capitalize">{displayVal}</p>
                        </div>
                     </li>
                   );
                })}
             </ul>
          </section>

          {/* Documents Section */}
          <section className="glass p-8 rounded-3xl border-slate-800">
             <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
               <span className="text-orange-500">📄</span> {t('detail.documents')}
             </h3>
             <ul className="space-y-3">
                {scheme.documents_required?.map((doc: any, i: number) => (
                  <li key={i} className="flex items-start gap-4 pb-3 border-b border-slate-800 last:border-0 last:pb-0">
                    <div className="mt-1">
                      {doc.mandatory ? (
                        <span className="text-rose-400 font-bold text-lg">*</span>
                      ) : (
                        <span className="text-slate-500 text-sm italic">opt</span>
                      )}
                    </div>
                    <div>
                       <p className="text-white font-medium">{doc.name}</p>
                       {doc.condition && <p className="text-sm text-slate-400 mt-1">{doc.condition}</p>}
                    </div>
                  </li>
                ))}
             </ul>
             <p className="text-xs text-rose-400 mt-4">* {t('detail.mandatory')}</p>
          </section>

        </div>

        {/* Sidebar (Right, 1/3) */}
        <div className="space-y-8">
          
          {/* Benefit Box */}
          <section className="glass-card p-6 md:p-8 rounded-3xl border-emerald-500/20 bg-emerald-500/5 text-center relative overflow-hidden">
             <div className="absolute -top-10 -right-10 text-9xl opacity-5">💰</div>
             <h3 className="text-sm font-bold text-emerald-500 uppercase tracking-widest mb-4">{t('detail.benefit_type')}: {scheme.benefits?.type?.replace(/_/g, ' ')}</h3>
             
             {scheme.benefits?.amount ? (
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                  ₹{scheme.benefits.amount.toLocaleString()}
                </div>
             ) : scheme.benefits?.max_amount ? (
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {t('scheme_card.up_to')} ₹{scheme.benefits.max_amount.toLocaleString()}
                </div>
             ) : null}
             
             {scheme.benefits?.frequency && (
                <div className="text-slate-400 text-sm mb-6 capitalize px-4 py-1 bg-slate-800 rounded-full inline-block">
                  {scheme.benefits.frequency.replace(/_/g, ' ')}
                </div>
             )}
             
             <p className="text-slate-300 text-sm leading-relaxed border-t border-emerald-500/20 pt-4">
               {scheme.benefits?.description}
             </p>
          </section>

          {/* Application Process Box */}
          <section className="glass p-6 md:p-8 rounded-3xl border-slate-800 relative">
             <h3 className="text-xl font-bold mb-6 text-white border-b border-slate-800 pb-4">{t('detail.how_to_apply')}</h3>
             <div className="space-y-6">
                
                {scheme.application_process?.online_url && (
                   <div>
                     <p className="text-xs font-bold text-slate-500 uppercase mb-2">{t('detail.online_portal')}</p>
                     <a 
                      href={scheme.application_process.online_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full py-3 px-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold rounded-xl hover:shadow-[0_0_15px_rgba(245,158,11,0.4)] transition-all"
                     >
                       {t('detail.visit_site')}
                       <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                         <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                       </svg>
                     </a>
                   </div>
                )}

                <div>
                   <p className="text-xs font-bold text-slate-500 uppercase mb-4">{t('detail.manual_steps')}</p>
                   <ol className="relative border-l border-slate-700 ml-3 space-y-6">                  
                      {scheme.application_process?.offline_steps?.map((step: string, i: number) => (
                        <li key={i} className="mb-2 ml-6">            
                          <span className="absolute flex items-center justify-center w-6 h-6 bg-slate-800 rounded-full -left-3 ring-4 ring-[#0b1120] text-xs font-bold text-orange-400">
                            {i + 1}
                          </span>
                          <p className="text-sm text-slate-300 mt-1">{step}</p>
                        </li>
                      ))}
                   </ol>
                </div>
             </div>
          </section>

        </div>
      </div>
      
    </div>
  );
}
