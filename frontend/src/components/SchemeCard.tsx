"use client";

import React from 'react';
import Link from 'next/link';
import { useLanguage } from '@/context/LanguageContext';

type SchemeCardProps = {
  schemeId: string;
  schemeName?: string;
  status: 'Eligible' | 'Potentially Eligible' | 'Ineligible' | string;
  deterministicOutcome?: 'pass' | 'missing' | 'fail';
  failedReasons?: string[];
  missingData?: string[];
};

export default function SchemeCard({ schemeId, schemeName, status, deterministicOutcome, failedReasons = [], missingData = [] }: SchemeCardProps) {
  const { t } = useLanguage();

  const resolvedOutcome: 'pass' | 'missing' | 'fail' = deterministicOutcome
    ? deterministicOutcome
    : failedReasons.length > 0
    ? 'fail'
    : missingData.length > 0
    ? 'missing'
    : status === 'Eligible'
    ? 'pass'
    : status === 'Potentially Eligible'
    ? 'missing'
    : 'fail';

  const isEligible = resolvedOutcome === 'pass';
  const isPotential = resolvedOutcome === 'missing';
  const isPositive = isEligible || isPotential;
  
  // Format Scheme ID to readable title if name isn't provided
  const title = schemeName || schemeId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  
  // Color classes based on status
  const borderColor = isEligible 
    ? 'border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
    : isPotential
    ? 'border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/15 shadow-[0_0_15px_rgba(245,158,11,0.1)]'
    : 'border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10';

  const badgeColor = isEligible
    ? 'bg-emerald-500/20 text-emerald-300'
    : isPotential
    ? 'bg-amber-500/20 text-amber-300'
    : 'bg-rose-500/20 text-rose-300';

  const dotColor = isEligible ? 'bg-emerald-400' : 'bg-amber-400';
  const dotBg = isEligible ? 'bg-emerald-500' : 'bg-amber-500';

  return (
    <div className={`relative p-4 rounded-xl border mb-3 transition-all duration-300 glass ${borderColor}`}>
      <div className="flex items-center justify-between mb-2">
         <h4 className="font-semibold text-slate-100 flex items-center gap-2">
           {title}
           {isPositive && (
              <span className="flex h-3 w-3 relative">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${dotColor} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-3 w-3 ${dotBg}`}></span>
              </span>
           )}
         </h4>
         <span className={`text-xs px-2 py-1 rounded-full font-medium ${badgeColor}`}>
           {isEligible ? 'Eligible' : isPotential ? 'Potentially Eligible' : 'Ineligible'}
         </span>
      </div>
      
      {!isPositive && failedReasons.length > 0 && (
        <div className="mt-3 text-sm text-slate-300">
           <p className="text-rose-400 font-medium text-xs uppercase tracking-wider mb-1">{t('chatcard.failed')}</p>
           <ul className="list-disc pl-4 space-y-1">
             {failedReasons.map((r, i) => <li key={i}>{r}</li>)}
           </ul>
        </div>
      )}
      
      {isPotential && missingData.length > 0 && (
         <div className="mt-3 text-sm text-slate-300">
           <p className="text-amber-400 font-medium text-xs uppercase tracking-wider mb-1">{t('chatcard.missing')}</p>
           <ul className="list-disc pl-4 space-y-1">
             {missingData.map((m, i) => <li key={i}>{m}</li>)}
           </ul>
         </div>
      )}

      {!isPositive && missingData.length > 0 && (
         <div className="mt-3 text-sm text-slate-300">
           <p className="text-amber-400 font-medium text-xs uppercase tracking-wider mb-1">{t('chatcard.missing')}</p>
           <ul className="list-disc pl-4 space-y-1">
             {missingData.map((m, i) => <li key={i}>{m}</li>)}
           </ul>
         </div>
      )}
      
      {isPositive && (
         <div className="mt-3">
             <Link href={`/explore/scheme/${schemeId}`} className={`text-sm ${isEligible ? 'text-emerald-300 hover:text-emerald-200 decoration-emerald-500/30' : 'text-amber-300 hover:text-amber-200 decoration-amber-500/30'} underline decoration-2 underline-offset-4 font-medium transition-colors`}>
                 {t('chatcard.view_proof')}
             </Link>
         </div>
      )}
    </div>
  );
}
