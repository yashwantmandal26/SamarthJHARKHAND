"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Language = 'en' | 'hi' | 'hinglish';

type LanguageContextType = {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string) => string;
  langLabel: string;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// ─── TRANSLATIONS ───────────────────────────────────────────
const translations: Record<string, Record<Language, string>> = {

  // ─── NAVBAR ─────────────────────────────────────────────
  "nav.home": {
    en: "Home",
    hi: "होम",
    hinglish: "Home",
  },
  "nav.explore": {
    en: "Explore Schemes",
    hi: "योजनाएँ देखें",
    hinglish: "Schemes Dekho",
  },
  "nav.chat": {
    en: "AI Assistant",
    hi: "AI सहायक",
    hinglish: "AI Assistant",
  },

  // ─── HOME PAGE — HERO ──────────────────────────────────
  "home.badge": {
    en: "Beta Version 1.0 Live",
    hi: "बीटा संस्करण 1.0 लाइव",
    hinglish: "Beta Version 1.0 Live",
  },
  "home.hero.line1": {
    en: "Find the right schemes.",
    hi: "सही योजनाएँ खोजें।",
    hinglish: "Sahi schemes khojein.",
  },
  "home.hero.line2": {
    en: "For You, For Jharkhand.",
    hi: "आपके लिए, झारखंड के लिए।",
    hinglish: "Aapke liye, Jharkhand ke liye.",
  },
  "home.hero.desc": {
    en: "Samarth is an AI-powered assistant designed to help citizens of Jharkhand discover, understand, and apply for government schemes effortlessly.",
    hi: "समर्थ एक AI-संचालित सहायक है जो झारखंड के नागरिकों को सरकारी योजनाओं को समझने और आवेदन करने में मदद करता है।",
    hinglish: "Samarth ek AI assistant hai jo Jharkhand ke logon ko sarkari yojanaon ko samajhne aur apply karne mein help karta hai.",
  },
  "home.cta.assistant": {
    en: "Start AI Assistant",
    hi: "AI सहायक शुरू करें",
    hinglish: "AI Assistant Start Karo",
  },
  "home.cta.explore": {
    en: "Explore Schemes Manually",
    hi: "योजनाएँ मैन्युअली देखें",
    hinglish: "Schemes Manually Dekho",
  },

  // ─── HOME PAGE — STATS ─────────────────────────────────
  "home.stats.schemes": {
    en: "Active Schemes",
    hi: "सक्रिय योजनाएँ",
    hinglish: "Active Schemes",
  },
  "home.stats.categories": {
    en: "Key Categories",
    hi: "मुख्य श्रेणियाँ",
    hinglish: "Key Categories",
  },
  "home.stats.accuracy": {
    en: "Deterministic Accuracy",
    hi: "निश्चयात्मक सटीकता",
    hinglish: "Deterministic Accuracy",
  },

  // ─── HOME PAGE — HOW IT WORKS ──────────────────────────
  "home.how.title": {
    en: "How Samarth Works",
    hi: "समर्थ कैसे काम करता है",
    hinglish: "Samarth kaise kaam karta hai",
  },
  "home.how.subtitle": {
    en: "Discover your eligibility in three simple steps",
    hi: "तीन आसान चरणों में अपनी पात्रता जानें",
    hinglish: "Teen simple steps mein apni eligibility jaano",
  },
  "home.how.step1.title": {
    en: "1. Tell us about you",
    hi: "1. अपने बारे में बताएं",
    hinglish: "1. Apne baare mein batao",
  },
  "home.how.step1.desc": {
    en: "Chat with Samarth in your preferred language. Share basic details like your occupation, age, or income.",
    hi: "अपनी पसंदीदा भाषा में समर्थ से बात करें। अपना व्यवसाय, उम्र, या आय जैसी जानकारी साझा करें।",
    hinglish: "Apni favourite language mein Samarth se baat karo. Apna occupation, age, ya income share karo.",
  },
  "home.how.step2.title": {
    en: "2. AI Matches Schemes",
    hi: "2. AI योजनाएँ मिलाता है",
    hinglish: "2. AI Schemes Match Karta Hai",
  },
  "home.how.step2.desc": {
    en: "Our deterministic engine scans all active government schemes to find the ones you explicitly qualify for.",
    hi: "हमारा इंजन सभी सक्रिय सरकारी योजनाओं की जांच करके वे योजनाएँ ढूंढता है जिनके लिए आप पात्र हैं।",
    hinglish: "Hamara engine saari active sarkari schemes check karke aapke liye eligible wali dhundhta hai.",
  },
  "home.how.step3.title": {
    en: "3. Apply with Confidence",
    hi: "3. विश्वास से आवेदन करें",
    hinglish: "3. Confidence se Apply Karo",
  },
  "home.how.step3.desc": {
    en: "Get step-by-step guidance, required document lists, and direct links to official application portals.",
    hi: "चरण-दर-चरण मार्गदर्शन, आवश्यक दस्तावेज़ सूची, और आधिकारिक पोर्टल के लिंक प्राप्त करें।",
    hinglish: "Step-by-step guidance, zaruri documents ki list, aur official portal ke links paao.",
  },
  "home.how.tryit": {
    en: "Try it out →",
    hi: "इसे आज़माएं →",
    hinglish: "Try karo →",
  },

  // ─── HOME PAGE — ABOUT / PROJECT DESCRIPTION ───────────
  "home.about.title": {
    en: "About Samarth",
    hi: "समर्थ के बारे में",
    hinglish: "Samarth ke baare mein",
  },
  "home.about.subtitle": {
    en: "Bridging the gap between citizens and government schemes",
    hi: "नागरिकों और सरकारी योजनाओं के बीच की खाई को पाटना",
    hinglish: "Citizens aur sarkari schemes ke beech ka gap fill karna",
  },
  "home.about.p1": {
    en: "Samarth is a research-driven Dissertation Project that harnesses the power of Artificial Intelligence combined with a rule-based deterministic engine to help citizens of Jharkhand navigate the complex landscape of government welfare schemes.",
    hi: "समर्थ एक शोध-आधारित शोध प्रबंध परियोजना है जो कृत्रिम बुद्धिमत्ता और नियम-आधारित इंजन की शक्ति का उपयोग करके झारखंड के नागरिकों को सरकारी कल्याण योजनाओं की जटिलताओं को समझने में मदद करता है।",
    hinglish: "Samarth ek research-driven Dissertation Project hai jo AI aur rule-based deterministic engine ki power use karke Jharkhand ke logon ko sarkari welfare schemes samajhne mein help karta hai.",
  },
  "home.about.p2": {
    en: "Unlike traditional chatbots, Samarth uses a Hybrid AI Architecture — the AI handles natural language understanding while core eligibility decisions are made by a deterministic code-based engine, ensuring 100% accuracy in scheme matching. No hallucinations, no guesswork.",
    hi: "पारंपरिक चैटबॉट्स के विपरीत, समर्थ एक हाइब्रिड AI आर्किटेक्चर का उपयोग करता है — AI प्राकृतिक भाषा को समझता है जबकि पात्रता के निर्णय एक कोड-आधारित इंजन द्वारा लिए जाते हैं, जो 100% सटीकता सुनिश्चित करता है।",
    hinglish: "Traditional chatbots se alag, Samarth ek Hybrid AI Architecture use karta hai — AI natural language samajhta hai jabki eligibility decisions ek code-based engine leta hai, jo 100% accuracy ensure karta hai. No hallucinations, no guesswork.",
  },
  "home.about.feature1.title": {
    en: "Hybrid AI Architecture",
    hi: "हाइब्रिड AI आर्किटेक्चर",
    hinglish: "Hybrid AI Architecture",
  },
  "home.about.feature1.desc": {
    en: "LLM for conversation, deterministic engine for eligibility — best of both worlds.",
    hi: "बातचीत के लिए LLM, पात्रता के लिए नियतात्मक इंजन — दोनों का सर्वश्रेष्ठ।",
    hinglish: "LLM conversation ke liye, deterministic engine eligibility ke liye — dono ka best.",
  },
  "home.about.feature2.title": {
    en: "Multilingual Support",
    hi: "बहुभाषी समर्थन",
    hinglish: "Multilingual Support",
  },
  "home.about.feature2.desc": {
    en: "Interact in English, Hindi, or Hinglish — the AI adapts to how Jharkhand speaks.",
    hi: "अंग्रेज़ी, हिंदी, या हिंग्लिश में बात करें — AI झारखंड की भाषा समझता है।",
    hinglish: "English, Hindi ya Hinglish mein baat karo — AI Jharkhand ki language samajhta hai.",
  },
  "home.about.feature3.title": {
    en: "Privacy First",
    hi: "गोपनीयता प्राथमिकता",
    hinglish: "Privacy First",
  },
  "home.about.feature3.desc": {
    en: "Your data stays local. No cloud storage of personal information. Session-based and secure.",
    hi: "आपका डेटा स्थानीय रहता है। व्यक्तिगत जानकारी क्लाउड पर नहीं जाती। सत्र-आधारित और सुरक्षित।",
    hinglish: "Aapka data local rehta hai. Personal info cloud pe nahi jaati. Session-based aur secure.",
  },
  "home.about.feature4.title": {
    en: "Real Jharkhand Schemes",
    hi: "असली झारखंड योजनाएँ",
    hinglish: "Real Jharkhand Schemes",
  },
  "home.about.feature4.desc": {
    en: "25+ verified schemes across agriculture, housing, education, women empowerment, and more.",
    hi: "कृषि, आवास, शिक्षा, महिला सशक्तिकरण और अन्य में 25+ सत्यापित योजनाएँ।",
    hinglish: "Agriculture, housing, education, women empowerment mein 25+ verified schemes.",
  },
  "home.about.tech.title": {
    en: "Built With Modern Technology",
    hi: "आधुनिक तकनीक से निर्मित",
    hinglish: "Modern Technology se bana",
  },
  "home.about.tech.desc": {
    en: "Next.js + FastAPI + SQLite + Google Gemini / Ollama • Deterministic Eligibility Engine • Profile Accumulation • Multi-Agent Orchestration",
    hi: "Next.js + FastAPI + SQLite + Google Gemini / Ollama • नियतात्मक पात्रता इंजन • प्रोफ़ाइल संचय • मल्टी-एजेंट ऑर्केस्ट्रेशन",
    hinglish: "Next.js + FastAPI + SQLite + Google Gemini / Ollama • Deterministic Eligibility Engine • Profile Accumulation • Multi-Agent Orchestration",
  },
  "home.footer.disclaimer": {
    en: "Samarth is a Dissertation Research Project and is not officially affiliated with the Government of Jharkhand. Information is for educational and assistive purposes only. Always verify on official government portals.",
    hi: "समर्थ एक शोध प्रबंध परियोजना है और झारखंड सरकार से आधिकारिक रूप से संबद्ध नहीं है। जानकारी केवल शैक्षिक और सहायक उद्देश्यों के लिए है। हमेशा आधिकारिक सरकारी पोर्टल पर सत्यापित करें।",
    hinglish: "Samarth ek Dissertation Research Project hai aur officially Jharkhand Government se affiliated nahi hai. Information sirf educational aur assistive purposes ke liye hai. Hamesha official government portals pe verify karein.",
  },
  "home.footer.made": {
    en: "A Dissertation Project",
    hi: "एक शोध प्रबंध परियोजना",
    hinglish: "Ek Dissertation Project",
  },

  // ─── EXPLORE PAGE ──────────────────────────────────────
  "explore.title": {
    en: "Explore",
    hi: "देखें",
    hinglish: "Explore",
  },
  "explore.title2": {
    en: "Schemes",
    hi: "योजनाएँ",
    hinglish: "Schemes",
  },
  "explore.desc": {
    en: "Browse through all active government schemes in Jharkhand. Select a category below to see available support and benefits.",
    hi: "झारखंड की सभी सक्रिय सरकारी योजनाओं को ब्राउज़ करें। उपलब्ध सहायता और लाभ देखने के लिए नीचे एक श्रेणी चुनें।",
    hinglish: "Jharkhand ki saari active sarkari schemes browse karo. Support aur benefits dekhne ke liye neeche category select karo.",
  },
  "explore.schemes_count": {
    en: "Schemes",
    hi: "योजनाएँ",
    hinglish: "Schemes",
  },
  "explore.explore_link": {
    en: "Explore schemes →",
    hi: "योजनाएँ देखें →",
    hinglish: "Schemes dekho →",
  },
  "explore.found_count": {
    en: "active matching schemes.",
    hi: "सक्रिय मिलती योजनाएँ।",
    hinglish: "active matching schemes.",
  },
  "explore.no_schemes": {
    en: "No schemes found",
    hi: "कोई योजना नहीं मिली",
    hinglish: "Koi scheme nahi mili",
  },
  "explore.no_schemes_desc": {
    en: "We couldn't find any active schemes in this category at the moment.",
    hi: "इस श्रेणी में इस समय कोई सक्रिय योजना नहीं मिली।",
    hinglish: "Is category mein abhi koi active scheme nahi mili.",
  },

  // ─── EXPLORE SCHEME CARD ───────────────────────────────
  "scheme_card.key_benefit": {
    en: "Key Benefit",
    hi: "मुख्य लाभ",
    hinglish: "Main Benefit",
  },
  "scheme_card.details": {
    en: "Details",
    hi: "विवरण",
    hinglish: "Details",
  },
  "scheme_card.view_benefits": {
    en: "View Benefits Details",
    hi: "लाभ विवरण देखें",
    hinglish: "Benefits Details Dekho",
  },
  "scheme_card.up_to": {
    en: "Up to",
    hi: "अधिकतम",
    hinglish: "Up to",
  },
  "scheme_card.per_month": {
    en: "/ month",
    hi: "/ माह",
    hinglish: "/ month",
  },

  // ─── SCHEME DETAIL PAGE ────────────────────────────────
  "detail.eligibility": {
    en: "Eligibility Criteria",
    hi: "पात्रता मानदंड",
    hinglish: "Eligibility Criteria",
  },
  "detail.documents": {
    en: "Required Documents",
    hi: "आवश्यक दस्तावेज़",
    hinglish: "Zaruri Documents",
  },
  "detail.mandatory": {
    en: "mandatory document",
    hi: "अनिवार्य दस्तावेज़",
    hinglish: "mandatory document",
  },
  "detail.benefit_type": {
    en: "Benefit Type",
    hi: "लाभ प्रकार",
    hinglish: "Benefit Type",
  },
  "detail.how_to_apply": {
    en: "How to Apply",
    hi: "आवेदन कैसे करें",
    hinglish: "Apply Kaise Karo",
  },
  "detail.online_portal": {
    en: "Online Portal",
    hi: "ऑनलाइन पोर्टल",
    hinglish: "Online Portal",
  },
  "detail.visit_site": {
    en: "Visit Official Site",
    hi: "आधिकारिक साइट पर जाएँ",
    hinglish: "Official Site Dekho",
  },
  "detail.manual_steps": {
    en: "Manual Steps",
    hi: "मैन्युअल चरण",
    hinglish: "Manual Steps",
  },
  "detail.not_found": {
    en: "Scheme Not Found",
    hi: "योजना नहीं मिली",
    hinglish: "Scheme Nahi Mili",
  },
  "detail.return": {
    en: "Return to Explore",
    hi: "योजनाओं पर वापस जाएँ",
    hinglish: "Explore pe Wapas Jao",
  },

  // ─── CHAT PAGE ─────────────────────────────────────────
  "chat.welcome": {
    en: "Johar! 🙏 I am Samarth — your government scheme assistant. I can help you discover Jharkhand's government schemes.\n\nFirst, what is your name? And what type of scheme would you like to know about?",
    hi: "जोहार! 🙏 मैं समर्थ हूँ — आपका सरकारी योजना सहायक। मैं आपको झारखंड की सरकारी योजनाओं के बारे में मदद कर सकता हूँ।\n\nसबसे पहले, आपका नाम क्या है? और आप किस प्रकार की योजना के बारे में जानना चाहते हैं?",
    hinglish: "Johar! 🙏 Main Samarth hoon — aapka government scheme assistant. Main aapko Jharkhand ki sarkari yojanaon ke baare mein madad kar sakta hoon.\n\nSabse pehle, aapka naam kya hai? Aur aap kis type ki scheme ke baare mein jaanna chahte hain?",
  },
  "chat.placeholder": {
    en: "Type your message in English, Hindi or Hinglish...",
    hi: "अपना संदेश हिंदी, अंग्रेजी या हिंग्लिश में लिखें...",
    hinglish: "Apna message Hindi, English ya Hinglish mein likho...",
  },
  "chat.placeholder_typing": {
    en: "Type your next message while AI is thinking...",
    hi: "AI सोच रहा है... अगला संदेश लिखते रहें...",
    hinglish: "AI soch raha hai... apna agla message likho...",
  },
  "chat.disclaimer": {
    en: "Samarth uses AI. Always verify information on official portals.",
    hi: "समर्थ AI का उपयोग करता है। हमेशा आधिकारिक पोर्टल पर जानकारी सत्यापित करें।",
    hinglish: "Samarth AI use karta hai. Hamesha official portals pe info verify karo.",
  },
  "chat.profile_engine": {
    en: "Profile Engine",
    hi: "प्रोफ़ाइल इंजन",
    hinglish: "Profile Engine",
  },
  "chat.profile_desc": {
    en: "Context builds deterministic accuracy",
    hi: "संदर्भ सटीकता बनाता है",
    hinglish: "Context se accuracy banti hai",
  },
  "chat.confidence": {
    en: "AI Context Confidence",
    hi: "AI संदर्भ विश्वास",
    hinglish: "AI Context Confidence",
  },
  "chat.today": {
    en: "Today",
    hi: "आज",
    hinglish: "Aaj",
  },
  "chat.quick.housing": {
    en: "I need a housing scheme",
    hi: "मुझे घर बनाने की योजना चाहिए",
    hinglish: "Mujhe ghar banane ki scheme chahiye",
  },
  "chat.quick.farmer": {
    en: "I am a farmer, any schemes?",
    hi: "मैं किसान हूँ, कोई योजना है?",
    hinglish: "Main kisan hoon, koi yojana hai kya?",
  },
  "chat.quick.scholarship": {
    en: "Any scholarships for girls?",
    hi: "लड़कियों के लिए कोई छात्रवृत्ति?",
    hinglish: "Ladkiyon ke liye koi scholarship?",
  },
  "chat.quick.pension": {
    en: "How to apply for pension?",
    hi: "पेंशन के लिए कैसे आवेदन करें?",
    hinglish: "Pension ke liye kaise apply karein?",
  },
  "chat.error_connect": {
    en: "Connecting to server failed. Please try again later. Is the backend running?",
    hi: "सर्वर से कनेक्ट नहीं हो पाया। कृपया बाद में पुनः प्रयास करें। क्या बैकएंड चल रहा है?",
    hinglish: "Server se connect nahi ho paya. Please baad mein try karo. Kya backend chal raha hai?",
  },

  // ─── SCHEME CARD (CHAT) ────────────────────────────────
  "chatcard.failed": {
    en: "Failed Criteria",
    hi: "असफल मानदंड",
    hinglish: "Failed Criteria",
  },
  "chatcard.missing": {
    en: "Missing Profile Data",
    hi: "प्रोफ़ाइल डेटा गायब है",
    hinglish: "Profile Data Missing Hai",
  },
  "chatcard.view_proof": {
    en: "View Eligibility Proof & Steps →",
    hi: "पात्रता प्रमाण और चरण देखें →",
    hinglish: "Eligibility Proof & Steps Dekho →",
  },

  // ─── PROFILE LABELS ────────────────────────────────────
  "profile.name": { en: "Name", hi: "नाम", hinglish: "Naam" },
  "profile.age": { en: "Age", hi: "उम्र", hinglish: "Age" },
  "profile.income": { en: "Income", hi: "आय", hinglish: "Income" },
  "profile.category": { en: "Category", hi: "श्रेणी", hinglish: "Category" },
  "profile.gender": { en: "Gender", hi: "लिंग", hinglish: "Gender" },
  "profile.occupation": { en: "Occupation", hi: "व्यवसाय", hinglish: "Occupation" },
  "profile.farmer_type": { en: "Farmer Type", hi: "किसान प्रकार", hinglish: "Farmer Type" },
  "profile.housing": { en: "Housing", hi: "आवास", hinglish: "Housing" },
  "profile.student_class": { en: "Student Class", hi: "कक्षा", hinglish: "Class" },
  "profile.marital_status": { en: "Marital Status", hi: "वैवाहिक स्थिति", hinglish: "Marital Status" },
  "profile.ration": { en: "Ration Card", hi: "राशन कार्ड", hinglish: "Ration Card" },

  // ─── CATEGORY NAMES ────────────────────────────────────
  "cat.agriculture": { en: "Agriculture", hi: "कृषि", hinglish: "Agriculture" },
  "cat.housing": { en: "Housing", hi: "आवास", hinglish: "Housing" },
  "cat.education": { en: "Education", hi: "शिक्षा", hinglish: "Education" },
  "cat.women": { en: "Women", hi: "महिला", hinglish: "Women" },
  "cat.social_security": { en: "Social Security", hi: "सामाजिक सुरक्षा", hinglish: "Social Security" },
  "cat.employment": { en: "Employment", hi: "रोज़गार", hinglish: "Rozgaar" },

  // ─── LANGUAGE SELECTOR ─────────────────────────────────
  "lang.en": { en: "English", hi: "English", hinglish: "English" },
  "lang.hi": { en: "हिंदी", hi: "हिंदी", hinglish: "हिंदी" },
  "lang.hinglish": { en: "Hinglish", hi: "Hinglish", hinglish: "Hinglish" },

  // ─── NAVBAR — AI ASSISTANT ────────────────────────────
  "nav.ai": {
    en: "Pure AI",
    hi: "Pure AI",
    hinglish: "Pure AI",
  },

  // ─── PURE AI ASSISTANT PAGE ───────────────────────────
  "ai.title": {
    en: "Pure AI Assistant",
    hi: "Pure AI सहायक",
    hinglish: "Pure AI Assistant",
  },
  "ai.subtitle": {
    en: "Conversational government scheme advisor",
    hi: "वार्तालाप आधारित सरकारी योजना सलाहकार",
    hinglish: "Conversational sarkari yojana advisor",
  },
  "ai.badge": {
    en: "Samarth AI Advisor",
    hi: "समर्थ AI सलाहकार",
    hinglish: "Samarth AI Advisor",
  },
  "ai.welcome": {
    en: "Namaste! 🙏 I am Samarth, your dedicated **Government Scheme Advisor**.\n\nI am here to help you personally with any question about Jharkhand government schemes — from checking your eligibility and understanding benefits, to knowing the right documents and application process.\n\nUnlike an automated system, I can have a real conversation with you to find exactly what you need.\n\nAsk me anything! For example:\n• \"Which housing schemes are available for BPL families?\"\n• \"What documents do I need to prepare for PM Kisan?\"\n• \"Can you explain the Savitribai Phule scheme benefits?\"",
    hi: "नमस्ते! 🙏 मैं समर्थ हूँ, आपका अपना **सरकारी योजना सलाहकार**।\n\nमैं झारखंड की योजनाओं से जुड़े आपके हर सवाल का जवाब देने के लिए यहाँ हूँ — चाहे वो पात्रता जानना हो, लाभ समझना हो, या आवेदन प्रक्रिया की जानकारी चाहिए।\n\nएक मशीन की तरह नहीं, मैं आपसे बातचीत करके आपके लिए सबसे सही योजना खोज सकता हूँ।\n\nकुछ भी पूछें! जैसे:\n• \"BPL परिवारों के लिए कौन सी आवास योजनाएं हैं?\"\n• \"PM किसान के लिए मुझे कौन से दस्तावेज़ तैयार करने होंगे?\"\n• \"क्या आप सावित्रीबाई फुले योजना के लाभ समझा सकते हैं?\"",
    hinglish: "Namaste! 🙏 Main Samarth hoon, aapka apna **Sarkari Yojana Advisor**.\n\nMain Jharkhand ki yojanaon se jude aapke har sawaal ka properly jawab dene ke liye yahan hoon — eligibility rules, benefits, documents, aur application process sab samjhaunga.\n\nEk normal system se alag, main aapse human-like conversation karke aapke liye correct schemes dhoondh sakta hoon.\n\nKuch bhi pucho! Jaise:\n• \"BPL families ke liye housing schemes kaun si hain?\"\n• \"PM Kisan form ke liye kya documents ready rakhne honge?\"\n• \"Savitribai Phule scheme ke benefits ache se samjha do?\"",
  },
  "ai.placeholder": {
    en: "Ask anything about Jharkhand schemes...",
    hi: "झारखंड योजनाओं के बारे में कुछ भी पूछें...",
    hinglish: "Jharkhand schemes ke baare mein kuch bhi pucho...",
  },
  "ai.placeholder_typing": {
    en: "Type your next question while AI is searching...",
    hi: "AI खोज रहा है... अगला सवाल लिखते रहें...",
    hinglish: "AI search kar raha hai... apna agla sawaal likho...",
  },
  "ai.disclaimer": {
    en: "Pure AI mode uses RAG for comprehensive answers. Always verify on official portals.",
    hi: "Pure AI मोड RAG का उपयोग करता है। हमेशा आधिकारिक पोर्टल पर सत्यापित करें।",
    hinglish: "Pure AI mode RAG use karta hai. Hamesha official portals pe verify karo.",
  },
  "ai.capabilities": {
    en: "What I Can Do",
    hi: "मेरी क्षमताएँ",
    hinglish: "Main Kya Kar Sakta Hoon",
  },
  "ai.cap.search": {
    en: "Search & find relevant schemes instantly",
    hi: "प्रासंगिक योजनाएँ खोजें",
    hinglish: "Relevant schemes instantly dhundho",
  },
  "ai.cap.compare": {
    en: "Compare multiple schemes side by side",
    hi: "कई योजनाओं की तुलना करें",
    hinglish: "Multiple schemes compare karo",
  },
  "ai.cap.apply": {
    en: "Step-by-step application guidance",
    hi: "चरण-दर-चरण आवेदन मार्गदर्शन",
    hinglish: "Step-by-step apply karne ki guidance",
  },
  "ai.cap.documents": {
    en: "Explain required documents clearly",
    hi: "आवश्यक दस्तावेज़ स्पष्ट रूप से बताएं",
    hinglish: "Required documents clearly samjhao",
  },
  "ai.cap.suggest": {
    en: "Suggest schemes based on your situation",
    hi: "आपकी स्थिति के अनुसार योजनाएँ सुझाएं",
    hinglish: "Aapki situation ke hisaab se schemes suggest karo",
  },
  "ai.cap.multilingual": {
    en: "Answer in English, Hindi, or Hinglish",
    hi: "अंग्रेज़ी, हिंदी, या हिंग्लिश में जवाब",
    hinglish: "English, Hindi ya Hinglish mein jawab",
  },
  "ai.powered_by": {
    en: "Powered By",
    hi: "द्वारा संचालित",
    hinglish: "Powered By",
  },
  "ai.rag_desc": {
    en: "Retrieves relevant scheme data using BM25 scoring, then generates answers with full context.",
    hi: "BM25 स्कोरिंग से योजना डेटा लाता है, फिर पूर्ण संदर्भ के साथ उत्तर बनाता है।",
    hinglish: "BM25 scoring se relevant scheme data lata hai, phir full context ke saath answer generate karta hai.",
  },
  "ai.suggest.compare": {
    en: "Compare housing schemes for poor families",
    hi: "गरीब परिवारों के लिए आवास योजनाओं की तुलना",
    hinglish: "Garib families ke liye housing schemes compare karo",
  },
  "ai.suggest.housing": {
    en: "Tell me about Abua Awas Yojana",
    hi: "अबुआ आवास योजना के बारे में बताइए",
    hinglish: "Abua Awas Yojana ke baare mein batao",
  },
  "ai.suggest.apply": {
    en: "How to apply for PM Kisan scheme?",
    hi: "PM किसान योजना के लिए कैसे आवेदन करें?",
    hinglish: "PM Kisan scheme ke liye kaise apply karein?",
  },
  "ai.suggest.documents": {
    en: "What documents needed for pension?",
    hi: "पेंशन के लिए कौन से दस्तावेज़ चाहिए?",
    hinglish: "Pension ke liye kya documents chahiye?",
  },
};

// ─── PROVIDER ───────────────────────────────────────────
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Language>('en');

  useEffect(() => {
    const stored = localStorage.getItem('samarth_lang') as Language | null;
    if (stored && ['en', 'hi', 'hinglish'].includes(stored)) {
      setLang(stored);
    }
  }, []);

  const handleSetLang = (newLang: Language) => {
    setLang(newLang);
    localStorage.setItem('samarth_lang', newLang);
  };

  const t = (key: string): string => {
    return translations[key]?.[lang] || translations[key]?.en || key;
  };

  const langLabel = lang === 'en' ? 'EN' : lang === 'hi' ? 'हि' : 'HG';

  return (
    <LanguageContext.Provider value={{ lang, setLang: handleSetLang, t, langLabel }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
