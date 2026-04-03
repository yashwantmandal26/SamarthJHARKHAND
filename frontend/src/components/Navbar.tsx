"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useLanguage, Language } from '@/context/LanguageContext';

export default function Navbar() {
  const pathname = usePathname();
  const { lang, setLang, t, langLabel } = useLanguage();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const langRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close language dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(e.target as Node)) {
        setLangMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navLinks: { name: string; path: string; highlight?: boolean; highlightAlt?: boolean }[] = [
    { name: t('nav.home'), path: '/' },
    { name: t('nav.explore'), path: '/explore' },
    { name: t('nav.chat'), path: '/chat', highlight: true },
    { name: t('nav.ai'), path: '/ai', highlightAlt: true },
  ];

  const languages: { key: Language; label: string; flag: string }[] = [
    { key: 'en', label: 'English', flag: 'EN' },
    { key: 'hi', label: 'हिंदी', flag: 'हि' },
    { key: 'hinglish', label: 'Hinglish', flag: 'HG' },
  ];

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled
        ? 'bg-slate-900/80 backdrop-blur-xl border-b border-slate-800/80 shadow-lg shadow-black/20'
        : 'bg-transparent border-b border-transparent'
        }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20 md:h-28">

          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Link href="/" className="flex items-center group">
              <Image
                src="/smarth.png"
                alt="Samarth Logo"
                width={100}
                height={30}
                className="w-12 md:w-16 h-auto max-h-10 object-contain transition-transform group-hover:scale-105"
                priority
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-4">
            {navLinks.map((link) => {
              const isActive = pathname === link.path || (link.path !== '/' && pathname?.startsWith(link.path));

              if (link.highlight) {
                return (
                  <Link
                    key={link.path}
                    href={link.path}
                    className="ml-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-orange-500 to-amber-500 text-white font-medium text-sm hover:shadow-[0_0_20px_rgba(245,158,11,0.4)] hover:scale-105 transition-all duration-300"
                  >
                    {link.name}
                  </Link>
                );
              }

              if (link.highlightAlt) {
                return (
                  <Link
                    key={link.path}
                    href={link.path}
                    className="ml-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-medium text-sm hover:shadow-[0_0_20px_rgba(20,184,166,0.4)] hover:scale-105 transition-all duration-300"
                  >
                    {link.name}
                  </Link>
                );
              }

              return (
                <Link
                  key={link.path}
                  href={link.path}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                    }`}
                >
                  {link.name}
                </Link>
              );
            })}

            {/* Language Switcher — Desktop */}
            <div className="relative ml-3" ref={langRef}>
              <button
                onClick={() => setLangMenuOpen(!langMenuOpen)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/50 transition-all duration-200 border border-slate-700/50"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.148 15.25 3 15.25m6-10c2.98 5.304 7.664 8.677 12.6 9.093" />
                </svg>
                <span className="font-bold">{langLabel}</span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`w-3 h-3 transition-transform ${langMenuOpen ? 'rotate-180' : ''}`}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </button>

              {langMenuOpen && (
                <div className="absolute right-0 mt-2 w-44 rounded-xl glass border border-slate-700/50 shadow-2xl overflow-hidden z-50 animate-fade-in">
                  {languages.map((l) => (
                    <button
                      key={l.key}
                      onClick={() => { setLang(l.key); setLangMenuOpen(false); }}
                      className={`w-full px-4 py-3 text-left text-sm font-medium flex items-center gap-3 transition-colors ${
                        lang === l.key
                          ? 'bg-orange-500/20 text-orange-400'
                          : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                      }`}
                    >
                      <span className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold">
                        {l.flag}
                      </span>
                      {l.label}
                      {lang === l.key && (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 ml-auto text-orange-400">
                          <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </nav>

          {/* Mobile — Language + Menu */}
          <div className="flex md:hidden items-center gap-2">
            {/* Mobile Language Toggle */}
            <button
              onClick={() => {
                const order: Language[] = ['en', 'hi', 'hinglish'];
                const nextIdx = (order.indexOf(lang) + 1) % order.length;
                setLang(order[nextIdx]);
              }}
              className="text-slate-300 hover:text-white p-2 border border-slate-700/50 rounded-lg text-xs font-bold"
            >
              {langLabel}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-slate-300 hover:text-white p-2"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden glass border-t border-slate-700/50 absolute w-full pb-4 shadow-xl">
          <div className="px-4 pt-2 pb-3 space-y-1 sm:px-3 flex flex-col">
            {navLinks.map((link) => {
              const isActive = pathname === link.path || (link.path !== '/' && pathname?.startsWith(link.path));

              return (
                <Link
                  key={link.path}
                  href={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-3 rounded-md text-base font-medium ${link.highlight
                    ? 'mt-2 bg-gradient-to-r from-orange-500 to-amber-500 text-white text-center shadow-lg'
                    : link.highlightAlt
                      ? 'mt-2 bg-gradient-to-r from-teal-500 to-cyan-500 text-white text-center shadow-lg'
                      : isActive
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`}
                >
                  {link.name}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
}
