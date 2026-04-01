"use client";

import React from 'react';

type SchemeCardProps = {
  schemeId: string;
  schemeName?: string;
  status: 'Eligible' | 'Ineligible' | string;
  failedReasons?: string[];
  missingData?: string[];
};

export default function SchemeCard({ schemeId, schemeName, status, failedReasons = [], missingData = [] }: SchemeCardProps) {
  const isEligible = status === 'Eligible' || status === 'Potentially Eligible';
  
  // Format Scheme ID to readable title if name isn't provided
  const title = schemeName || schemeId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  
  return (
    <div className={`
      relative p-4 rounded-xl border mb-3
      transition-all duration-300
      ${isEligible 
        ? 'glass border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
        : 'glass border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10'}
    `}>
      <div className="flex items-center justify-between mb-2">
         <h4 className="font-semibold text-slate-100 flex items-center gap-2">
           {title}
           {isEligible && (
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
           )}
         </h4>
         <span className={`text-xs px-2 py-1 rounded-full font-medium ${isEligible ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
           {status}
         </span>
      </div>
      
      {!isEligible && failedReasons.length > 0 && (
        <div className="mt-3 text-sm text-slate-300">
           <p className="text-rose-400 font-medium text-xs uppercase tracking-wider mb-1">Failed Criteria</p>
           <ul className="list-disc pl-4 space-y-1">
             {failedReasons.map((r, i) => <li key={i}>{r}</li>)}
           </ul>
        </div>
      )}
      
      {!isEligible && missingData.length > 0 && (
         <div className="mt-3 text-sm text-slate-300">
           <p className="text-amber-400 font-medium text-xs uppercase tracking-wider mb-1">Missing Profile Data</p>
           <ul className="list-disc pl-4 space-y-1">
             {missingData.map((m, i) => <li key={i}>{m}</li>)}
           </ul>
         </div>
      )}
      
      {isEligible && (
         <div className="mt-3">
             <a href={`/explore/scheme/${schemeId}`} className="text-sm text-emerald-300 hover:text-emerald-200 decoration-emerald-500/30 underline decoration-2 underline-offset-4 font-medium transition-colors">
                 View Eligibility Proof & Steps →
             </a>
         </div>
      )}
    </div>
  );
}
