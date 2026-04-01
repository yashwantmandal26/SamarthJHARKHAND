import React from 'react';
import Link from 'next/link';

type Scheme = {
  scheme_id: string;
  name: string;
  name_hindi: string;
  department: string;
  category: string;
  description: string;
  benefits: any;
  tags: string[];
};

export default function ExploreSchemeCard({ scheme }: { scheme: Scheme }) {
  // Try to extract a readable amount
  let benefitText = "View Benefits Details";
  if (scheme.benefits?.amount) {
    benefitText = `₹${scheme.benefits.amount.toLocaleString()} ${scheme.benefits.frequency === 'monthly' ? '/ month' : ''}`;
  } else if (scheme.benefits?.max_amount) {
    benefitText = `Up to ₹${scheme.benefits.max_amount.toLocaleString()}`;
  }

  return (
    <div className="glass-card p-6 rounded-2xl flex flex-col h-full hover:shadow-[0_8px_30px_rgb(0,0,0,0.4)] transition-all duration-300 transform hover:-translate-y-1">
      <div className="mb-4">
        <span className="inline-block px-3 py-1 bg-slate-800 text-slate-300 text-xs font-semibold rounded-full border border-slate-700/50 mb-3 capitalize">
          {scheme.category.replace('_', ' ')}
        </span>
        <h3 className="text-xl font-bold text-white mb-1 leading-snug">{scheme.name}</h3>
        <h4 className="text-sm font-medium text-orange-400 font-hindi mb-3">{scheme.name_hindi}</h4>
        <p className="text-slate-400 text-sm line-clamp-3 leading-relaxed">
          {scheme.description}
        </p>
      </div>
      
      <div className="mt-auto pt-4 border-t border-slate-700/50 flex items-end justify-between">
        <div>
           <p className="text-[10px] uppercase tracking-wide text-slate-500 mb-1 font-semibold">Key Benefit</p>
           <p className="font-bold text-emerald-400 text-sm sm:text-base">{benefitText}</p>
        </div>
        <Link 
          href={`/explore/scheme/${scheme.scheme_id}`}
          className="text-sm font-medium text-white bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg transition-colors border border-slate-600 shadow-sm"
        >
          Details
        </Link>
      </div>
    </div>
  );
}
