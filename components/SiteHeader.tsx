'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Cpu, Heart, Search, Stethoscope, User, Zap } from 'lucide-react';

const links = [
  { name: 'Home', href: '/' },
  { name: 'Find a Phone', href: '/find-a-phone' },
  { name: 'How It Works', href: '/how-it-works' },
];

export default function SiteHeader() {
  const pathname = usePathname();

  return (
    <>
      <div className="z-40 flex w-full items-center justify-center gap-6 bg-gradient-to-r from-blue-700 via-cyan-600 to-blue-700 px-4 py-2 font-mono text-xs text-white">
        <span className="flex items-center gap-1.5">
          <Zap className="size-3.5 shrink-0 text-cyan-200" aria-hidden="true" />
          Smarter Decisions, Longer Life for Your Device.
        </span>
        <span className="hidden text-cyan-300 md:block" aria-hidden="true">|</span>
        <span className="hidden items-center gap-1.5 md:flex">
          <Cpu className="size-3.5 text-cyan-200" aria-hidden="true" />
          Powered by Multi-Agent AI Technology
        </span>
      </div>
      <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#070d1f]/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-2 px-4 md:gap-x-4 md:px-8 lg:flex-nowrap">
          <Link href="/" className="group flex h-14 shrink-0 items-center gap-3">
            <Image
              src="/revivai-logo.png"
              alt="REVIVAI home"
              width={142}
              height={36}
              loading="eager"
              className="h-8 w-[126px] object-contain drop-shadow-[0_0_16px_rgba(6,182,212,0.35)] transition-transform group-hover:scale-105 md:h-9 md:w-[142px]"
            />
            <span className="hidden border-l border-white/10 pl-2.5 font-mono text-[9px] tracking-widest text-slate-400 uppercase xl:block">
              Repair · Replace · Recommend
            </span>
          </Link>

          <label className="relative hidden min-w-0 max-w-xs flex-1 md:block">
            <span className="sr-only">Search for phone models</span>
            <Search className="pointer-events-none absolute top-1/2 left-3 size-3.5 -translate-y-1/2 text-slate-500" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search for phone models..."
              className="w-full rounded-full border border-white/10 bg-slate-800/60 py-2 pr-4 pl-9 text-xs text-slate-300 transition-colors placeholder:text-slate-500 focus:border-cyan-500/50 focus:outline-none"
            />
          </label>

          <nav aria-label="Main navigation" className="order-last flex w-full items-center justify-center gap-6 border-t border-white/5 py-2 text-xs font-medium lg:order-none lg:w-auto lg:shrink-0 lg:border-0">
            {links.map(({ name, href }) => {
              const current = pathname === href ? 'page' : pathname.startsWith(`${href}/`) ? 'location' : undefined;
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={current}
                  className={`border-b-2 pb-0.5 transition-colors ${current ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:border-white/30 hover:text-white'}`}
                >
                  {name}
                </Link>
              );
            })}
          </nav>

          <div className="ml-auto flex shrink-0 items-center gap-2 text-slate-400 sm:gap-3">
            <Link
              href="/diagnose"
              aria-current={pathname === '/diagnose' ? 'page' : undefined}
              className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1.5 text-xs font-semibold text-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-colors hover:bg-cyan-500/20 sm:px-3.5"
            >
              <Stethoscope className="size-3.5" aria-hidden="true" /> Diagnose
            </Link>
            <button type="button" aria-label="Account" className="transition-colors hover:text-white"><User size={18} aria-hidden="true" /></button>
            <button type="button" aria-label="Saved phones" className="transition-colors hover:text-white"><Heart size={18} aria-hidden="true" /></button>
          </div>
        </div>
      </header>
    </>
  );
}
