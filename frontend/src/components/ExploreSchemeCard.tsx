"use client";

import React from 'react';
import Link from 'next/link';
import { useLanguage } from '@/context/LanguageContext';

type Scheme = {
  scheme_id: string;
  name: string;
  name_hindi: string;
  department: string;
  category: string;
  description: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  benefits: any;
  tags: string[];
};

export default function ExploreSchemeCard({ scheme }: { scheme: Scheme }) {
  const { t, lang } = useLanguage();

  // Try to extract a readable amount
  let benefitText = t('scheme_card.view_benefits');
  if (scheme.benefits?.amount) {
    const suffix = scheme.benefits.frequency === 'monthly' ? ` ${t('scheme_card.per_month')}` : '';
    benefitText = `₹${scheme.benefits.amount.toLocaleString()}${suffix}`;
  } else if (scheme.benefits?.max_amount) {
    benefitText = `${t('scheme_card.up_to')} ₹${scheme.benefits.max_amount.toLocaleString()}`;
  }

  // Show Hindi name as primary when Hindi is selected
  const primaryName = lang === 'hi' ? scheme.name_hindi : scheme.name;
  const secondaryName = lang === 'hi' ? scheme.name : scheme.name_hindi;

  // Translate category name
  const catKey = `cat.${scheme.category}`;
  const translatedCategory = t(catKey) !== catKey ? t(catKey) : scheme.category.replace(/_/g, ' ');

  return (
    <div className="glass-card p-6 rounded-2xl flex flex-col h-full hover:shadow-[0_8px_30px_rgb(0,0,0,0.4)] transition-all duration-300 transform hover:-translate-y-1">
      <div className="mb-4">
        <span className="inline-block px-3 py-1 bg-slate-800 text-slate-300 text-xs font-semibold rounded-full border border-slate-700/50 mb-3 capitalize">
          {translatedCategory}
        </span>
        <h3 className="text-xl font-bold text-white mb-1 leading-snug">{primaryName}</h3>
        <h4 className="text-sm font-medium text-orange-400 font-hindi mb-3">{secondaryName}</h4>
        <p className="text-slate-400 text-sm line-clamp-3 leading-relaxed">
          {scheme.description}
        </p>
      </div>
      
      <div className="mt-auto pt-4 border-t border-slate-700/50 flex items-end justify-between">
        <div>
           <p className="text-[10px] uppercase tracking-wide text-slate-500 mb-1 font-semibold">{t('scheme_card.key_benefit')}</p>
           <p className="font-bold text-emerald-400 text-sm sm:text-base">{benefitText}</p>
        </div>
        <Link 
          href={`/explore/scheme/${scheme.scheme_id}`}
          className="text-sm font-medium text-white bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg transition-colors border border-slate-600 shadow-sm"
        >
          {t('scheme_card.details')}
        </Link>
      </div>
    </div>
  );
}
