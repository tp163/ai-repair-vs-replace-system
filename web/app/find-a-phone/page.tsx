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
    <main className="flex-1 bg-page bg-catalogue text-ink-100 ">
      <div className="mx-auto max-w-7xl px-4 pt-6 pb-14 sm:px-8 sm:pt-11 sm:pb-20">
        <nav aria-label="Breadcrumb" className="flex items-center gap-2.5 text-xs text-ink-400">
          <Link href="/" className="inline-flex items-center gap-1.5 hover:text-cyan-ink-200">
            <House className="size-3.5" aria-hidden="true" />
            Home
          </Link>
          <ChevronRight className="size-3 text-ink-500" aria-hidden="true" />
          <span aria-current="page" className="text-cyan-ink-300">Find a Phone</span>
        </nav>
        <h1 className="mt-3 text-3xl font-black tracking-tight text-foreground sm:text-4xl">
          Mobile <span className="bg-linear-to-r from-cyan-300 to-blue-500 bg-clip-text text-transparent">Phones</span>
        </h1>
        <PhoneCatalogue />
      </div>
    </main>
  );
}
