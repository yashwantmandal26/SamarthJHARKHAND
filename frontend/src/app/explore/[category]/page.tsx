"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import ExploreSchemeCard from '@/components/ExploreSchemeCard';
import { useLanguage } from '@/context/LanguageContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function CategorySchemesPage() {
  const params = useParams();
  const category = params?.category as string;
  const { t } = useLanguage();
  
  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!category) return;
    
    async function fetchSchemes() {
      try {
        const res = await fetch(`${API_URL}/api/schemes?category=${category}`);
        if (res.ok) {
          const data = await res.json();
          setSchemes(data);
        }
      } catch (err) {
        console.error("Failed to fetch schemes", err);
      } finally {
        setLoading(false);
      }
    }
    fetchSchemes();
  }, [category]);

  // Translate category name
  const catKey = `cat.${category}`;
  const displayCategory = t(catKey) !== catKey 
    ? t(catKey) 
    : (category 
        ? category.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
        : '');

  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-6 py-24 page-enter">
      
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm font-medium">
        <ol className="list-none p-0 inline-flex items-center text-slate-400">
          <li className="flex items-center">
            <Link href="/explore" className="hover:text-white transition-colors text-orange-400 hover:text-orange-300">{t('explore.title')}</Link>
            <span className="mx-2 text-slate-600">/</span>
          </li>
          <li className="text-slate-200 capitalize">
            {displayCategory} {t('explore.title2')}
          </li>
        </ol>
      </nav>

      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4 capitalize">{displayCategory} {t('explore.title2')}</h1>
        <p className="text-slate-400">{schemes.length} {t('explore.found_count')}</p>
      </div>

      {loading ? (
        <div className="flex justify-center mt-20">
          <div className="w-10 h-10 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin"></div>
        </div>
      ) : schemes.length === 0 ? (
        <div className="glass p-12 rounded-3xl text-center max-w-xl mx-auto">
           <div className="text-4xl mb-4">🔍</div>
           <h3 className="text-xl font-bold text-white mb-2">{t('explore.no_schemes')}</h3>
           <p className="text-slate-400">{t('explore.no_schemes_desc')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.map((scheme, idx) => (
            <div key={scheme.scheme_id} className={`stagger-${(idx % 5) + 1} opacity-0 page-enter`} style={{ animationFillMode: 'forwards' }}>
              <ExploreSchemeCard scheme={scheme} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
