'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import PhoneIllustration from '../find-a-phone/phone-illustration';
import { ChatComposer, ChatTranscript, type ChatMessage } from './diagnosis-chat';
import IntroBackdrop from './intro-backdrop';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Cpu, ExternalLink, ChevronDown, ShieldCheck, Sparkles,
  Filter, SlidersHorizontal, ArrowUpDown, Search, RotateCcw, Check 
} from 'lucide-react';

type SpecAnswer = {
  question: string;
  answer: string;
  source_url?: string;
  source?: string;
  section?: string;
  retrieved_at?: string;
  citation?: string;
  source_verification_status?: string;
  source_scope?: string;
};

type Decision = {
  recommended_path: string;
  reason: string;
  cost_to_device_value_ratio?: number | null;
  repair_cost_midpoint_lkr?: number | null;
  device_value_lkr?: number | null;
  cost_verified?: boolean;
};

type ResourceLink = {
  title: string;
  url: string;
  source?: string;
  type?: string;
  difficulty?: string;
};

type DetailedStep = {
  text: string;
  classification?: string;
  resources?: ResourceLink[];
};

type Troubleshooting = {
  steps?: string[];
  detailed_steps?: DetailedStep[];
  escalate_to_technician?: boolean;
  escalation_reason?: string;
  resource_note?: string;
};

type RepairCost = {
  min_lkr: number | null;
  max_lkr: number | null;
  currency?: string;
  source?: string;
  source_url?: string;
  retrieved_at?: string;
  pricing_type?: string;
  verified?: boolean;
  part_quality?: string;
  labor_included?: string;
  warranty_duration?: string;
  location?: string;
  status?: string;
  message?: string;
  note?: string;
};

export type DiagnosisResult = {
  chat_reply?: { message: string; question_id?: string | null };
  matched_device?: {
    brand: string;
    model: string;
    canonical_name: string;
    was_corrected: boolean;
    confidence?: number;
    original_input?: string;
    matched_id?: string;
    match_status?: string;
  };
  diagnosis: {
    fault_category: string;
    probable_cause: string;
    confidence: string;
    uncertainty?: string;
    follow_up_questions?: string[];
    image_attached?: boolean;
    image_reviewed?: boolean;
  };
  safety_flags: { code: string; message: string }[];
  repair_cost: RepairCost | null;
  decision?: Decision | null;
  spec_answers?: SpecAnswer[];
  troubleshooting?: Troubleshooting | null;
  recommendations: {
    id: string;
    name: string;
    price_lkr: number | null;
    score?: number | null;
    over_budget?: boolean;
    verdict_vs_old?: string;
    dimensions?: Record<string, number>;
    product?: {
      ram_gb?: number;
      storage_gb?: number;
      display_type?: string;
      battery_mah?: number;
      camera_mp?: number;
      has_5g?: boolean;
      price_source?: string;
      source_url?: string;
    };
  }[];
};

const formatPrice = new Intl.NumberFormat('en-LK', { maximumFractionDigits: 2 });

function getPhoneImage(name: string): { src?: string; isPhoto: boolean } {
  const n = name.toLowerCase();
  if (n.includes('iphone 13 pro')) return { src: '/phones/iphone-camera.webp', isPhoto: true };
  if (n.includes('iphone')) return { src: '/phones/iphone-front.webp', isPhoto: true };
  if (n.includes('galaxy') || n.includes('samsung')) return { src: '/phones/galaxy-front.webp', isPhoto: true };
  if (n.includes('pixel')) return { src: '/phones/pixel-front.webp', isPhoto: true };
  return { isPhoto: false };
}

const KNOWN_CATALOG: Record<string, { models: string[]; variants?: Record<string, string[]> }> = {
  Apple: {
    models: ['iPhone 13', 'iPhone 13 Pro'],
    variants: {
      'iPhone 13': ['128GB', '256GB', '512GB'],
      'iPhone 13 Pro': ['128GB', '256GB', '512GB', '1TB'],
    },
  },
  Samsung: {
    models: ['Galaxy A55', 'Galaxy A51'],
    variants: {
      'Galaxy A55': ['128GB', '256GB'],
      'Galaxy A51': ['128GB'],
    },
  },
  Xiaomi: {
    models: ['Redmi Note 13 4G', 'Redmi Note 13 5G', 'Redmi Note 13'],
    variants: {
      'Redmi Note 13 4G': ['128GB', '256GB'],
      'Redmi Note 13 5G': ['128GB', '256GB'],
      'Redmi Note 13': ['128GB', '256GB'],
    },
  },
  Google: {
    models: ['Pixel 8a'],
    variants: {
      'Pixel 8a': ['128GB', '256GB'],
    },
  },
  Poco: {
    models: ['X6'],
    variants: {
      'X6': ['256GB', '512GB'],
    },
  },
};

function detectDeviceFromText(text: string): { brand: string; model: string; variant?: string } | null {
  const t = text.toLowerCase();
  if (t.includes('iphone 13 pro')) return { brand: 'Apple', model: 'iPhone 13 Pro', variant: '128GB' };
  if (t.includes('iphone 13') || t.includes('iphone') || t.includes('iponw')) return { brand: 'Apple', model: 'iPhone 13', variant: '128GB' };
  if (t.includes('galaxy a55') || t.includes('a55')) return { brand: 'Samsung', model: 'Galaxy A55', variant: '128GB' };
  if (t.includes('galaxy a51') || t.includes('a51') || t.includes('galxy')) return { brand: 'Samsung', model: 'Galaxy A51', variant: '128GB' };
  if (t.includes('samsung') || t.includes('galaxy')) return { brand: 'Samsung', model: 'Galaxy A51', variant: '128GB' };
  if (t.includes('pixel 8a') || t.includes('pixel') || t.includes('pixl')) return { brand: 'Google', model: 'Pixel 8a', variant: '128GB' };
  if (t.includes('redmi note 13 4g')) return { brand: 'Xiaomi', model: 'Redmi Note 13 4G', variant: '128GB' };
  if (t.includes('redmi note 13 5g')) return { brand: 'Xiaomi', model: 'Redmi Note 13 5G', variant: '256GB' };
  if (t.includes('redmi note 13') || t.includes('redmi') || t.includes('xiaomi')) return { brand: 'Xiaomi', model: 'Redmi Note 13 4G', variant: '128GB' };
  if (t.includes('poco x6') || t.includes('poco')) return { brand: 'Poco', model: 'X6', variant: '256GB' };
  return null;
}

export default function Home() {
  const [step, setStep] = useState<'input' | 'confirm_device' | 'diagnosed' | 'repair' | 'recommendations'>('input');
  
  const [query, setQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pendingIssue, setPendingIssue] = useState<{ text: string; image: string | null } | null>(null);
  const [conversationImage, setConversationImage] = useState<string | null>(null);
  const requestInFlight = useRef(false);
  
  const [brand, setBrand] = useState('Apple');
  const [model, setModel] = useState('iPhone 13');
  const [variant, setVariant] = useState('128GB');

  const availableModels = brand && KNOWN_CATALOG[brand] ? KNOWN_CATALOG[brand].models : [];
  const availableVariants = brand && model && KNOWN_CATALOG[brand]?.variants?.[model]
    ? KNOWN_CATALOG[brand].variants![model]
    : ['128GB', '256GB', '512GB'];

  // Recommendation Filtering & Sorting States
  const [filterBrand, setFilterBrand] = useState<string>('All');
  const [sortBy, setSortBy] = useState<'match' | 'price_asc' | 'price_desc' | 'performance' | 'battery' | 'camera'>('match');
  const [maxBudget, setMaxBudget] = useState<number | null>(null);
  const [only5G, setOnly5G] = useState<boolean>(false);
  const [minRam, setMinRam] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const availableBrands = useMemo(() => {
    if (!result?.recommendations) return ['All'];
    const brands = new Set<string>();
    for (const p of result.recommendations) {
      const b = p.name.split(' ')[0] || '';
      if (b) brands.add(b);
    }
    return ['All', ...Array.from(brands)];
  }, [result?.recommendations]);

  const filteredRecommendations = useMemo(() => {
    if (!result?.recommendations) return [];
    let list = [...result.recommendations];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((p) => p.name.toLowerCase().includes(q));
    }

    if (filterBrand !== 'All') {
      list = list.filter((p) => p.name.toLowerCase().startsWith(filterBrand.toLowerCase()));
    }

    if (maxBudget !== null) {
      list = list.filter((p) => p.price_lkr !== null && p.price_lkr <= maxBudget);
    }

    if (only5G) {
      list = list.filter((p) => Boolean(p.product?.has_5g));
    }

    if (minRam !== null) {
      list = list.filter((p) => (p.product?.ram_gb ?? 0) >= minRam);
    }

    list.sort((a, b) => {
      if (sortBy === 'price_asc') {
        return (a.price_lkr ?? Infinity) - (b.price_lkr ?? Infinity);
      }
      if (sortBy === 'price_desc') {
        return (b.price_lkr ?? -Infinity) - (a.price_lkr ?? -Infinity);
      }
      if (sortBy === 'performance') {
        return (b.dimensions?.performance ?? 0) - (a.dimensions?.performance ?? 0);
      }
      if (sortBy === 'battery') {
        return (b.dimensions?.battery ?? 0) - (a.dimensions?.battery ?? 0);
      }
      if (sortBy === 'camera') {
        return (b.dimensions?.camera ?? 0) - (a.dimensions?.camera ?? 0);
      }
      return (b.score ?? 0) - (a.score ?? 0);
    });

    return list;
  }, [result?.recommendations, filterBrand, sortBy, maxBudget, only5G, minRam, searchQuery]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const issue = params.get('issue');
      if (issue) {
        setQuery(`Issue: ${issue}. `);
      }
      const pBrand = params.get('brand');
      const pModel = params.get('model');
      if (pBrand && pBrand in KNOWN_CATALOG) {
        setBrand(pBrand);
        if (pModel && KNOWN_CATALOG[pBrand].models.includes(pModel)) {
          setModel(pModel);
          const vList = KNOWN_CATALOG[pBrand].variants?.[pModel] || [];
          if (vList.length > 0) setVariant(vList[0]);
        }
      }
    }
  }, []);

  const handleInitialSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && !selectedImage) return;
    setError('');

    const detected = detectDeviceFromText(query);
    if (detected && detected.brand in KNOWN_CATALOG) {
      setBrand(detected.brand);
      const brandModels = KNOWN_CATALOG[detected.brand].models;
      if (brandModels.includes(detected.model)) {
        setModel(detected.model);
        const vList = KNOWN_CATALOG[detected.brand]?.variants?.[detected.model] || [];
        setVariant(detected.variant && vList.includes(detected.variant) ? detected.variant : (vList[0] || '128GB'));
      } else {
        setModel(brandModels[0]);
        const vList = KNOWN_CATALOG[detected.brand]?.variants?.[brandModels[0]] || [];
        setVariant(vList[0] || '128GB');
      }
    } else if (!brand || !(brand in KNOWN_CATALOG)) {
      setBrand('Apple');
      setModel('iPhone 13');
      setVariant('128GB');
    }

    setPendingIssue({ text: query.trim(), image: selectedImage });
    setMessages([{ id: crypto.randomUUID(), role: 'user', content: query.trim() || 'Please help me with the issue in this photo.', image: selectedImage }]);
    setQuery('');
    setSelectedImage(null);
    setStep('confirm_device');
  };

  const assistantMessage = (data: DiagnosisResult): ChatMessage => ({
    id: crypto.randomUUID(), role: 'assistant',
    content: data.chat_reply?.message || `${data.diagnosis.probable_cause}\n\n${data.diagnosis.follow_up_questions?.[0] || 'What else have you noticed about this issue?'}`,
    question_id: data.chat_reply?.question_id,
    assessment: data,
  });

  const cancelConfirmation = () => {
    setQuery(pendingIssue?.text || '');
    setSelectedImage(pendingIssue?.image || null);
    setPendingIssue(null);
    setMessages([]);
    setError('');
    setStep('input');
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (requestInFlight.current || loading || step === 'confirm_device') return;
    if (!result) { handleInitialSubmit(e); return; }
    void sendFollowup(query.trim(), selectedImage);
  };

  const sendFollowup = async (draft: string, image: string | null = null) => {
    if (requestInFlight.current || loading || step === 'confirm_device' || !result || (!draft && !image)) return;
    requestInFlight.current = true;
    const previousMessages = messages;
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: draft || 'Here is another photo of the issue.', image };
    setMessages([...previousMessages, userMessage]);
    setQuery('');
    setSelectedImage(null);
    setError('');
    setLoading(true);
    setStep('diagnosed');
    try {
      // Keep the original issue alongside recent turns when a conversation is long.
      const history = previousMessages.length <= 40 ? previousMessages : [previousMessages[0], ...previousMessages.slice(-39)];
      const response = await fetch('/api/diagnose', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: draft || userMessage.content, brand, model, variant,
          image_data_uri: image || conversationImage,
          messages: history.map(({ role, content, question_id }) => ({ role, content: content.slice(0, 4000), question_id })),
        }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data?.diagnosis) throw new Error(typeof (data?.error ?? data?.detail) === 'string' ? (data.error ?? data.detail) : 'Could not send your message. Please try again.');
      setResult(data);
      setMessages([...previousMessages, userMessage, assistantMessage(data)]);
      if (image) setConversationImage(image);
    } catch (cause) {
      setMessages(previousMessages);
      setQuery(draft);
      setSelectedImage(image);
      setError(cause instanceof Error ? cause.message : 'Could not send your message. Please try again.');
    } finally {
      requestInFlight.current = false;
      setLoading(false);
    }
  };

  const handleConfirmDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (requestInFlight.current || loading || !pendingIssue) return;
    requestInFlight.current = true;
    setLoading(true);
    setError('');

    if (!brand.trim() || !model.trim()) {
      setError('Please select both brand and model name.');
      requestInFlight.current = false;
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: pendingIssue.text,
          brand: brand.trim(),
          model: model.trim(),
          variant: variant.trim(),
          image_data_uri: pendingIssue.image,
        }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data?.diagnosis) {
        const message = data?.error ?? data?.detail;
        throw new Error(typeof message === 'string' ? message : 'Diagnosis failed. Check your details and try again.');
      }
      setResult(data);
      setMessages(previous => [...previous, assistantMessage(data)]);
      setConversationImage(pendingIssue.image);
      setPendingIssue(null);
      setStep('diagnosed');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Diagnosis failed. Please try again.');
    } finally {
      requestInFlight.current = false;
      setLoading(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const image = e.target.files?.[0];
    if (!image) return;
    if (!image.type.startsWith('image/') || image.size > 5 * 1024 * 1024) {
      setError('Choose an image smaller than 5 MB.');
      return;
    }
    setError('');
    const reader = new FileReader();
    reader.onload = () => setSelectedImage(String(reader.result));
    reader.readAsDataURL(image);
  };

  const startNewDiagnosis = () => {
    setQuery('');
    setSelectedImage(null);
    setBrand('Apple');
    setModel('iPhone 13');
    setVariant('128GB');
    setResult(null);
    setMessages([]);
    setPendingIssue(null);
    setConversationImage(null);
    setError('');
    setStep('input');
    setFilterBrand('All');
    setSortBy('match');
    setMaxBudget(null);
    setOnly5G(false);
    setMinRam(null);
    setSearchQuery('');
  };

  const isIntro = messages.length === 0 && step === 'input';

  return (
    <main className={`diagnosis-chat-page ${isIntro ? 'diagnosis-intro-page' : ''} flex flex-1 flex-col items-center p-4 md:p-8 relative text-ink-100 selection:bg-cyan-500 selection:text-foreground`}>
      {isIntro && <IntroBackdrop />}
      


      <header className="relative z-10 mx-auto mb-8 flex w-full max-w-4xl items-start justify-between gap-4">
        {isIntro ? <><div className="diagnosis-intro-brand"><span><Cpu size={22} aria-hidden="true" /></span><div><p>REVIVAI</p><span>Intelligent device diagnosis</span></div></div><span className="diagnosis-intro-ready"><ShieldCheck size={13} aria-hidden="true" /> Ready to diagnose</span></> : <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-cyan-ink-300">Your phone assistant</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Let&apos;s work through it.</h1>
          <p className="mt-2 text-sm text-ink-400">{result ? [result.matched_device?.canonical_name || `${brand} ${model}`, variant].filter(Boolean).join(' / ') : 'A conversation about your phone, one step at a time.'}</p>
        </div>}
        {messages.length > 0 && <button type="button" onClick={startNewDiagnosis} disabled={loading} className="shrink-0 rounded-xl border border-line/10 bg-raised/60 px-3 py-2 text-xs font-medium text-ink-300 hover:bg-raised disabled:opacity-50">Start over</button>}
      </header>

      {/* MAIN DIAGNOSTIC WORKFLOW CONTAINER */}
      <div className={`relative z-10 flex w-full max-w-4xl ${isIntro ? 'diagnosis-intro-body' : 'flex-1'} flex-col`}>
        <ChatTranscript messages={messages} loading={loading} onAnswer={text => void sendFollowup(text)} onDraft={text => { setQuery(text); document.getElementById('diagnosis-message')?.focus({ preventScroll: true }); }} />
        <AnimatePresence mode="wait">
          
          {/* STEP 2: CONFIRM DEVICE */}
          {step === 'confirm_device' && (
            <motion.div
              key="confirm_device"
              id="confirm-device"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="bg-surface/70 backdrop-blur-xl border border-cyan-500/30 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl"
            >
              <div className="border-b border-line/10 pb-4">
                <span className="text-xs text-cyan-ink-400 font-mono uppercase tracking-wider">Step 2: Confirm Device Details</span>
                <h2 className="text-2xl font-bold text-foreground mt-1">Verify Your Phone Model</h2>
              </div>

              <form onSubmit={handleConfirmDevice} className="space-y-5">
                <fieldset disabled={loading} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {/* Brand Select Dropdown */}
                    <div className="space-y-1.5">
                      <label className="text-xs text-ink-300 font-semibold block">Brand</label>
                      <div className="relative">
                        <select
                          value={brand}
                          onChange={(e) => {
                            const selectedBrand = e.target.value;
                            setBrand(selectedBrand);
                            const brandData = KNOWN_CATALOG[selectedBrand];
                            if (brandData && brandData.models.length > 0) {
                              const firstModel = brandData.models[0];
                              setModel(firstModel);
                              const vList = brandData.variants?.[firstModel] || [];
                              setVariant(vList[0] || '128GB');
                            }
                          }}
                          className="w-full bg-inset/80 border border-line/10 hover:border-cyan-500/40 rounded-xl px-3 py-2.5 text-xs text-foreground appearance-none cursor-pointer focus:outline-none focus:border-cyan-500 transition-all pr-8"
                        >
                          {Object.keys(KNOWN_CATALOG).map((b) => (
                            <option key={b} value={b} className="bg-surface text-foreground">
                              {b}
                            </option>
                          ))}
                        </select>
                        <ChevronDown className="w-3.5 h-3.5 text-ink-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                      </div>
                    </div>

                    {/* Model Select Dropdown */}
                    <div className="space-y-1.5">
                      <label className="text-xs text-ink-300 font-semibold block">Model Name</label>
                      <div className="relative">
                        <select
                          value={model}
                          onChange={(e) => {
                            const selectedModel = e.target.value;
                            setModel(selectedModel);
                            const vList = KNOWN_CATALOG[brand]?.variants?.[selectedModel] || [];
                            setVariant(vList[0] || '128GB');
                          }}
                          className="w-full bg-inset/80 border border-line/10 hover:border-cyan-500/40 rounded-xl px-3 py-2.5 text-xs text-foreground appearance-none cursor-pointer focus:outline-none focus:border-cyan-500 transition-all pr-8"
                        >
                          {availableModels.map((m) => (
                            <option key={m} value={m} className="bg-surface text-foreground">
                              {m}
                            </option>
                          ))}
                        </select>
                        <ChevronDown className="w-3.5 h-3.5 text-ink-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                      </div>
                    </div>

                    {/* Variant Select Dropdown */}
                    <div className="space-y-1.5">
                      <label className="text-xs text-ink-300 font-semibold block">Variant</label>
                      <div className="relative">
                        <select
                          value={variant}
                          onChange={(e) => setVariant(e.target.value)}
                          className="w-full bg-inset/80 border border-line/10 hover:border-cyan-500/40 rounded-xl px-3 py-2.5 text-xs text-foreground appearance-none cursor-pointer focus:outline-none focus:border-cyan-500 transition-all pr-8"
                        >
                          {availableVariants.map((v) => (
                            <option key={v} value={v} className="bg-surface text-foreground">
                              {v}
                            </option>
                          ))}
                        </select>
                        <ChevronDown className="w-3.5 h-3.5 text-ink-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-inset/50 border border-line/5 text-[11px] text-ink-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                    <span>
                      Hardware datasheets, modular teardown guides, and repair cost estimates are loaded directly for this model.
                    </span>
                  </div>
                </fieldset>

                {error && <p role="alert" className="text-sm text-rose-ink-300">{error}</p>}

                <div className="pt-4 flex justify-between items-center border-t border-line/10">
                  <button
                    type="button"
                    disabled={loading}
                    onClick={cancelConfirmation}
                    className="text-xs text-ink-400 hover:text-foreground underline disabled:opacity-50 cursor-pointer"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !brand || !model}
                    className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-xl text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] disabled:opacity-50 cursor-pointer"
                  >
                    {loading ? 'Running Diagnosis…' : 'Confirm & Run Diagnosis'}
                  </button>
                </div>
              </form>
            </motion.div>
          )}

          {/* STEP 4: REPAIR COST */}
          {step === 'repair' && result && (
            <motion.div id="diagnosis-option-panel" onAnimationComplete={() => document.getElementById('diagnosis-option-panel')?.scrollIntoView({ block: 'start' })} key="repair" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-surface/70 backdrop-blur-xl border border-line/10 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-line/10 pb-4">
                <h2 className="text-2xl font-bold text-foreground">Repair Cost Analysis</h2>
                <button onClick={() => setStep('diagnosed')} className="text-xs text-ink-400 underline">← Back</button>
              </div>
              {/* Pricing Card */}
              <div className="bg-inset/80 border border-cyan-500/30 rounded-2xl p-6 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line/10 pb-3">
                  <div>
                    <span className="text-[11px] text-ink-400 uppercase tracking-wider font-mono">Estimated Repair Range</span>
                    {result.repair_cost?.min_lkr != null && result.repair_cost.max_lkr != null ? (
                      <div className="text-2xl md:text-3xl font-black text-cyan-ink-400 font-mono mt-1">
                        LKR {formatPrice.format(result.repair_cost.min_lkr)} - {formatPrice.format(result.repair_cost.max_lkr)}
                      </div>
                    ) : (
                      <p className="text-sm text-ink-300 mt-1">{result.repair_cost?.message || 'No repair estimate is available for this device and issue.'}</p>
                    )}
                  </div>

                  {/* Pricing Badge */}
                  {result.repair_cost?.status === 'estimate' && (
                    <div>
                      {result.repair_cost.verified ? (
                        <span className="text-[11px] font-semibold text-emerald-ink-400 bg-emerald-tint-950/70 border border-emerald-500/40 px-3 py-1 rounded-full">
                          Verified Price
                        </span>
                      ) : result.repair_cost.pricing_type === 'catalog_price' ? (
                        <span className="text-[11px] font-semibold text-sky-ink-400 bg-sky-tint-950/70 border border-sky-500/40 px-3 py-1 rounded-full">
                          Published Catalog Listing
                        </span>
                      ) : (
                        <span className="text-[11px] font-semibold text-amber-ink-400 bg-amber-tint-950/70 border border-amber-500/40 px-3 py-1 rounded-full">
                          Unverified Indicative Range
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Structured Conditions */}
                <div className="space-y-2 text-xs text-ink-300">
                  {result.repair_cost?.part_quality && (
                    <p><strong className="text-cyan-ink-300">Part Quality:</strong> {result.repair_cost.part_quality}</p>
                  )}
                  {(result.repair_cost?.labor_included || result.repair_cost?.warranty_duration) && (
                    <p className="text-ink-400">
                      {[result.repair_cost.labor_included, result.repair_cost.warranty_duration].filter(Boolean).join(' • ')}
                    </p>
                  )}
                  {result.repair_cost?.source_url && (
                    <div className="pt-1">
                      <a 
                        href={result.repair_cost.source_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-cyan-ink-400 hover:underline"
                      >
                        <span>Source: {result.repair_cost.source || 'Workshop Listing'}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                      {result.repair_cost.retrieved_at && (
                        <span className="text-ink-400 ml-2 font-mono">({result.repair_cost.retrieved_at})</span>
                      )}
                    </div>
                  )}
                  {result.repair_cost?.note && <p className="text-ink-400 text-[11px] italic">{result.repair_cost.note}</p>}
                </div>
              </div>

              {/* AI Repair-vs-Replace Decision Card */}
              {result.decision && (
                <div className="bg-surface/80 border border-purple-500/30 rounded-2xl p-6 space-y-3 shadow-lg">
                  <div className="flex items-center justify-between border-b border-line/10 pb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-purple-ink-300">Repair vs. Replace Verdict</span>
                    <span className="text-xs font-semibold px-3 py-1 rounded-full bg-purple-tint-950/70 text-purple-ink-200 border border-purple-500/40 capitalize">
                      {result.decision.recommended_path.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-xs md:text-sm text-ink-200 leading-relaxed">{result.decision.reason}</p>
                  {result.decision.cost_to_device_value_ratio != null && (
                    <div className="text-[11px] text-ink-400 pt-1 font-mono">
                      Cost-to-device ratio: {(result.decision.cost_to_device_value_ratio * 100).toFixed(0)}% of estimated residual value
                    </div>
                  )}
                </div>
              )}
              <div className="flex justify-between pt-4 border-t border-line/10">
                <button onClick={() => setStep('diagnosed')} className="px-5 py-2.5 bg-raised text-xs rounded-xl">Back</button>
                <button onClick={() => setStep('recommendations')} className="px-5 py-2.5 bg-purple-600 text-xs rounded-xl text-white">Recommended Upgrades →</button>
              </div>
            </motion.div>
          )}

          {/* STEP 5: RECOMMENDATIONS */}
          {step === 'recommendations' && result && (
            <motion.div id="diagnosis-option-panel" onAnimationComplete={() => document.getElementById('diagnosis-option-panel')?.scrollIntoView({ block: 'start' })} key="recommendations" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-surface/70 backdrop-blur-xl border border-line/10 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl">
              
              {/* TOPIC HEADER */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-line/10 pb-5">
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-ink-400 shadow-[0_0_15px_rgba(6,182,212,0.25)]">
                      <Sparkles className="w-5 h-5" />
                    </span>
                    <h2 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
                      Recommended Phone Upgrades
                    </h2>
                  </div>
                  <p className="text-xs sm:text-sm text-ink-300 mt-1.5 leading-relaxed">
                    Curated smartphone replacements matched against your current device&apos;s repair cost, performance profile, and budget.
                  </p>
                </div>
                <button 
                  onClick={() => setStep('diagnosed')} 
                  className="self-start sm:self-center px-4 py-2 bg-raised/80 hover:bg-hover/80 border border-line/10 text-xs font-semibold text-ink-300 rounded-xl transition-all shadow-sm"
                >
                  ← Back to Diagnosis
                </button>
              </div>

              {/* INTERACTIVE FILTERS & SORTING CONTROLS */}
              <div className="bg-inset/70 border border-line/10 rounded-2xl p-4 sm:p-5 space-y-4 shadow-inner">
                {/* Row 1: Search Input & Brand Filter Pills */}
                <div className="flex flex-col md:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 text-ink-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search upgrades by name (e.g. Pixel, iPhone, Pro)..."
                      className="w-full bg-surface/90 border border-line/10 rounded-xl pl-10 pr-8 py-2 text-xs sm:text-sm text-foreground placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 transition-colors"
                    />
                    {searchQuery && (
                      <button
                        onClick={() => setSearchQuery('')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-400 hover:text-foreground"
                        title="Clear search"
                      >
                        ✕
                      </button>
                    )}
                  </div>

                  {/* Brand Pills */}
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
                    <span className="text-[11px] uppercase font-bold text-ink-400 shrink-0 mr-1 flex items-center gap-1">
                      <Filter className="w-3 h-3" /> Brand:
                    </span>
                    {availableBrands.map((b) => {
                      const isSelected = filterBrand === b;
                      return (
                        <button
                          key={b}
                          onClick={() => setFilterBrand(b)}
                          className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-all shrink-0 ${
                            isSelected
                              ? 'bg-cyan-500/20 text-cyan-ink-300 border-cyan-500/60 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                              : 'bg-surface/60 text-ink-400 border-line/5 hover:border-line/20 hover:text-ink-200'
                          }`}
                        >
                          {b}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Row 2: Sort, Max Budget & Feature Toggles */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-line/5">
                  {/* Sort Selector */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] uppercase font-bold text-ink-400 flex items-center gap-1">
                      <ArrowUpDown className="w-3 h-3 text-cyan-ink-400" /> Sort By
                    </label>
                    <div className="relative">
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as any)}
                        className="w-full bg-surface border border-line/10 rounded-xl px-3 py-2 text-xs text-foreground appearance-none focus:outline-none focus:border-cyan-500/50 cursor-pointer"
                      >
                        <option value="match">Best Overall Fit (Match Score)</option>
                        <option value="price_asc">Price: Low to High</option>
                        <option value="price_desc">Price: High to Low</option>
                        <option value="performance">Highest Performance</option>
                        <option value="battery">Best Battery Life</option>
                        <option value="camera">Best Camera Score</option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-ink-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  {/* Max Budget Selector */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] uppercase font-bold text-ink-400 flex items-center gap-1">
                      <SlidersHorizontal className="w-3 h-3 text-cyan-ink-400" /> Max Budget (LKR)
                    </label>
                    <div className="relative">
                      <select
                        value={maxBudget ?? 'all'}
                        onChange={(e) => setMaxBudget(e.target.value === 'all' ? null : Number(e.target.value))}
                        className="w-full bg-surface border border-line/10 rounded-xl px-3 py-2 text-xs text-foreground appearance-none focus:outline-none focus:border-cyan-500/50 cursor-pointer"
                      >
                        <option value="all">Any Price Range</option>
                        <option value="90000">Under LKR 90,000</option>
                        <option value="125000">Under LKR 125,000</option>
                        <option value="160000">Under LKR 160,000</option>
                        <option value="200000">Under LKR 200,000</option>
                      </select>
                      <ChevronDown className="w-3.5 h-3.5 text-ink-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  {/* Feature Toggles & Reset */}
                  <div className="sm:col-span-2 flex items-end gap-2 flex-wrap pt-1 sm:pt-0">
                    <button
                      onClick={() => setOnly5G(!only5G)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        only5G
                          ? 'bg-cyan-500/20 text-cyan-ink-300 border-cyan-500/60 shadow-[0_0_10px_rgba(6,182,212,0.25)]'
                          : 'bg-surface/60 text-ink-400 border-line/10 hover:border-line/20'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${only5G ? 'bg-cyan-400' : 'bg-slate-600'}`} />
                      5G Only
                    </button>

                    <button
                      onClick={() => setMinRam(minRam === 8 ? null : 8)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        minRam === 8
                          ? 'bg-cyan-500/20 text-cyan-ink-300 border-cyan-500/60 shadow-[0_0_10px_rgba(6,182,212,0.25)]'
                          : 'bg-surface/60 text-ink-400 border-line/10 hover:border-line/20'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${minRam === 8 ? 'bg-cyan-400' : 'bg-slate-600'}`} />
                      8 GB+ RAM
                    </button>

                    {(filterBrand !== 'All' || sortBy !== 'match' || maxBudget !== null || only5G || minRam !== null || searchQuery) && (
                      <button
                        onClick={() => {
                          setFilterBrand('All');
                          setSortBy('match');
                          setMaxBudget(null);
                          setOnly5G(false);
                          setMinRam(null);
                          setSearchQuery('');
                        }}
                        className="px-3 py-2 text-xs text-rose-ink-400 hover:text-rose-ink-300 flex items-center gap-1 font-semibold ml-auto transition-colors"
                      >
                        <RotateCcw className="w-3 h-3" /> Reset
                      </button>
                    )}
                  </div>
                </div>

                {/* Counter */}
                <div className="flex items-center justify-between text-xs text-ink-400 pt-2 border-t border-line/5 font-mono">
                  <span>
                    Showing <strong className="text-cyan-ink-400">{filteredRecommendations.length}</strong> of{' '}
                    <strong>{result.recommendations.length}</strong> recommended upgrades
                  </span>
                  {maxBudget && <span>Max: LKR {formatPrice.format(maxBudget)}</span>}
                </div>
              </div>

              {/* RECOMMENDATIONS CARDS */}
              <div className="flex flex-col gap-5">
                {filteredRecommendations.map((phone) => {
                  const photo = getPhoneImage(phone.name);
                  const brandName = phone.name.split(' ')[0] || 'Google';

                  return (
                    <div 
                      key={phone.id} 
                      className="group p-5 sm:p-6 bg-surface/90 border border-edge/60 hover:border-cyan-500/50 rounded-3xl transition-all duration-300 shadow-xl hover:shadow-[0_8px_30px_rgba(6,182,212,0.12)] flex flex-col sm:flex-row items-center sm:items-start gap-5 sm:gap-6"
                    >
                      {/* Device Image Box */}
                      <div className="w-32 h-32 sm:w-36 sm:h-36 shrink-0 bg-inset/80 border border-line/10 rounded-2xl p-2.5 flex items-center justify-center relative overflow-hidden group-hover:border-cyan-500/40 transition-colors shadow-inner">
                        {photo.isPhoto && photo.src ? (
                          <img 
                            src={photo.src} 
                            alt={phone.name} 
                            className="max-h-full max-w-full object-contain filter drop-shadow-[0_6px_12px_rgba(0,0,0,0.6)] group-hover:scale-105 transition-transform duration-300" 
                          />
                        ) : (
                          <div className="w-24 h-24 flex items-center justify-center">
                            <PhoneIllustration phone={{ brand: brandName } as any} className="size-full group-hover:scale-105 transition-transform duration-300" />
                          </div>
                        )}
                      </div>

                      {/* Device Details */}
                      <div className="flex-1 min-w-0 w-full space-y-4">
                        {/* Top Line: Name, Upgrade Verdict, Price & Match Score */}
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-line/5 pb-3">
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <h3 className="text-lg sm:text-xl font-bold text-foreground tracking-tight">{phone.name}</h3>
                              {phone.verdict_vs_old && (
                                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-ink-400 border border-emerald-500/30 uppercase tracking-wider">
                                  {phone.verdict_vs_old.replace(/_/g, ' ')}
                                </span>
                              )}
                            </div>
                            <p className="text-base sm:text-lg font-mono font-bold text-cyan-ink-400 mt-1">
                              {phone.price_lkr == null ? 'Price unavailable' : `LKR ${formatPrice.format(phone.price_lkr)}`}
                            </p>
                          </div>

                          {phone.score != null && (
                            <div className="self-start sm:self-auto shrink-0">
                              <span className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-bold font-mono px-3.5 py-1.5 rounded-xl bg-cyan-tint-950/80 text-cyan-ink-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                                {phone.score > 1 ? phone.score.toFixed(0) : (phone.score * 100).toFixed(0)}% Match
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Middle Line: Hardware Specifications Badges */}
                        {phone.product && (
                          <div className="flex flex-wrap gap-2 text-xs font-mono text-ink-200">
                            {phone.product.ram_gb && (
                              <span className="px-3 py-1 bg-inset/80 border border-edge/60 rounded-xl">
                                {phone.product.ram_gb} GB RAM
                              </span>
                            )}
                            {phone.product.storage_gb && (
                              <span className="px-3 py-1 bg-inset/80 border border-edge/60 rounded-xl">
                                {phone.product.storage_gb} GB Storage
                              </span>
                            )}
                            {phone.product.display_type && (
                              <span className="px-3 py-1 bg-inset/80 border border-edge/60 rounded-xl">
                                {phone.product.display_type}
                              </span>
                            )}
                            {phone.product.battery_mah && (
                              <span className="px-3 py-1 bg-inset/80 border border-edge/60 rounded-xl">
                                {phone.product.battery_mah} mAh
                              </span>
                            )}
                            {phone.product.has_5g && (
                              <span className="px-3 py-1 bg-inset/80 border border-cyan-500/30 text-cyan-ink-300 font-semibold rounded-xl">
                                5G Ready
                              </span>
                            )}
                          </div>
                        )}

                        {/* Bottom Line: Dimension Scores Laid Out Across 4 Clean Columns */}
                        {phone.dimensions && Object.keys(phone.dimensions).length > 0 && (
                          <div className="pt-2 border-t border-line/5 space-y-2">
                            <span className="text-[10px] uppercase font-bold tracking-wider text-ink-400">
                              Performance & Value Breakdown
                            </span>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
                              {Object.entries(phone.dimensions)
                                .filter(([k]) => ['performance', 'camera', 'battery', 'longevity'].includes(k))
                                .map(([dim, val]) => (
                                   <div key={dim} className="bg-inset/60 border border-line/5 rounded-xl p-2.5 space-y-1.5">
                                    <div className="flex justify-between items-center text-xs">
                                      <span className="capitalize text-ink-300 font-medium">{dim}</span>
                                      <span className="font-mono text-cyan-ink-300 font-bold text-[11px]">{(val * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="w-full bg-raised h-2 rounded-full overflow-hidden">
                                      <div 
                                        className="bg-gradient-to-r from-cyan-400 to-blue-500 h-full rounded-full transition-all" 
                                        style={{ width: `${Math.min(100, Math.max(0, val * 100))}%` }} 
                                      />
                                    </div>
                                  </div>
                                ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {filteredRecommendations.length === 0 && (
                  <div className="p-8 text-center bg-inset/40 border border-line/10 rounded-3xl space-y-3">
                    <p className="text-ink-300 text-sm font-medium">No upgrade recommendations match your selected filters.</p>
                    <button
                      onClick={() => {
                        setFilterBrand('All');
                        setSortBy('match');
                        setMaxBudget(null);
                        setOnly5G(false);
                        setMinRam(null);
                        setSearchQuery('');
                      }}
                      className="px-4 py-2 bg-cyan-600/30 hover:bg-cyan-600/50 border border-cyan-500/40 text-cyan-ink-300 text-xs font-semibold rounded-xl transition-all"
                    >
                      Clear All Filters
                    </button>
                  </div>
                )}
              </div>
              <div className="flex justify-between pt-4 border-t border-line/10">
                <button onClick={() => setStep('repair')} className="px-5 py-2.5 bg-raised text-xs rounded-xl">← Repair Cost</button>
                <button onClick={startNewDiagnosis} className="px-5 py-2.5 bg-cyan-600 text-xs rounded-xl text-white">Start New Diagnosis</button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      <ChatComposer
        intro={isIntro}
        value={query} onChange={setQuery} onSubmit={handleChatSubmit}
        image={selectedImage} onUpload={handleImageUpload} onRemoveImage={() => setSelectedImage(null)}
        loading={loading} confirming={step === 'confirm_device'} hasResult={Boolean(result)}
        view={step} onChooseOption={view => setStep(step === view ? 'diagnosed' : view)} error={step === 'confirm_device' ? '' : error}
      />
    </main>
  );
}
