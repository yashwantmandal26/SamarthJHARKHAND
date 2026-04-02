"use client";

import React from 'react';
import Link from 'next/link';
import { useLanguage } from '@/context/LanguageContext';

type CategoryCardProps = {
  id: string;
  name: string;
  count: number;
};

// Map categories to emoji icons
const iconMap: Record<string, string> = {
  agriculture: '🌾',
  housing: '🏠',
  education: '📚',
  women: '👩',
  social_security: '🛡️',
  employment: '💼',
};

const colorMap: Record<string, string> = {
  agriculture: 'from-green-500/20 to-emerald-500/5 hover:border-green-500/50',
  housing: 'from-blue-500/20 to-cyan-500/5 hover:border-blue-500/50',
  education: 'from-amber-500/20 to-orange-500/5 hover:border-amber-500/50',
  women: 'from-pink-500/20 to-rose-500/5 hover:border-pink-500/50',
  social_security: 'from-purple-500/20 to-fuchsia-500/5 hover:border-purple-500/50',
  employment: 'from-indigo-500/20 to-violet-500/5 hover:border-indigo-500/50',
};

export default function CategoryCard({ id, name, count }: CategoryCardProps) {
  const { t } = useLanguage();
  const icon = iconMap[id] || '📄';
  const colorClass = colorMap[id] || 'from-slate-500/20 to-slate-500/5 hover:border-slate-500/50';

  // Translate category name
  const translatedName = t(`cat.${id}`) !== `cat.${id}` ? t(`cat.${id}`) : name;

  return (
    <Link href={`/explore/${id}`}>
      <div className={`
        glass p-6 rounded-2xl h-full flex flex-col justify-between
        transition-all duration-300 transform hover:-translate-y-2
        bg-gradient-to-br ${colorClass} border-transparent
      `}>
        <div className="flex justify-between items-start mb-6">
          <div className="w-14 h-14 rounded-xl bg-slate-900/50 flex items-center justify-center text-3xl shadow-inner shadow-black/50 border border-white/5">
            {icon}
          </div>
          <span className="bg-slate-900/80 px-3 py-1 rounded-full text-xs font-semibold text-slate-300 border border-slate-700">
            {count} {t('explore.schemes_count')}
          </span>
        </div>
        
        <div>
          <h3 className="text-xl font-bold text-white mb-2">{translatedName}</h3>
          <p className="text-sm text-slate-400 flex items-center gap-1 group-hover:text-slate-300 transition-colors">
            {t('explore.explore_link')}
          </p>
        </div>
      </div>
    </Link>
  );
}
