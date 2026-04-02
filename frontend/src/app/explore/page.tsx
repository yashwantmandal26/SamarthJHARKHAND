"use client";

import React, { useEffect, useState } from 'react';
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
