"use client";

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useLanguage } from '@/context/LanguageContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Source = {
  scheme_id: string;
  scheme_name: string;
  scheme_name_hindi: string;
  category: string;
  relevance_score: number;
};

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
};

export default function AIAssistantPage() {
  const { t, lang } = useLanguage();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const [sessionId] = useState(() => {
    if (typeof window === 'undefined') return `ai-session-${Math.random().toString(36).substring(2, 9)}`;
    const stored = localStorage.getItem('samarth_ai_session_id');
    if (stored) return stored;
    const newId = `ai-session-${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('samarth_ai_session_id', newId);
    return newId;
  });

  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

  // Auto-focus on keypress
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') return;
      if ((e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v')) {
        inputRef.current?.focus();
      }
    };
    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  // Welcome message
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: t('ai.welcome')
    }]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    if (!shouldAutoScroll) return;
    endOfMessagesRef.current?.scrollIntoView({ behavior: loading ? 'auto' : 'smooth' });
  }, [messages, loading, shouldAutoScroll]);

  const handleMessagesScroll = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    setShouldAutoScroll(distanceFromBottom < 120);
  }, []);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setShouldAutoScroll(true);
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setLoading(true);

    // Create new AbortController for this request
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch(`${API_URL}/api/ai-chat-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: userMsg }),
        signal: controller.signal,
      });

      if (!response.ok) {
        let errMsg = 'Server error. Please try again.';
        try {
          const data = await response.json();
          errMsg = data.detail || errMsg;
        } catch { /* ignore */ }
        setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: `⚠️ ${errMsg}` }]);
        return;
      }

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      const messageId = Date.now().toString() + 'r';
      
      setMessages(prev => [...prev, {
        id: messageId,
        role: 'assistant',
        content: '',
        sources: []
      }]);

      let fullContent = '';
      let done = false;
      let buffer = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n');
          buffer = parts.pop() || ''; // Keep the last incomplete part in the buffer
          
          for (const line of parts) {
            if (!line.trim()) continue;
            try {
              const data = JSON.parse(line);
              if (data.type === 'sources') {
                setMessages(prev => prev.map(m => m.id === messageId ? { ...m, sources: data.sources } : m));
              } else if (data.type === 'chunk') {
                fullContent += data.text;
                setMessages(prev => prev.map(m => m.id === messageId ? { ...m, content: fullContent } : m));
              }
            } catch (e) {
              console.error('Stream parse error:', line, e);
            }
          }
        }
      }

    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        setMessages(prev => [...prev, { id: `stop-${Date.now()}`, role: 'assistant', content: '⏹️ Response stopped by you.' }]);
      } else {
        console.error(error);
        setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: t('chat.error_connect') }]);
      }
    } finally {
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  const handleStop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const handleNewChat = async () => {
    try {
      await fetch(`${API_URL}/api/session/${sessionId}`, { method: 'DELETE' });
    } catch { /* ignore */ }
    const newId = `ai-session-${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('samarth_ai_session_id', newId);
    window.location.reload();
  };

  const suggestedQueries = [
    t('ai.suggest.compare'),
    t('ai.suggest.housing'),
    t('ai.suggest.apply'),
    t('ai.suggest.documents'),
  ];

  const categoryColors: Record<string, string> = {
    agriculture: 'bg-green-500/20 text-green-400 border-green-500/30',
    housing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    education: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    women: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    employment: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    social_security: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
  };

  return (
    <div className="flex h-[calc(100vh-80px)] mt-20 max-w-[1600px] mx-auto overflow-hidden w-full page-enter">

      {/* Left Panel — Info + Sources (Desktop) */}
      <div className="hidden lg:flex flex-col w-[320px] p-6 border-r border-slate-700/50 bg-slate-900/40 backdrop-blur-3xl shrink-0 z-10">
        <div className="mb-4">
          <h1 className="text-2xl font-bold tracking-tight mb-2 flex items-center gap-2">
            <span className="text-gradient-teal">{t('ai.title')}</span>
          </h1>
          <p className="text-xs text-slate-400">{t('ai.subtitle')}</p>
        </div>

        <button
          onClick={handleNewChat}
          className="mb-4 w-full px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/50 text-slate-300 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer hover:border-teal-500/30"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
          New Chat
        </button>

        {/* Capabilities */}
        <div className="glass p-5 rounded-2xl flex-1 border-slate-700/50 overflow-y-auto scrollbar-hide">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">{t('ai.capabilities')}</h3>
          <div className="space-y-3">
            {[
              { icon: '🔍', text: t('ai.cap.search') },
              { icon: '📊', text: t('ai.cap.compare') },
              { icon: '📋', text: t('ai.cap.apply') },
              { icon: '📄', text: t('ai.cap.documents') },
              { icon: '💡', text: t('ai.cap.suggest') },
              { icon: '🗣️', text: t('ai.cap.multilingual') },
            ].map((cap, i) => (
              <div key={i} className="flex items-start gap-3 text-sm">
                <span className="text-lg mt-0.5 shrink-0">{cap.icon}</span>
                <span className="text-slate-300 leading-snug">{cap.text}</span>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-white/5">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{t('ai.powered_by')}</h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></div>
              <span className="text-xs text-teal-400 font-medium">RAG + BM25 Retrieval</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">{t('ai.rag_desc')}</p>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative max-w-4xl mx-auto w-full border-x border-transparent lg:border-slate-800/50 bg-slate-900/20">

        {/* Messages */}
        <div
          ref={messagesContainerRef}
          onScroll={handleMessagesScroll}
          className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-6"
        >
          <div className="text-center mb-8">
            <span className="bg-teal-900/30 text-teal-400 text-xs px-3 py-1 rounded-full border border-teal-500/20">
              ✨ {t('ai.badge')}
            </span>
          </div>

          {messages.map((m) => (
            <div key={m.id} className={`flex flex-col w-full group/msg ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`
                relative max-w-[85%] md:max-w-[80%] p-4 md:p-5 rounded-2xl shadow-lg leading-relaxed text-[15px]
                ${m.role === 'user'
                  ? 'bg-gradient-to-br from-teal-500 to-cyan-600 text-white rounded-br-sm'
                  : 'glass-card border-white/10 rounded-bl-sm text-slate-200'}
              `}>
                <div className="prose prose-invert prose-sm max-w-none 
                  [&_strong]:text-teal-300 [&_strong]:font-semibold
                  [&_h2]:text-teal-100 [&_h2]:font-bold [&_h2]:text-lg [&_h2]:mt-4 [&_h2]:mb-2
                  [&_h3]:text-teal-200 [&_h3]:font-bold [&_h3]:text-base [&_h3]:mt-3 [&_h3]:mb-1
                  [&_h4]:text-teal-300 [&_h4]:font-semibold [&_h4]:text-sm [&_h4]:mt-3 [&_h4]:mb-1
                  [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1 [&_ul]:my-2
                  [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1.5 [&_ol]:my-2
                  [&_li]:text-slate-200 [&_li]:leading-relaxed
                  [&_a]:text-teal-400 [&_a]:underline [&_a]:hover:text-teal-300
                  [&_code]:bg-slate-700/60 [&_code]:text-teal-300 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-xs
                  [&_hr]:border-slate-700/50 [&_hr]:my-3
                  [&_p]:my-1 [&_p]:leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: formatMarkdown(m.content) }}
                />

                {/* Copy Button */}
                <button
                  onClick={() => handleCopy(m.id, m.content)}
                  className={`absolute ${m.role === 'user' ? '-left-8 bottom-1' : '-right-8 bottom-1'} 
                    p-1.5 rounded-lg border border-slate-700/50 bg-slate-800/80 text-slate-400 
                    opacity-0 group-hover/msg:opacity-100 transition-opacity hover:bg-slate-700 hover:text-teal-400
                  `}
                  title="Copy text"
                >
                  {copiedId === m.id ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5 text-teal-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  )}
                </button>
              </div>

              {/* Sources */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2 max-w-[85%] mr-auto pl-2">
                  <span className="text-[10px] text-slate-500 w-full mb-0.5">📚 Sources:</span>
                  {m.sources.map((s, i) => (
                    <span
                      key={i}
                      className={`text-[11px] px-2.5 py-1 rounded-full border ${categoryColors[s.category] || 'bg-slate-800 text-slate-400 border-slate-700'}`}
                    >
                      {s.scheme_name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="glass-card w-fit p-4 rounded-2xl rounded-bl-sm flex items-center gap-1.5 shadow-lg">
                <div className="w-2 h-2 rounded-full bg-teal-400 typing-dot"></div>
                <div className="w-2 h-2 rounded-full bg-cyan-400 typing-dot"></div>
                <div className="w-2 h-2 rounded-full bg-emerald-400 typing-dot"></div>
              </div>
              <span className="text-xs text-slate-500">Searching schemes & generating...</span>
            </div>
          )}
          <div ref={endOfMessagesRef} className="h-4"></div>
        </div>

        {/* Input Block */}
        <div className="p-4 bg-slate-900/80 backdrop-blur-lg border-t border-slate-800 z-20 shrink-0">

          {/* Suggested Queries (first few messages) */}
          {messages.length < 3 && !loading && (
            <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-3 max-w-4xl mx-auto">
              {suggestedQueries.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(sq)}
                  className="whitespace-nowrap text-xs bg-teal-950/40 hover:bg-teal-900/50 text-teal-300 px-4 py-2 rounded-full border border-teal-600/30 transition-colors"
                >
                  {sq}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSend} className="relative group max-w-4xl mx-auto flex gap-2">
            <div className="flex-1 p-1 rounded-2xl bg-gradient-to-r from-slate-700/50 via-slate-600/30 to-slate-700/50 border border-slate-700/50 focus-within:border-teal-500/50 transition-all duration-300 shadow-xl overflow-hidden backdrop-blur-xl">
              <input
                ref={inputRef}
                className="w-full bg-slate-800/80 text-white placeholder-slate-400 p-4 pl-5 outline-none rounded-xl text-[15px]"
                placeholder={loading ? t('ai.placeholder_typing') : t('ai.placeholder')}
                value={input}
                onChange={e => setInput(e.target.value)}
                autoFocus
              />
            </div>

            {/* Stop button — visible only during loading */}
            {loading && (
              <button
                type="button"
                onClick={handleStop}
                className="flex-shrink-0 w-14 h-[60px] rounded-2xl flex items-center justify-center mt-[4px] bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-lg hover:shadow-red-500/30 cursor-pointer hover:scale-105 transition-all duration-200 animate-pulse"
                title="Stop generating"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              </button>
            )}

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className={`
                flex-shrink-0 w-14 h-[60px] rounded-2xl flex items-center justify-center mt-[4px]
                ${loading || !input.trim() ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg hover:shadow-teal-500/25 cursor-pointer hover:scale-105'}
                transition-all duration-200
              `}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 -rotate-45 ml-1 mb-1">
                <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
              </svg>
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-500">{t('ai.disclaimer')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Rich markdown-to-HTML formatter for streaming AI responses
function formatMarkdown(text: string): string {
  if (!text) return '';
  
  const lines = text.split('\n');
  const htmlLines: string[] = [];
  let inUl = false;
  let inOl = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Headings: ###, ##, #
    if (/^###\s+(.+)$/.test(line)) {
      closeLists();
      htmlLines.push(`<h4 class="text-teal-300 font-semibold text-sm mt-4 mb-1">${applyInline(line.replace(/^###\s+/, ''))}</h4>`);
      continue;
    }
    if (/^##\s+(.+)$/.test(line)) {
      closeLists();
      htmlLines.push(`<h3 class="text-teal-200 font-bold text-base mt-4 mb-1">${applyInline(line.replace(/^##\s+/, ''))}</h3>`);
      continue;
    }
    if (/^#\s+(.+)$/.test(line)) {
      closeLists();
      htmlLines.push(`<h2 class="text-teal-100 font-bold text-lg mt-4 mb-2">${applyInline(line.replace(/^#\s+/, ''))}</h2>`);
      continue;
    }

    // Horizontal rule
    if (/^[-*_]{3,}\s*$/.test(line)) {
      closeLists();
      htmlLines.push('<hr class="border-slate-700/50 my-3"/>');
      continue;
    }

    // Numbered list: 1. item, 2. item, etc.
    const olMatch = line.match(/^(\d+)\.\s+(.+)$/);
    if (olMatch) {
      if (inUl) { htmlLines.push('</ul>'); inUl = false; }
      if (!inOl) { htmlLines.push('<ol class="list-decimal pl-5 space-y-1.5 my-2">'); inOl = true; }
      htmlLines.push(`<li class="text-slate-200">${applyInline(olMatch[2])}</li>`);
      continue;
    }

    // Bullet list: - item or • item or * item (with optional indentation for nesting)
    const ulMatch = line.match(/^(\s*)[-•*]\s+(.+)$/);
    if (ulMatch) {
      if (inOl) { htmlLines.push('</ol>'); inOl = false; }
      if (!inUl) { htmlLines.push('<ul class="list-disc pl-5 space-y-1 my-2">'); inUl = true; }
      const indent = ulMatch[1].length >= 2 ? ' class="ml-4 text-slate-300"' : ' class="text-slate-200"';
      htmlLines.push(`<li${indent}>${applyInline(ulMatch[2])}</li>`);
      continue;
    }

    // Regular line — close any open lists first
    closeLists();

    // Empty line = paragraph break
    if (line.trim() === '') {
      htmlLines.push('<div class="h-2"></div>');
      continue;
    }

    // Regular paragraph
    htmlLines.push(`<p class="my-1">${applyInline(line)}</p>`);
  }

  closeLists();
  return htmlLines.join('\n');

  function closeLists() {
    if (inUl) { htmlLines.push('</ul>'); inUl = false; }
    if (inOl) { htmlLines.push('</ol>'); inOl = false; }
  }

  function escapeHtml(input: string): string {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function sanitizeSchemeId(input: string): string {
    return input.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '');
  }

  function sanitizeExternalUrl(input: string): string {
    const trimmed = input.trim();
    if (/^https?:\/\//i.test(trimmed)) {
      return trimmed.replace(/"/g, '%22');
    }
    return '#';
  }

  function applyInline(str: string): string {
    const safe = escapeHtml(str);
    return safe
      // Scheme card links: [[Scheme Name →]](link_id)
      .replace(/\[\[(.+?)\]\]\(([^)]+)\)/g, (_, label: string, linkId: string) => {
        const safeId = sanitizeSchemeId(linkId);
        if (!safeId) {
          return label;
        }
        return `<a href="/explore/scheme/${safeId}?from=ai" class="inline-flex items-center gap-1.5 text-teal-300 font-semibold hover:text-teal-200 transition-colors no-underline group/link"><span class="underline underline-offset-2 decoration-teal-500/40 group-hover/link:decoration-teal-400">${label}</span><svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 inline-block -mt-0.5 text-teal-400 group-hover/link:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg></a>`;
      })
      // Bold
      .replace(/\*\*(.+?)\*\*/g, '<strong class="text-teal-300 font-semibold">$1</strong>')
      // Italic
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Inline code
      .replace(/`([^`]+)`/g, '<code class="bg-slate-700/60 text-teal-300 px-1.5 py-0.5 rounded text-xs font-mono">$1</code>')
      // Regular links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label: string, url: string) => {
        const safeUrl = sanitizeExternalUrl(url);
        return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" class="text-teal-400 underline hover:text-teal-300">${label}</a>`;
      })
      // Arrow →
      .replace(/→/g, '<span class="text-teal-400">→</span>');
  }
}
