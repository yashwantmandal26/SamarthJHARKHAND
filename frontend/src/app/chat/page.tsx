"use client";

import React, { useState, useRef, useEffect } from 'react';
import SchemeCard from '@/components/SchemeCard';
import { useLanguage } from '@/context/LanguageContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  schemes?: any[];
};

export default function ChatPage() {
  const { t, lang } = useLanguage();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Persistent session ID across page reloads
  const [sessionId] = useState(() => {
    if (typeof window === 'undefined') return `session-${Math.random().toString(36).substring(2, 9)}`;
    const stored = localStorage.getItem('samarth_session_id');
    if (stored) return stored;
    const newId = `session-${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('samarth_session_id', newId);
    return newId;
  });
  
  // Profile state from API
  const [profile, setProfile] = useState<any>({});
  
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // Set welcome message based on lang (update when lang changes)
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: t('chat.welcome')
    }]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: userMsg, language: lang })
      });

      const data = await response.json();
      
      if (!response.ok) {
        const errMsg = data.detail || 'Server error. Please try again.';
        setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: `⚠️ ${errMsg}` }]);
        return;
      }
      
      setMessages(prev => [...prev, {
        id: Date.now().toString() + 'r',
        role: 'assistant',
        content: data.response,
        schemes: data.schemes_evaluated
      }]);
      
      setProfile(data.profile_snapshot || {});
      
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: t('chat.error_connect') }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReply = (text: string) => {
    setInput(text);
  };

  const quickReplies = [
    t('chat.quick.housing'),
    t('chat.quick.farmer'),
    t('chat.quick.scholarship'),
    t('chat.quick.pension'),
  ];

  return (
    <div className="flex h-[calc(100vh-80px)] mt-20 max-w-[1600px] mx-auto overflow-hidden w-full page-enter">
      
      {/* 1. Left Sidebar - Profile & Stats (Desktop Only) */}
      <div className="hidden lg:flex flex-col w-[320px] p-6 border-r border-slate-700/50 bg-slate-900/40 backdrop-blur-3xl shrink-0 z-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight text-white mb-2 flex items-center gap-2">
            <span className="text-orange-500">{t('chat.profile_engine')}</span>
          </h1>
          <p className="text-xs text-slate-400">{t('chat.profile_desc')}</p>
        </div>
        
        <div className="glass p-5 rounded-2xl flex-1 border-slate-700/50 overflow-y-auto scrollbar-hide">
          <div className="space-y-4">
             <ProfileField label={t('profile.name')} value={profile?.name} />
             <ProfileField label={t('profile.age')} value={profile?.age ? `${profile.age} Yrs` : null} />
             <ProfileField label={t('profile.income')} value={profile?.income ? `₹${profile.income.toLocaleString()}` : null} highlight="text-emerald-400" />
             <ProfileField label={t('profile.category')} value={profile?.category} highlight="text-orange-400" />
             <ProfileField label={t('profile.gender')} value={profile?.gender} capitalize />
             <ProfileField label={t('profile.occupation')} value={profile?.occupation} capitalize />
             <ProfileField label={t('profile.farmer_type')} value={profile?.farmer_type} capitalize />
             <ProfileField label={t('profile.housing')} value={profile?.housing_status} capitalize />
             <ProfileField label={t('profile.student_class')} value={profile?.student_class} />
             <ProfileField label={t('profile.marital_status')} value={profile?.marital_status} capitalize />
             <ProfileField label={t('profile.ration')} value={profile?.has_bpl_card !== undefined && profile?.has_bpl_card !== null ? (profile.has_bpl_card ? 'BPL' : 'No BPL') : null} />
          </div>
          
          <div className="mt-8 pt-6 border-t border-white/10">
            <h3 className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">{t('chat.confidence')}</h3>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-orange-500 to-amber-400 h-2 rounded-full transition-all duration-1000" 
                style={{ width: `${Math.min(100, Object.keys(profile).filter(k => profile[k] !== null && k !== 'session_id' && k !== 'disabilities').length / 8 * 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 2. Main Chat Engine */}
      <div className="flex-1 flex flex-col h-full relative max-w-4xl mx-auto w-full border-x border-transparent lg:border-slate-800/50 bg-slate-900/20">
        
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-6">
          <div className="text-center mb-8">
             <span className="bg-slate-800 text-slate-400 text-xs px-3 py-1 rounded-full border border-slate-700/50">{t('chat.today')}</span>
          </div>

          {messages.map((m) => (
            <div key={m.id} className={`flex flex-col w-full ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              
              <div className={`
                max-w-[85%] md:max-w-[80%] p-4 md:p-5 rounded-2xl shadow-lg leading-relaxed text-[15px]
                ${m.role === 'user' 
                  ? 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white rounded-br-sm' 
                  : 'glass-card border-white/10 rounded-bl-sm text-slate-200'}
              `}>
                <p className="whitespace-pre-wrap">{m.content}</p>
              </div>
              
              {/* Attachments - Evaluated Schemes */}
              {m.schemes && m.schemes.length > 0 && (
                <div className="mt-3 w-full grid grid-cols-1 gap-3 max-w-[85%] mr-auto pl-2 md:pl-4">
                  {m.schemes.map((s, i) => (
                    <SchemeCard 
                      key={i} 
                      schemeId={s.scheme_id} 
                      schemeName={s.scheme_name}
                      status={s.status} 
                      failedReasons={s.failed_reasons}
                      missingData={s.missing_data}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {loading && (
             <div className="flex glass-card w-fit p-4 rounded-2xl rounded-bl-sm items-center gap-1.5 shadow-lg">
                <div className="w-2 h-2 rounded-full bg-orange-400 typing-dot"></div>
                <div className="w-2 h-2 rounded-full bg-amber-400 typing-dot"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-400 typing-dot"></div>
             </div>
          )}
          <div ref={endOfMessagesRef} className="h-4"></div>
        </div>
        
        {/* Input Block */}
        <div className="p-4 bg-slate-900/80 backdrop-blur-lg border-t border-slate-800 z-20 shrink-0">
          
          {/* Quick Replies (only show when few messages) */}
          {messages.length < 3 && !loading && (
            <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-3 max-w-4xl mx-auto">
              {quickReplies.map((qr, idx) => (
                <button 
                  key={idx}
                  onClick={() => handleQuickReply(qr)}
                  className="whitespace-nowrap text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-full border border-slate-700 transition-colors"
                >
                  {qr}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSend} className="relative group max-w-4xl mx-auto flex gap-2">
             <div className="flex-1 p-1 rounded-2xl bg-gradient-to-r from-slate-700/50 via-slate-600/30 to-slate-700/50 border border-slate-700/50 focus-within:border-orange-500/50 transition-all duration-300 shadow-xl overflow-hidden backdrop-blur-xl">
               <input
                 className="w-full bg-slate-800/80 text-white placeholder-slate-400 p-4 pl-5 outline-none rounded-xl text-[15px]"
                 placeholder={t('chat.placeholder')}
                 value={input}
                 onChange={e => setInput(e.target.value)}
                 disabled={loading}
                 autoFocus
               />
             </div>
             
             <button 
               type="submit"
               disabled={loading || !input.trim()}
               className={`
                  flex-shrink-0 w-14 h-[60px] rounded-2xl flex items-center justify-center mt-[4px]
                  ${loading || !input.trim() ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-lg hover:shadow-orange-500/25 cursor-pointer hover:scale-105'}
                  transition-all duration-200
               `}
             >
               <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 -rotate-45 ml-1 mb-1">
                  <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
               </svg>
             </button>
          </form>
          <div className="text-center mt-2">
             <span className="text-[10px] text-slate-500">{t('chat.disclaimer')}</span>
          </div>
        </div>
        
      </div>
    </div>
  );
}

// Small helper component for sidebar
function ProfileField({ label, value, highlight = "text-white", capitalize = false }: { label: string, value: any, highlight?: string, capitalize?: boolean }) {
  if (value === undefined) return null;
  
  const displayValue = value === null || value === '' ? '--' : value;
  const isSet = displayValue !== '--';
  
  return (
    <div className="flex justify-between items-center pb-2 border-b border-white/5">
       <span className="text-slate-400 text-sm">{label}</span>
       <span className={`font-semibold ${isSet ? highlight : 'text-slate-600'} ${capitalize && isSet ? 'capitalize' : ''} text-right max-w-[150px] truncate`}>
         {displayValue}
       </span>
    </div>
  );
}
