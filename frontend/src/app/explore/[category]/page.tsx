"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import ExploreSchemeCard from '@/components/ExploreSchemeCard';

export default function CategorySchemesPage() {
  const params = useParams();
  const category = params?.category as string;
  
  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!category) return;
    
    async function fetchSchemes() {
      try {
        const res = await fetch(`http://localhost:8000/api/schemes?category=${category}`);
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

  const displayCategory = category ? category.replace('_', ' ').charAt(0).toUpperCase() + category.replace('_', ' ').slice(1) : '';

  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-6 py-24 page-enter">
      
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm font-medium">
        <ol className="list-none p-0 inline-flex items-center text-slate-400">
          <li className="flex items-center">
            <Link href="/explore" className="hover:text-white transition-colors text-orange-400 hover:text-orange-300">Explore</Link>
            <span className="mx-2 text-slate-600">/</span>
          </li>
          <li className="text-slate-200 capitalize">
            {displayCategory} Schemes
          </li>
        </ol>
      </nav>

      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4 capitalize">{displayCategory} Schemes</h1>
        <p className="text-slate-400">Found {schemes.length} active matching schemes.</p>
      </div>

      {loading ? (
        <div className="flex justify-center mt-20">
          <div className="w-10 h-10 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin"></div>
        </div>
      ) : schemes.length === 0 ? (
        <div className="glass p-12 rounded-3xl text-center max-w-xl mx-auto">
           <div className="text-4xl mb-4">🔍</div>
           <h3 className="text-xl font-bold text-white mb-2">No schemes found</h3>
           <p className="text-slate-400">We couldn't find any active schemes in this category at the moment.</p>
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
