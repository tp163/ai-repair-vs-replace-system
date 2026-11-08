'use client';

import { useEffect, useRef, useState, type ReactNode } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ArrowLeft, ArrowRight, Check, ChevronLeft, ChevronRight, Pause, Play, Search, SlidersHorizontal, Smartphone } from 'lucide-react';
import { phones } from '@/lib/catalogue';
import type { Phone } from '@/lib/contracts';

const money = (value: number) => new Intl.NumberFormat('en-LK', { style: 'currency', currency: 'LKR', maximumFractionDigits: 0 }).format(value);
type Skin = { name: string; hex: string };
const skins: Record<string, Skin[]> = {
  'iphone-13-128': [{ name: 'Midnight', hex: '#303641' }, { name: 'Starlight', hex: '#ede9df' }, { name: 'Pink', hex: '#f1d6d2' }],
  'samsung-a55-128': [{ name: 'Navy', hex: '#323d56' }, { name: 'Ice blue', hex: '#c9dfeb' }, { name: 'Lilac', hex: '#cdc3de' }],
  'xiaomi-note13-256': [{ name: 'Black', hex: '#30353a' }, { name: 'White', hex: '#e7e8e9' }, { name: 'Green', hex: '#bddbd1' }],
  'poco-x6-256': [{ name: 'Black', hex: '#262a30' }, { name: 'Blue', hex: '#9bc9eb' }, { name: 'White', hex: '#ededeb' }],
  'pixel-8a-128': [{ name: 'Obsidian', hex: '#3d4241' }, { name: 'Porcelain', hex: '#e5e2da' }, { name: 'Bay', hex: '#8fb8eb' }, { name: 'Aloe', hex: '#b4d8ae' }],
};

function Reveal({ children, className = '' }: { children: ReactNode; className?: string }) {
  const reduced = useReducedMotion();
  return <motion.div className={className} initial={{ opacity: 0, y: reduced ? 0 : 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.08 }} transition={{ duration: reduced ? 0 : 0.55 }}>{children}</motion.div>;
}

// Skin previews are intentionally separate from original product photography.
// They show the selected finish without recolouring a manufacturer's photograph.
function SkinPreview({ phone, skin }: { phone: Phone; skin: Skin }) {
  return <div className={`skin-preview ${phone.brand.toLowerCase()}`} style={{ '--skin': skin.hex } as React.CSSProperties} role="img" aria-label={`${phone.model} ${skin.name} skin preview`}>
    <div className="skin-camera"><i /><i /><i /></div><span>{phone.brand === 'Apple' ? '●' : phone.brand === 'Google' ? 'G' : phone.brand}</span>
  </div>;
}

function Gallery({ phone, skin, showSkin = false, large = false, onOpen }: { phone: Phone; skin: Skin; showSkin?: boolean; large?: boolean; onOpen?: () => void }) {
  const reduced = useReducedMotion();
  const [slide, setSlide] = useState(0);
  const [paused, setPaused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [failed, setFailed] = useState<number[]>([]);
  const count = phone.id === 'samsung-a55-128' ? 2 : 3;
  useEffect(() => {
    if (reduced || paused || hovered || showSkin) return;
    const timer = window.setInterval(() => {
      if (!document.hidden && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        setSlide(current => current < count ? current + 1 : 1);
      }
    }, 3800);
    return () => window.clearInterval(timer);
  }, [reduced, paused, hovered, showSkin]);
  useEffect(() => {
    if (!resetting) return;
    const timer = window.setTimeout(() => setResetting(false), 40);
    return () => window.clearTimeout(timer);
  }, [resetting]);
  return <div className={`catalogue-gallery ${large ? 'large' : ''}`} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)} onFocusCapture={() => setHovered(true)} onBlurCapture={event => { if (!event.currentTarget.contains(event.relatedTarget)) setHovered(false); }} aria-label={`${phone.model} photo gallery`}>
    {showSkin ? <div className="skin-stage"><SkinPreview phone={phone} skin={skin} /><span>Skin preview · {skin.name}</span></div> : <div className="gallery-track" style={{ transform: `translateX(-${slide * 100}%)`, transition: resetting ? 'none' : undefined }} onTransitionEnd={() => { if (slide === count) { setResetting(true); setSlide(0); } }}>{Array.from({ length: count + 1 }, (_, offset) => { const index = offset % count; return <div className="gallery-frame" key={offset} aria-hidden={offset !== slide}>
      {failed.includes(index) ? <SkinPreview phone={phone} skin={skin} /> : <img src={`/phones/${phone.id}-${index + 1}.jpg`} alt={`${phone.brand} ${phone.model}, product view ${index + 1}`} loading={index === 0 ? 'eager' : 'lazy'} onError={() => setFailed(current => [...current, index])} />}
    </div>; })}</div>}
    {!showSkin && <div className="gallery-controls"><div className="gallery-dots">{Array.from({ length: count }, (_, index) => <button type="button" key={index} className={slide % count === index ? 'active' : ''} aria-label={`Show ${phone.model} photo ${index + 1}`} aria-pressed={slide % count === index} onClick={() => setSlide(index)} />)}</div><button type="button" className="gallery-play" onClick={() => setPaused(!paused)} aria-label={`${paused ? 'Play' : 'Pause'} ${phone.model} slideshow`}>{paused ? <Play size={12} /> : <Pause size={12} />}</button></div>}
    {onOpen && <button type="button" className="catalogue-photo-link" aria-label={`View full specifications for ${phone.model}`} onClick={onOpen} />}
    {large && !showSkin && <><button type="button" className="gallery-arrow previous" aria-label="Previous photo" onClick={() => setSlide((slide + count - 1) % count)}><ChevronLeft size={20} /></button><button type="button" className="gallery-arrow next" aria-label="Next photo" onClick={() => setSlide((slide + 1) % count)}><ChevronRight size={20} /></button></>}
  </div>;
}

function Colours({ phone, value, onChange }: { phone: Phone; value: number; onChange: (index: number) => void }) {
  return <div className="skin-options" role="group" aria-label={`${phone.model} skin colour`}>{skins[phone.id].map((skin, index) => <button type="button" key={skin.name} title={skin.name} aria-label={`${phone.model}: ${skin.name}`} aria-pressed={value === index} className={value === index ? 'selected' : ''} style={{ '--skin': skin.hex } as React.CSSProperties} onClick={() => onChange(index)}>{value === index && <Check size={12} />}</button>)}</div>;
}

function PhoneCard({ phone, open, compared, compare }: { phone: Phone; open: () => void; compared: boolean; compare: () => void }) {
  const [colour, setColour] = useState(0);
  const [showSkin, setShowSkin] = useState(false);
  return <article className="catalogue-card">
    <div className="catalogue-card-top"><span>{phone.has_5g ? '5G' : '4G'} · {phone.storage_gb} GB</span><button type="button" className={compared ? 'compare-toggle active' : 'compare-toggle'} aria-label={`${compared ? 'Remove' : 'Add'} ${phone.model} ${compared ? 'from' : 'to'} comparison`} aria-pressed={compared} onClick={compare}>{compared ? <Check size={15} /> : <span>+</span>}</button></div>
    <Gallery phone={phone} skin={skins[phone.id][colour]} showSkin={showSkin} onOpen={open} />
    <div className="catalogue-card-copy"><small>{phone.brand}</small><h2><button type="button" onClick={open}>{phone.model}</button></h2><p className="catalogue-price">{money(phone.price_lkr)}</p><Colours phone={phone} value={colour} onChange={index => { setColour(index); setShowSkin(true); }} />
    {showSkin && <button type="button" className="photo-reset" onClick={() => setShowSkin(false)}>View product photos</button>}
    <button type="button" className="catalogue-view" onClick={open}>Explore phone <ArrowRight size={15} /></button></div>
  </article>;
}

function Specs({ phone }: { phone: Phone }) {
  const groups: [string, [string, string][]][] = [
    ['Overview', [['Brand', phone.brand], ['Model', phone.model], ['Catalogue configuration', phone.variant], ['Release year', String(phone.release_year)], ['Operating system', phone.os]]],
    ['Display', [['Screen size', `${phone.display_size_in} inches`], ['Panel technology', phone.display_type], ['Refresh rate', `${phone.refresh_rate_hz} Hz`]]],
    ['Memory & performance', [['RAM', `${phone.ram_gb} GB`], ['Internal storage', `${phone.storage_gb} GB`], ['Performance tier', `${phone.chipset_tier} / 10 (catalogue rating)`]]],
    ['Camera & battery', [['Main camera', `${phone.camera_mp} MP`], ['Battery capacity', `${phone.battery_mah.toLocaleString()} mAh`]]],
    ['Connectivity & warranty', [['5G connectivity', phone.has_5g ? 'Supported' : 'Not supported'], ['Sample warranty', `${phone.warranty_months} months`], ['Sample catalogue price', money(phone.price_lkr)]]],
  ];
  return <section className="full-specifications"><div className="catalogue-section-heading"><span className="eyebrow">EVERY DETAIL, IN ONE PLACE</span><h2>Full catalogue specifications</h2><p>All specifications available for this catalogue configuration.</p></div>{groups.map(([title, rows]) => <Reveal key={title} className="spec-group"><h3>{title}</h3><dl>{rows.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></Reveal>)}</section>;
}

export default function PhoneCatalogue({ search, setSearch, budget, setBudget, compare, toggleCompare, diagnose }: { search: string; setSearch: (value: string) => void; budget: string; setBudget: (value: string) => void; compare: string[]; toggleCompare: (id: string) => void; diagnose: (id: string) => void }) {
  const [brand, setBrand] = useState('All');
  const [sort, setSort] = useState('featured');
  const [filters, setFilters] = useState(false);
  const [selected, setSelected] = useState<Phone>();
  const [colour, setColour] = useState(0);
  const [showSkin, setShowSkin] = useState(false);
  const title = useRef<HTMLHeadingElement>(null);
  const restoring = useRef(false);
  const scrollPosition = useRef(0);
  useEffect(() => {
    if (!restoring.current) return;
    title.current?.focus({ preventScroll: true });
    window.scrollTo({ top: selected ? 0 : scrollPosition.current, behavior: 'instant' });
    restoring.current = false;
  }, [selected]);
  const filtered = phones.filter(phone => (brand === 'All' || phone.brand === brand) && `${phone.brand} ${phone.model}`.toLowerCase().includes(search.toLowerCase()) && (!budget || phone.price_lkr <= Number(budget))).sort((a, b) => sort === 'low' ? a.price_lkr - b.price_lkr : sort === 'high' ? b.price_lkr - a.price_lkr : sort === 'name' ? a.model.localeCompare(b.model) : 0);
  function open(phone: Phone) { scrollPosition.current = window.scrollY; restoring.current = true; setColour(0); setShowSkin(false); setSelected(phone); }
  function close() { restoring.current = true; setSelected(undefined); }
  return <div className="phone-catalogue">
    <div className="catalogue-breadcrumb"><span>Home</span><ChevronRight size={13} /><button type="button" onClick={close}>Find a Phone</button>{selected && <><ChevronRight size={13} /><span>{selected.model}</span></>}</div>
    {selected ? <>
      <button type="button" className="catalogue-back" onClick={close}><ArrowLeft size={16} /> Back to all phones</button>
      <div className="phone-detail" key={selected.id}><div className="detail-visual"><Gallery phone={selected} skin={skins[selected.id][colour]} large showSkin={showSkin} /><p className="photo-credit">Product photography: GSMArena · Skin previews are illustrative.</p></div><div className="detail-copy"><span className="eyebrow">{selected.brand.toUpperCase()}</span><h1 tabIndex={-1} ref={title}>{selected.model}</h1><p className="detail-tagline">A closer look at your next phone.</p><span className="caption">Sample catalogue price</span><p className="detail-price">{money(selected.price_lkr)}</p><div className="detail-chips"><span>{selected.storage_gb} GB storage</span><span>{selected.ram_gb} GB RAM</span><span>{selected.has_5g ? '5G' : '4G'}</span></div><div className="detail-colour"><p>Skin colour <strong>{skins[selected.id][colour].name}</strong></p><Colours phone={selected} value={colour} onChange={index => { setColour(index); setShowSkin(true); }} />{showSkin && <button type="button" className="photo-reset" onClick={() => setShowSkin(false)}>View product photos</button>}</div><div className="detail-highlights"><span><strong>{selected.display_size_in}″</strong>{selected.display_type} display</span><span><strong>{selected.camera_mp} MP</strong>Main camera</span><span><strong>{selected.battery_mah.toLocaleString()}</strong>mAh battery</span></div><button type="button" className="catalogue-primary" onClick={() => toggleCompare(selected.id)}>{compare.includes(selected.id) ? 'Remove from comparison' : 'Add to comparison'} <ArrowRight size={16} /></button><button type="button" className="catalogue-secondary" onClick={() => diagnose(selected.id)}><Smartphone size={16} /> Diagnose this model</button><p className="catalogue-disclaimer">Sample catalogue. Confirm specifications, price, warranty, colours and availability with a seller before purchase.</p></div></div>
      <Specs phone={selected} />
    </> : <>
      <div className="catalogue-heading"><div><span className="eyebrow">FIND YOUR NEXT EVERYDAY ESSENTIAL</span><h1 tabIndex={-1} ref={title}>Find a Phone<span>.</span></h1><p>Explore the collection. Get to know every detail.</p></div><label className="catalogue-search"><Search size={18} /><input aria-label="Search catalogue" placeholder="Search by brand or model" value={search} onChange={event => setSearch(event.target.value)} /></label></div>
      <div className="catalogue-brands" role="group" aria-label="Filter phones by brand">{['All', ...new Set(phones.map(phone => phone.brand))].map(name => <button type="button" key={name} className={brand === name ? 'active' : ''} aria-pressed={brand === name} onClick={() => setBrand(name)}><span className={`brand-wordmark brand-${name.toLowerCase()}`}>{name === 'All' ? <Smartphone size={28} /> : name === 'Xiaomi' ? 'mi' : name === 'Google' ? 'Google' : name === 'Poco' ? 'POCO' : name}</span><small>{name === 'All' ? 'All phones' : name}</small></button>)}</div>
      <div className="catalogue-toolbar"><button type="button" className="catalogue-filter-toggle" aria-expanded={filters} aria-controls="catalogue-filters" onClick={() => setFilters(!filters)}><SlidersHorizontal size={15} />{filters ? 'Hide filters' : 'Show filters'}{budget && <span className="filter-indicator" />}</button><span aria-live="polite">{filtered.length} {filtered.length === 1 ? 'phone' : 'phones'}</span><label>Sort by<select aria-label="Sort phones" value={sort} onChange={event => setSort(event.target.value)}><option value="featured">Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option><option value="name">Name</option></select></label></div>
      {filters && <div className="catalogue-filter-panel" id="catalogue-filters"><label>Maximum budget (LKR)<input type="number" min="1" placeholder="Any budget" value={budget} onChange={event => setBudget(event.target.value)} /></label><button type="button" onClick={() => { setBudget(''); setBrand('All'); setSearch(''); }}>Reset filters</button></div>}
      <div className="catalogue-rows">{Array.from({ length: Math.ceil(filtered.length / 4) }, (_, row) => <Reveal className="catalogue-row" key={`${brand}-${search}-${budget}-${sort}-${row}`}>{filtered.slice(row * 4, row * 4 + 4).map(phone => <PhoneCard key={phone.id} phone={phone} open={() => open(phone)} compared={compare.includes(phone.id)} compare={() => toggleCompare(phone.id)} />)}</Reveal>)}</div>
      {!filtered.length && <div className="catalogue-empty"><Search size={30} /><h2>No phones found</h2><p>Try another model or adjust your filters.</p><button type="button" className="catalogue-secondary" onClick={() => { setSearch(''); setBudget(''); setBrand('All'); }}>Clear filters</button></div>}
      <p className="catalogue-disclaimer">Sample catalogue prices · Stock unverified · Select a phone to see its full catalogue specifications.</p>
    </>}
  </div>;
}
