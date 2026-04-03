"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import CategoryCard from '@/components/CategoryCard';
import { useLanguage } from '@/context/LanguageContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type CategoryInfo = {
  id: string;
  name: string;
  count: number;
};

export default function ExplorePage() {
  const { t } = useLanguage();
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCategories() {
      try {
        const res = await fetch(`${API_URL}/api/categories`);
        if (res.ok) {
          const data = await res.json();
          setCategories(data);
        }
      } catch (err) {
        console.error("Failed to fetch categories", err);
      } finally {
        setLoading(false);
      }
    }
    fetchCategories();
  }, []);

  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-6 py-24 page-enter">
      {/* Back to Home */}
      <div className="flex items-center gap-4 mb-10">
        <Link 
          href="/" 
          className="flex items-center justify-center w-10 h-10 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all duration-200 shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <span className="text-sm font-medium text-slate-400">{t('nav.home')}</span>
      </div>
      
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">{t('explore.title')} <span className="text-orange-400">{t('explore.title2')}</span></h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          {t('explore.desc')}
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="w-12 h-12 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {categories.map((cat, idx) => (
            <div key={cat.id} className={`stagger-${(idx % 5) + 1} opacity-0 page-enter`} style={{ animationFillMode: 'forwards' }}>
              <CategoryCard id={cat.id} name={cat.name} count={cat.count} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
