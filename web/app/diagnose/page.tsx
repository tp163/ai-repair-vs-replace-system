'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Send, AlertTriangle, Smartphone, Zap } from 'lucide-react';

type DiagnosisResult = {
  diagnosis: {
    fault_category: string;
    probable_cause: string;
    confidence: string;
    uncertainty?: string;
    follow_up_questions?: string[];
  };
  safety_flags: { code: string; message: string }[];
  repair_cost: { min_lkr: number | null; max_lkr: number | null; note?: string } | null;
  recommendations: { id: string; name: string; price_lkr: number | null }[];
};

const formatPrice = new Intl.NumberFormat('en-LK', { maximumFractionDigits: 2 });

/* ---------------- DYNAMIC REALISTIC STARRY NIGHT CANVAS ---------------- */
function StarrySkyBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Create realistic stars matching the reference image density
    const numStars = 400;
    const stars = Array.from({ length: numStars }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 1.8 + 0.4,
      alpha: Math.random(),
      speedAlpha: Math.random() * 0.02 + 0.005,
      speedY: Math.random() * 0.15 + 0.05, // Subtle downward drifting star motion
      speedX: (Math.random() - 0.5) * 0.08,
      color: Math.random() > 0.85 ? '#a5f3fc' : Math.random() > 0.7 ? '#c4b5fd' : '#7dd3fc'
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Deep space night sky gradient background
      const skyGradient = ctx.createLinearGradient(0, 0, width, height);
      skyGradient.addColorStop(0, '#04091a');
      skyGradient.addColorStop(0.5, '#07122b');
      skyGradient.addColorStop(1, '#02050f');
      ctx.fillStyle = skyGradient;
      ctx.fillRect(0, 0, width, height);

      // Diagonal Milky Way dust glow band (matching reference image angle)
      ctx.save();
      ctx.translate(width / 2, height / 2);
      ctx.rotate((-35 * Math.PI) / 180);
      const milkyWayGradient = ctx.createRadialGradient(0, 0, 50, 0, 0, Math.max(width, height) * 0.7);
      milkyWayGradient.addColorStop(0, 'rgba(147, 112, 219, 0.18)');
      milkyWayGradient.addColorStop(0.4, 'rgba(70, 130, 180, 0.12)');
      milkyWayGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = milkyWayGradient;
      ctx.fillRect(-width, -height, width * 2, height * 2);
      ctx.restore();

      // Render & update moving twinkling stars
      stars.forEach((star) => {
        // Twinkle effect
        star.alpha += star.speedAlpha;
        if (star.alpha > 1 || star.alpha < 0.2) {
          star.speedAlpha = -star.speedAlpha;
        }

        // Drifting motion
        star.y += star.speedY;
        star.x += star.speedX;

        // Wrap around screen edges
        if (star.y > height) star.y = 0;
        if (star.x > width) star.x = 0;
        if (star.x < 0) star.x = width;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = star.color;
        ctx.globalAlpha = Math.max(0.1, Math.min(1, star.alpha));
        ctx.shadowBlur = star.size > 1.4 ? 8 : 0;
        ctx.shadowColor = star.color;
        ctx.fill();
        ctx.globalAlpha = 1;
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-0" />;
}

export default function Home() {
  const [step, setStep] = useState<'input' | 'confirm_device' | 'diagnosed' | 'repair' | 'recommendations'>('input');
  
  const [query, setQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [variant, setVariant] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const issue = params.get('issue');
      if (issue) {
        setQuery(`Issue: ${issue}. `);
      }
    }
  }, []);

  const handleInitialSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && !selectedImage) return;
    setError('');
    setStep('confirm_device');
  };

  const handleConfirmDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, brand, model, variant, image_data_uri: selectedImage }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data?.diagnosis) {
        const message = data?.error ?? data?.detail;
        throw new Error(typeof message === 'string' ? message : 'Diagnosis failed. Check your details and try again.');
      }
      setResult(data);
      setStep('diagnosed');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Diagnosis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const image = e.target.files?.[0];
    if (!image) return;
    const reader = new FileReader();
    reader.onload = () => setSelectedImage(String(reader.result));
    reader.readAsDataURL(image);
  };

  const startNewDiagnosis = () => {
    setQuery('');
    setSelectedImage(null);
    setBrand('');
    setModel('');
    setVariant('');
    setResult(null);
    setStep('input');
  };

  return (
    <main className="flex flex-1 flex-col items-center justify-between p-4 md:p-8 relative overflow-hidden text-slate-100 selection:bg-cyan-500 selection:text-white">
      
      {/* REALISTIC NIGHT SKY BACKGROUND WITH MOVING STARS */}
      <StarrySkyBackground />

      <div className="z-10 mb-6 flex w-full max-w-5xl justify-end">
        <div className="text-xs text-slate-300 font-mono bg-slate-950/80 px-3.5 py-1.5 rounded-full border border-cyan-500/30 backdrop-blur-md flex items-center gap-2 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          System Status: <span className="text-emerald-400 font-bold">Online</span>
        </div>
      </div>

      {/* MAIN DIAGNOSTIC WORKFLOW CONTAINER */}
      <div className="w-full max-w-3xl z-10 flex-1 flex flex-col justify-center">
        <AnimatePresence mode="wait">
          
          {/* STEP 1: INPUT */}
          {step === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              <div className="text-center space-y-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-500/40 rounded-full uppercase backdrop-blur-md shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                  <Zap className="w-3.5 h-3.5" /> AI Fault Detection & Recovery
                </span>
                <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white drop-shadow-[0_4px_20px_rgba(0,0,0,0.8)]">
                  Diagnose. Repair. <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">Evolve.</span>
                </h1>
                <p className="text-slate-300 text-sm md:text-base max-w-xl mx-auto leading-relaxed drop-shadow">
                  Describe your phone issue or upload a photo for diagnosis, repair estimates, and replacement recommendations. Photo analysis requires an image-capable model on the backend.
                </p>
              </div>

              <div className="bg-slate-900/65 backdrop-blur-xl border border-white/10 rounded-3xl p-6 md:p-8 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
                <form onSubmit={handleInitialSubmit} className="space-y-6">
                  
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Smartphone className="w-4 h-4 text-cyan-400" /> State your phone issue or symptoms
                    </label>
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="e.g., My phone screen cracked after a fall, display shows flickering green lines..."
                      className="w-full h-36 bg-slate-950/70 border border-white/10 rounded-2xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 transition-all resize-none text-sm"
                      required={!selectedImage}
                    />
                  </div>

                  {selectedImage && (
                    <div className="relative w-24 h-24 rounded-xl overflow-hidden border border-cyan-500/50 shadow-md">
                      <img src={selectedImage} alt="Uploaded fault" className="w-full h-full object-cover" />
                      <button 
                        type="button" 
                        onClick={() => setSelectedImage(null)}
                        className="absolute top-1 right-1 bg-black/70 rounded-full w-5 h-5 flex items-center justify-center text-xs text-white"
                      >
                        ✕
                      </button>
                    </div>
                  )}

                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <label className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-5 py-3.5 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-2xl cursor-pointer text-xs font-medium text-slate-300 hover:text-white transition-all backdrop-blur-sm">
                      <Upload className="w-4 h-4 text-cyan-400" />
                      <span>{selectedImage ? 'Change Image' : 'Upload Fault Image'}</span>
                      <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                    </label>

                    <button
                      type="submit"
                      className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-2xl transition-all shadow-[0_0_25px_rgba(6,182,212,0.3)] text-xs uppercase tracking-wider disabled:opacity-50"
                    >
                      <span>Continue to Device Details</span>
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          )}

          {/* STEP 2: CONFIRM DEVICE */}
          {step === 'confirm_device' && (
            <motion.div
              key="confirm_device"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="bg-slate-900/70 backdrop-blur-xl border border-cyan-500/30 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl"
            >
              <div className="border-b border-white/10 pb-4">
                <span className="text-xs text-cyan-400 font-mono uppercase tracking-wider">Step 2: Confirm Device Details</span>
                <h2 className="text-2xl font-bold text-white mt-1">Verify Your Phone Model</h2>
              </div>

              <form onSubmit={handleConfirmDevice} className="space-y-4">
                <fieldset disabled={loading} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs text-slate-300 font-semibold">Brand</label>
                    <input type="text" value={brand} onChange={(e) => setBrand(e.target.value)} className="w-full bg-slate-950/70 border border-white/10 rounded-xl px-3 py-2 text-xs text-white" required />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-slate-300 font-semibold">Model Name</label>
                    <input type="text" value={model} onChange={(e) => setModel(e.target.value)} className="w-full bg-slate-950/70 border border-white/10 rounded-xl px-3 py-2 text-xs text-white" required />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-slate-300 font-semibold">Variant</label>
                    <input type="text" value={variant} onChange={(e) => setVariant(e.target.value)} className="w-full bg-slate-950/70 border border-white/10 rounded-xl px-3 py-2 text-xs text-white" />
                  </div>
                </fieldset>

                {error && <p role="alert" className="text-sm text-rose-300">{error}</p>}

                <div className="pt-4 flex justify-between items-center">
                  <button type="button" disabled={loading} onClick={() => setStep('input')} className="text-xs text-slate-400 underline disabled:opacity-50">← Back</button>
                  <button type="submit" disabled={loading} className="px-6 py-3 bg-cyan-600 text-white font-semibold rounded-xl text-xs uppercase disabled:opacity-50">
                    {loading ? 'Running Diagnosis…' : 'Confirm & Run Diagnosis'}
                  </button>
                </div>
              </form>
            </motion.div>
          )}

          {/* STEP 3: DIAGNOSED RESULT */}
          {step === 'diagnosed' && result && (
            <motion.div
              key="diagnosed"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900/70 backdrop-blur-xl border border-white/10 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-white/10 pb-5">
                <div>
                  <span className="text-[11px] text-emerald-400 font-semibold uppercase bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/40">Diagnosis Complete</span>
                  <h2 className="text-2xl font-bold mt-2 text-white">{brand} {model}{variant && ` (${variant})`}</h2>
                </div>
                <button onClick={startNewDiagnosis} className="text-xs text-slate-400 underline">Start Over</button>
              </div>

              <div className="space-y-2">
                <h3 className="text-lg font-semibold capitalize">{result.diagnosis.fault_category.replace(/_/g, ' ')}</h3>
                <p className="text-sm text-slate-200">{result.diagnosis.probable_cause}</p>
                <p className="text-xs text-slate-400">Confidence: {result.diagnosis.confidence}</p>
                {result.diagnosis.uncertainty && <p className="text-xs text-slate-400">{result.diagnosis.uncertainty}</p>}
                {result.diagnosis.follow_up_questions?.map((question) => (
                  <p key={question} className="text-sm text-slate-300">{question}</p>
                ))}
              </div>

              {result.safety_flags.length > 0 && (
                <div className="bg-amber-950/30 border border-amber-800/40 rounded-2xl p-4 flex items-start gap-3.5">
                  <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-xs font-bold uppercase text-amber-300">Safety Warnings</h4>
                    {result.safety_flags.map((flag) => (
                      <p key={flag.code} className="text-xs text-amber-200/80 mt-1">{flag.message}</p>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-2 border-t border-white/10 space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <button onClick={() => setStep('repair')} className="p-4 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-2xl text-left">
                    <span className="text-xs text-cyan-400 font-bold">Option A</span>
                    <h5 className="text-sm font-bold text-white mt-1">Check Repair Cost</h5>
                  </button>
                  <button onClick={() => setStep('recommendations')} className="p-4 bg-purple-900/40 hover:bg-purple-900/60 border border-purple-500/30 rounded-2xl text-left">
                    <span className="text-xs text-purple-400 font-bold">Option B</span>
                    <h5 className="text-sm font-bold text-white mt-1">Explore Replacement (Multi-Agent)</h5>
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 4: REPAIR COST */}
          {step === 'repair' && result && (
            <motion.div key="repair" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900/70 backdrop-blur-xl border border-white/10 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <h2 className="text-2xl font-bold text-white">Repair Cost Analysis</h2>
                <button onClick={() => setStep('diagnosed')} className="text-xs text-slate-400 underline">← Back</button>
              </div>
              <div className="bg-slate-950/80 border border-cyan-500/30 rounded-2xl p-6 text-center space-y-3">
                {result.repair_cost?.min_lkr != null && result.repair_cost.max_lkr != null ? (
                  <div className="text-3xl md:text-4xl font-black text-cyan-400 font-mono">
                    LKR {formatPrice.format(result.repair_cost.min_lkr)} – {formatPrice.format(result.repair_cost.max_lkr)}
                  </div>
                ) : (
                  <p className="text-sm text-slate-300">No repair estimate is available for this device and issue.</p>
                )}
                {result.repair_cost?.note && <p className="text-xs text-slate-400">{result.repair_cost.note}</p>}
              </div>
              <div className="flex justify-between pt-4 border-t border-white/10">
                <button onClick={() => setStep('diagnosed')} className="px-5 py-2.5 bg-slate-800 text-xs rounded-xl">Back</button>
                <button onClick={() => setStep('recommendations')} className="px-5 py-2.5 bg-purple-600 text-xs rounded-xl text-white">Replacement Options →</button>
              </div>
            </motion.div>
          )}

          {/* STEP 5: RECOMMENDATIONS */}
          {step === 'recommendations' && result && (
            <motion.div key="recommendations" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900/70 backdrop-blur-xl border border-white/10 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <h2 className="text-2xl font-bold text-white">Multi-Agent Recommendations</h2>
                <button onClick={() => setStep('diagnosed')} className="text-xs text-slate-400 underline">← Back</button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {result.recommendations.map((phone) => (
                  <div key={phone.id} className="p-4 bg-slate-950/60 border border-white/5 rounded-2xl">
                    <h4 className="text-sm font-bold text-white">{phone.name}</h4>
                    <p className="text-[11px] text-slate-400 mt-1">
                      {phone.price_lkr == null ? 'Price unavailable' : `LKR ${formatPrice.format(phone.price_lkr)}`}
                    </p>
                  </div>
                ))}
                {result.recommendations.length === 0 && <p className="text-sm text-slate-300">No replacements found in the catalogue.</p>}
              </div>
              <div className="flex justify-between pt-4 border-t border-white/10">
                <button onClick={() => setStep('repair')} className="px-5 py-2.5 bg-slate-800 text-xs rounded-xl">← Repair Cost</button>
                <button onClick={startNewDiagnosis} className="px-5 py-2.5 bg-cyan-600 text-xs rounded-xl text-white">Start New Diagnosis</button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      <footer className="w-full max-w-5xl text-center py-6 border-t border-white/5 text-[11px] text-slate-500 mt-12 z-10 backdrop-blur-sm">
        REVIVAI Multi-Agent Research Preview • Sri Lankan Market Intelligence Layer[cite: 1]
      </footer>
    </main>
  );
}
