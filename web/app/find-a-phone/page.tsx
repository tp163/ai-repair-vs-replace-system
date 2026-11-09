import type { Metadata } from 'next';
import Link from 'next/link';
import { ChevronRight, House } from 'lucide-react';
import PhoneCatalogue from './phone-catalogue';

export const metadata: Metadata = {
  title: 'Find a Phone | REVIVAI',
  description: 'Browse replacement phones, explore device specifications, and see catalogue prices in LKR.',
};

export default function FindAPhonePage() {
  return (
    <main className="flex-1 bg-[#06091a] bg-[radial-gradient(ellipse_at_top_right,#11234b_0%,transparent_42%),radial-gradient(ellipse_at_top_left,#0b2639_0%,transparent_34%)] text-slate-100 [color-scheme:dark]">
      <div className="mx-auto max-w-7xl px-4 pt-6 pb-14 sm:px-8 sm:pt-11 sm:pb-20">
        <nav aria-label="Breadcrumb" className="flex items-center gap-2.5 text-xs text-slate-400">
          <Link href="/" className="inline-flex items-center gap-1.5 hover:text-cyan-200">
            <House className="size-3.5" aria-hidden="true" />
            Home
          </Link>
          <ChevronRight className="size-3 text-slate-500" aria-hidden="true" />
          <span aria-current="page" className="text-cyan-300">Find a Phone</span>
        </nav>
        <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
          Mobile <span className="bg-linear-to-r from-cyan-300 to-blue-500 bg-clip-text text-transparent">Phones</span>
        </h1>
        <PhoneCatalogue />
      </div>
    </main>
  );
}
