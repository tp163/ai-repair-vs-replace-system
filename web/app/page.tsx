'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  motion,
  AnimatePresence,
} from 'framer-motion';
import {
  ChevronRight, ArrowRight,
  Shield, CheckCircle2, Battery, Plug, Thermometer,
  Stethoscope, DollarSign, Smartphone, Star, MapPin, MessageSquare,
  MonitorSmartphone, Volume2, VolumeX,
  Play, Pause, Sparkles, Maximize2, RotateCcw
} from 'lucide-react';

/* ─── VIDEO ASSET PATHS ─── */
const SYSTEM_INTRO_VIDEO_SRC = '/system-intro.mp4'; 
const HERO_BG_VIDEO_SRC = '/hero-bg.mp4';           

/* ─── STARRY NIGHT CANVAS BACKGROUND ─── */
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

    const numStars = 350;
    const stars = Array.from({ length: numStars }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 1.8 + 0.3,
      alpha: Math.random(),
      speedAlpha: Math.random() * 0.02 + 0.004,
      speedY: Math.random() * 0.1 + 0.02,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      const skyGradient = ctx.createLinearGradient(0, 0, width, height);
      skyGradient.addColorStop(0, '#04091a');
      skyGradient.addColorStop(0.5, '#07122b');
      skyGradient.addColorStop(1, '#02050f');
      ctx.fillStyle = skyGradient;
      ctx.fillRect(0, 0, width, height);

      ctx.save();
      ctx.translate(width / 2, height / 2);
      ctx.rotate((-30 * Math.PI) / 180);
      const milkyWay = ctx.createRadialGradient(0, 0, 50, 0, 0, Math.max(width, height) * 0.8);
      milkyWay.addColorStop(0, 'rgba(147, 112, 219, 0.15)');
      milkyWay.addColorStop(0.5, 'rgba(59, 130, 246, 0.08)');
      milkyWay.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = milkyWay;
      ctx.fillRect(-width, -height, width * 2, height * 2);
      ctx.restore();

      stars.forEach((star) => {
        star.alpha += star.speedAlpha;
        if (star.alpha > 1 || star.alpha < 0.2) star.speedAlpha = -star.speedAlpha;
        star.y += star.speedY;
        if (star.y > height) star.y = 0;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.globalAlpha = Math.max(0.1, Math.min(1, star.alpha));
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

/* ─── OPENING SYSTEM SHOWCASE VIDEO MODAL ─── */
function SystemIntroStage({
  isOpen,
  onFinish,
}: {
  isOpen: boolean;
  onFinish: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isMuted, setIsMuted] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      const vid = videoRef.current;
      if (vid) {
        vid.currentTime = 0;
        vid.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
      }
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleTimeUpdate = () => {
    const vid = videoRef.current;
    if (!vid || !vid.duration) return;
    setProgress((vid.currentTime / vid.duration) * 100);
  };

  const togglePlay = () => {
    const vid = videoRef.current;
    if (!vid) return;
    if (vid.paused) {
      vid.play();
      setIsPlaying(true);
    } else {
      vid.pause();
      setIsPlaying(false);
    }
  };

  const toggleMute = () => {
    const vid = videoRef.current;
    if (!vid) return;
    vid.muted = !vid.muted;
    setIsMuted(vid.muted);
  };

  const requestFullscreen = () => {
    const vid = videoRef.current;
    if (!vid) return;
    if (vid.requestFullscreen) {
      vid.requestFullscreen();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          key="system-intro-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 0.96, filter: 'blur(12px)' }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#030613]/90 backdrop-blur-2xl px-4 py-6 select-none overflow-hidden"
        >
          <motion.div
            animate={{
              scale: [1, 1.12, 1],
              opacity: [0.35, 0.55, 0.35],
              rotate: [0, 90, 0],
            }}
            transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute w-[520px] h-[520px] md:w-[760px] md:h-[420px] rounded-full bg-gradient-to-tr from-cyan-500/25 via-blue-600/20 to-purple-600/25 blur-3xl pointer-events-none"
          />

          <motion.div
            initial={{ y: -24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.15, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-10 flex items-center gap-3 mb-4"
          >
            <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-semibold uppercase tracking-widest text-cyan-300 bg-cyan-950/70 border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.2)]">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              REVIVAI System Architecture Overview
            </span>
          </motion.div>

          <motion.div
            initial={{ y: 30, scale: 0.92, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-10 w-full max-w-5xl rounded-3xl p-[1.5px] bg-gradient-to-b from-cyan-400/50 via-white/15 to-purple-500/40 shadow-[0_0_70px_rgba(6,182,212,0.2)]"
          >
            <div className="absolute -top-2 -left-2 w-6 h-6 border-t-2 border-l-2 border-cyan-400 rounded-tl-lg pointer-events-none" />
            <div className="absolute -top-2 -right-2 w-6 h-6 border-t-2 border-r-2 border-cyan-400 rounded-tr-lg pointer-events-none" />
            <div className="absolute -bottom-2 -left-2 w-6 h-6 border-b-2 border-l-2 border-purple-400 rounded-bl-lg pointer-events-none" />
            <div className="absolute -bottom-2 -right-2 w-6 h-6 border-b-2 border-r-2 border-purple-400 rounded-br-lg pointer-events-none" />

            <div className="relative w-full aspect-video max-h-[70vh] bg-[#02040a] rounded-[22px] overflow-hidden flex items-center justify-center">
              <video
                ref={videoRef}
                src={SYSTEM_INTRO_VIDEO_SRC}
                autoPlay
                muted={isMuted}
                playsInline
                preload="auto"
                onClick={togglePlay}
                onTimeUpdate={handleTimeUpdate}
                onEnded={onFinish}
                onError={onFinish}
                className="w-full h-full object-contain cursor-pointer"
              />

              <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1 rounded-full bg-black/50 backdrop-blur-md border border-white/10 text-[11px] font-mono text-slate-300 pointer-events-none">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                Multi-Agent Workflow Demo
              </div>

              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent pt-8 pb-3.5 px-5 flex flex-col gap-2.5">
                <div className="w-full h-1 bg-white/15 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <button
                      onClick={togglePlay}
                      aria-label={isPlaying ? 'Pause' : 'Play'}
                      className="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/15 flex items-center justify-center text-white transition-all"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white" />}
                    </button>

                    <button
                      onClick={toggleMute}
                      aria-label={isMuted ? 'Unmute' : 'Mute'}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/15 text-xs text-white transition-all"
                    >
                      {isMuted ? (
                        <>
                          <VolumeX className="w-3.5 h-3.5 text-rose-400" />
                          <span>Unmute Audio</span>
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Sound On</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={requestFullscreen}
                      title="Fullscreen"
                      className="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/15 flex items-center justify-center text-white/80 hover:text-white transition-all"
                    >
                      <Maximize2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <button
                    onClick={onFinish}
                    className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-bold text-white shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all"
                  >
                    Enter Platform <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.45 }}
            className="relative z-10 mt-4 text-xs text-slate-400 font-mono text-center"
          >
            Watch how our Diagnosis, Cost Analyst & Phone Match agents collaborate — or click <span className="text-cyan-400">Enter Platform</span> anytime.
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ─── STATIC HERO SECTION (NO FULL-PAGE SCROLL SCRUBBING) ─── */
function Hero({
  isSystemIntroActive,
  onOpenSystemVideo,
}: {
  isSystemIntroActive: boolean;
  onOpenSystemVideo: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const ambientVideoRef = useRef<HTMLVideoElement | null>(null);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    const vid = videoRef.current;
    const ambVid = ambientVideoRef.current;
    if (!vid) return;

    if (isSystemIntroActive) {
      vid.pause();
      if (ambVid) ambVid.pause();
      return;
    }

    vid.currentTime = 0;
    vid.play().catch(() => {});
    if (ambVid) {
      ambVid.currentTime = 0;
      ambVid.play().catch(() => {});
    }
  }, [isSystemIntroActive]);

  const toggleMute = () => {
    const vid = videoRef.current;
    if (!vid) return;
    vid.muted = !vid.muted;
    setIsMuted(vid.muted);
  };

  return (
    <section className="relative w-full h-[560px] overflow-hidden bg-[#040714] select-none z-20 flex items-center justify-center">
      {/* Softly Blurred Ambient Backdrop */}
      <video
        ref={ambientVideoRef}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        aria-hidden="true"
        className="absolute inset-0 w-full h-full object-cover object-center blur-2xl scale-110 opacity-35 pointer-events-none"
      >
        <source src={HERO_BG_VIDEO_SRC} type="video/mp4" />
      </video>

      {/* HERO VIDEO BANNER */}
      <video
        ref={videoRef}
        autoPlay
        muted={isMuted}
        loop
        playsInline
        preload="auto"
        className="absolute inset-0 w-full h-full object-contain md:object-right opacity-85 z-10 transition-all duration-700"
      >
        <source src={HERO_BG_VIDEO_SRC} type="video/mp4" />
      </video>

      {/* Readability Gradients */}
      <div className="absolute inset-0 z-10 bg-gradient-to-r from-[#06091a] via-[#06091a]/75 to-transparent pointer-events-none" />
      <div className="absolute bottom-0 left-0 right-0 h-24 z-10 bg-gradient-to-t from-[#070d1f] to-transparent pointer-events-none" />

      {/* Floating Audio Mute Control */}
      <div className="absolute bottom-6 right-6 z-30 flex items-center gap-2.5">
        <button
          onClick={toggleMute}
          aria-label={isMuted ? 'Unmute' : 'Mute'}
          className="w-9 h-9 rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-md border border-white/15 flex items-center justify-center text-white/80 hover:text-white transition-all"
        >
          {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
        </button>
      </div>

      {/* HERO CONTENT */}
      <div className="absolute inset-0 z-20 max-w-7xl mx-auto px-4 md:px-8 h-full flex items-center">
        <div className="max-w-xl">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
            Your Phone.<br />
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              A Smarter Next Move.
            </span>
          </h1>
          <p className="mt-4 text-slate-300 text-sm md:text-base leading-relaxed max-w-sm">
            AI agents work together to diagnose faults, estimate repair costs, and find the right replacement.
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Link
              href="/diagnose"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold rounded-full text-sm transition-all shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:shadow-[0_0_35px_rgba(6,182,212,0.6)] cursor-pointer"
            >
              Diagnose My Phone <ArrowRight className="w-4 h-4" />
            </Link>
            <button
              onClick={onOpenSystemVideo}
              className="inline-flex items-center gap-2 px-5 py-3 bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold rounded-full text-sm backdrop-blur-sm transition-all"
            >
              <Play className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" /> System Overview
            </button>
          </div>

          <div className="mt-7 flex flex-wrap gap-5 text-xs text-slate-400 font-mono">
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Multi-agent analysis</span>
            <span className="text-slate-600">|</span>
            <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-cyan-500" /> Sri Lankan prices</span>
            <span className="text-slate-600">|</span>
            <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-cyan-500" /> Clear recommendations</span>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─── ISSUE CARDS ─── */
const issues = [
  { icon: MonitorSmartphone, label: 'Cracked Screen', sub: 'Get advice & options', color: 'from-blue-600 to-cyan-500' },
  { icon: Battery,           label: 'Battery Problems', sub: 'Check solutions',     color: 'from-cyan-500 to-teal-500' },
  { icon: Plug,              label: 'Charging Issues', sub: 'Find the cause',       color: 'from-purple-600 to-blue-600' },
  { icon: Thermometer,       label: 'Slow or Overheating', sub: 'Get recommendations', color: 'from-rose-500 to-orange-500' },
];

function IssueCards() {
  return (
    <section className="w-full bg-[#070d1f] py-10 px-4 md:px-8 z-10 relative">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-white">Start with your phone fault</h2>
            <p className="text-xs text-slate-400 mt-0.5">Select a common problem to launch direct diagnosis</p>
          </div>
          <Link href="/diagnose" className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-mono">
            Go to Diagnose Page <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {issues.map((item) => (
            <Link
              key={item.label}
              href={`/diagnose?issue=${encodeURIComponent(item.label)}`}
              className="flex items-center gap-3 bg-slate-900/70 border border-white/8 rounded-2xl p-4 cursor-pointer hover:border-cyan-500/40 hover:bg-slate-900/90 transition-all group"
            >
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shrink-0 shadow-lg`}>
                <item.icon className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold text-white truncate">{item.label}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{item.sub}</div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors shrink-0" />
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── RECOMMENDED PHONES ─── */
const phones = [
  { name: 'Samsung Galaxy A15',   price: 'LKR 89,900',  display: '6.5"', ram: '6GB', storage: '128GB', tag: 'Budget Pick',   color: 'from-blue-600 to-purple-700' },
  { name: 'Xiaomi Redmi Note 13', price: 'LKR 124,900', display: '6.7"', ram: '6GB', storage: '256GB', tag: 'Best Value',    color: 'from-cyan-600 to-blue-700' },
  { name: 'Samsung Galaxy A55',   price: 'LKR 159,900', display: '6.7"', ram: '8GB', storage: '256GB', tag: 'Popular',       color: 'from-purple-600 to-pink-700' },
  { name: 'iPhone 15',            price: 'LKR 199,900', display: '6.8"', ram: '12GB', storage: '512GB', tag: 'Premium',      color: 'from-indigo-600 to-blue-700' },
];

function RecommendedPhones() {
  return (
    <section id="recommended" className="w-full bg-[#06091a] py-12 px-4 md:px-8 z-10 relative">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Recommended Phones</h2>
            <p className="text-xs text-slate-400 mt-1">Based on your budget and needs</p>
          </div>
          <Link href="/find-a-phone" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
            See all <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {phones.map((phone) => (
            <motion.div key={phone.name} whileHover={{ y: -4 }} className="bg-slate-900/70 border border-white/8 rounded-2xl p-4 flex flex-col gap-3 hover:border-cyan-500/40 transition-all">
              <div className={`w-full h-36 rounded-xl bg-gradient-to-br ${phone.color} flex items-center justify-center relative overflow-hidden`}>
                <span className="absolute top-2 right-2 text-[10px] font-bold bg-white/20 backdrop-blur-sm px-2 py-0.5 rounded-full text-white">{phone.tag}</span>
              </div>
              <div>
                <div className="text-lg font-black text-cyan-400">{phone.price}</div>
                <div className="text-xs font-semibold text-white mt-0.5 truncate">{phone.name}</div>
                <div className="mt-2 flex flex-wrap gap-x-3 text-[10px] text-slate-400">
                  <span>📱 {phone.display}</span>
                  <span>⚡ {phone.ram}</span>
                  <span>💾 {phone.storage}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── AGENT BANNER ─── */
const agents = [
  { icon: Stethoscope, name: 'Diagnosis Agent',    sub: 'Find the problem' },
  { icon: DollarSign,  name: 'Cost Analyst',       sub: 'Compare the cost' },
  { icon: Smartphone,  name: 'Phone Match Agents', sub: 'Find the best options' },
];

function AgentBanner() {
  return (
    <section id="agents" className="w-full bg-gradient-to-r from-[#06091a] via-[#0a1535] to-[#06091a] border-y border-white/5 py-10 px-4 md:px-8 z-10 relative">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-8">
        <div className="shrink-0 max-w-xs">
          <h2 className="text-2xl md:text-3xl font-black text-white leading-tight">
            Repair it. Replace it.{' '}
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Know why.</span>
          </h2>
          <div className="mt-4">
            <Link
              href="/diagnose"
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 border border-cyan-500/40 text-cyan-300 font-semibold rounded-full text-xs transition-all shadow-[0_0_15px_rgba(6,182,212,0.15)]"
            >
              Open Diagnostic Page <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
        <div className="hidden lg:block w-px h-20 bg-white/10" />
        <div className="flex-1 flex flex-col sm:flex-row items-center justify-around gap-6 w-full">
          {agents.map((a) => (
            <Link key={a.name} href="/diagnose" className="flex items-center gap-6 group cursor-pointer">
              <div className="flex flex-col items-center text-center gap-2">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.15)] group-hover:border-cyan-400 transition-all">
                  <a.icon className="w-6 h-6 text-cyan-400 group-hover:scale-110 transition-transform" />
                </div>
                <div>
                  <div className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">{a.name}</div>
                  <div className="text-[11px] text-slate-400">{a.sub}</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── TRUST BAR FOOTER ─── */
const trustItems = [
  { icon: Shield,        label: 'Repair cost clarity' },
  { icon: MapPin,        label: 'Local price context' },
  { icon: MessageSquare, label: 'Recommendations explained' },
  { icon: Star,          label: 'Your choice comes first' },
];

function TrustBar() {
  return (
    <div className="w-full bg-[#040810] border-t border-white/5 py-4 px-4 md:px-8 z-10 relative">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-center gap-6 md:gap-10">
        {trustItems.map((item) => (
          <span key={item.label} className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <item.icon className="w-3.5 h-3.5 text-cyan-500" />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── MAIN HOME PAGE ─── */
export default function HomePage() {
  const [showSystemIntro, setShowSystemIntro] = useState(true);

  return (
    <div className="flex flex-1 flex-col bg-[#06091a] text-slate-100 relative overflow-x-clip">
      <StarrySkyBackground />

      {/* Opening system video overlay */}
      <SystemIntroStage
        isOpen={showSystemIntro}
        onFinish={() => setShowSystemIntro(false)}
      />

      <Hero
        isSystemIntroActive={showSystemIntro}
        onOpenSystemVideo={() => setShowSystemIntro(true)}
      />

      <IssueCards />
      <RecommendedPhones />
      <AgentBanner />
      <TrustBar />
    </div>
  );
}
