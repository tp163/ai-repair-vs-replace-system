'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Search, SlidersHorizontal, Smartphone } from 'lucide-react';
import { formatPrice, phones } from './catalogue-data';
import PhoneIllustration from './phone-illustration';

const brands = [...new Set(phones.map((phone) => phone.brand))];
const brandStyles: Record<string, string> = {
  Apple: 'text-slate-100',
  Samsung: 'text-blue-300 uppercase tracking-tight',
  Xiaomi: 'text-orange-300',
  Google: 'text-sky-300',
  Poco: 'text-amber-300 uppercase',
};

export default function PhoneCatalogue() {
  const [brand, setBrand] = useState('');
  const [search, setSearch] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sort, setSort] = useState('featured');
  const [showFilters, setShowFilters] = useState(false);
  const terms = search.trim().toLowerCase().split(/\s+/);
  const results = phones.filter((phone) => {
    const text = `${phone.brand} ${phone.model} ${phone.variant}`.toLowerCase();
    return (!brand || phone.brand === brand)
      && (!maxPrice || phone.price_lkr <= Number(maxPrice))
      && terms.every((term) => text.includes(term));
  });
  if (sort === 'lowest') results.sort((first, second) => first.price_lkr - second.price_lkr);
  if (sort === 'highest') results.sort((first, second) => second.price_lkr - first.price_lkr);

  function clearFilters() {
    setBrand('');
    setSearch('');
    setMaxPrice('');
  }

  return (
    <>
      <div role="group" aria-label="Filter phones by brand" className="mt-7 flex gap-3 overflow-x-auto px-0.5 pb-2 sm:gap-4">
        {['', ...brands].map((name) => (
          <button
            key={name}
            type="button"
            aria-pressed={brand === name}
            onClick={() => setBrand(name)}
            className="group w-27 shrink-0 cursor-pointer rounded-xl text-center focus-visible:outline-2 focus-visible:outline-cyan-300 sm:w-33 lg:min-w-0 lg:flex-1"
          >
            <span className={`flex h-20 items-center justify-center rounded-xl border transition-colors sm:h-24 ${brand === name ? 'border-cyan-400/60 bg-linear-to-br from-cyan-500/20 to-blue-600/20 shadow-[inset_0_0_24px_rgba(6,182,212,0.12)]' : 'border-white/10 bg-slate-900/85 group-hover:border-cyan-400/45'}`}>
              {name ? (
                <span aria-hidden="true" className={`text-base font-black sm:text-lg ${brandStyles[name] ?? 'text-slate-100'}`}>{name}</span>
              ) : (
                <Smartphone className="size-7 text-cyan-300" aria-hidden="true" />
              )}
            </span>
            <span className={`mt-2.5 block text-xs font-semibold ${brand === name ? 'text-cyan-200' : 'text-slate-300'}`}>{name || 'All phones'}</span>
          </button>
        ))}
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-x-5 gap-y-3">
        <div className="flex flex-wrap items-center gap-3 sm:gap-5">
          <button
            type="button"
            aria-expanded={showFilters}
            aria-controls="phone-filters"
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 text-sm font-semibold text-cyan-200 hover:bg-cyan-500/20"
          >
            <SlidersHorizontal className="size-4" aria-hidden="true" />
            {showFilters ? 'Hide filters' : 'Show filters'}
          </button>
          <p role="status" className="text-sm text-slate-400">
            {results.length} {results.length === 1 ? 'phone' : 'phones'}
          </p>
          {(brand || search || maxPrice) && (
            <button type="button" onClick={clearFilters} className="cursor-pointer text-sm text-cyan-300 underline underline-offset-4 hover:text-cyan-100">
              Clear filters
            </button>
          )}
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-400">
          Sort by
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value)}
            className="min-h-10 cursor-pointer rounded-full border border-white/15 bg-slate-900 px-3 text-sm font-medium text-slate-100 hover:border-cyan-500/40"
          >
            <option value="featured">Featured</option>
            <option value="lowest">Price: low to high</option>
            <option value="highest">Price: high to low</option>
          </select>
        </label>
      </div>

      <div id="phone-filters" hidden={!showFilters} className="mt-4 rounded-xl border border-white/10 bg-slate-900/85 p-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-medium text-slate-200">
            Search phones
            <span className="relative mt-1.5 block">
              <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-500" aria-hidden="true" />
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Brand, model, or storage"
                className="w-full rounded-lg border border-white/15 bg-slate-950/65 py-2.5 pr-3 pl-9 text-slate-100 placeholder:text-slate-400 focus-visible:outline-2 focus-visible:outline-cyan-400"
              />
            </span>
          </label>
          <label className="text-sm font-medium text-slate-200">
            Maximum price (LKR)
            <input
              type="number"
              min={0}
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value)}
              placeholder="Any price"
              className="mt-1.5 block w-full rounded-lg border border-white/15 bg-slate-950/65 px-3 py-2.5 text-slate-100 placeholder:text-slate-400 focus-visible:outline-2 focus-visible:outline-cyan-400"
            />
          </label>
        </div>
      </div>

      {results.length > 0 ? (
        <ul aria-label="Phones" className="mt-6 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          {results.map((phone) => (
            <li key={phone.id} className="min-w-0">
              <Link
                href={`/find-a-phone/${phone.id}`}
                className="group block h-full rounded-2xl border border-white/10 bg-slate-900/85 px-2 pt-4 pb-5 text-center transition-[border-color,box-shadow] hover:border-cyan-400/45 hover:shadow-[0_0_24px_rgba(6,182,212,0.12)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 sm:px-4 sm:pt-6 sm:pb-7"
              >
                <div className="mx-auto flex aspect-square w-full max-w-[14rem] items-center justify-center bg-[radial-gradient(ellipse_at_center,#233a65_0%,transparent_73%)] sm:p-2">
                  <PhoneIllustration phone={phone} className="size-full transition-transform group-hover:scale-105 motion-reduce:transition-none" />
                </div>
                <div className="mt-3 sm:mt-5">
                  <p className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">{phone.brand}</p>
                  <h2 className="mt-1.5 text-sm font-semibold leading-snug text-white sm:text-base">{phone.model}</h2>
                  <p className="mt-1.5 text-xs font-bold text-cyan-300 sm:text-sm">{formatPrice(phone.price_lkr)}</p>
                  <p className="mt-2 inline-block rounded-md border border-white/15 bg-slate-950/45 px-2 py-1 text-[10px] font-medium text-slate-300">
                    {phone.storage_gb} GB{phone.has_5g ? ' · 5G' : ''}
                  </p>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-6 rounded-xl border border-white/10 bg-slate-900/85 px-5 py-12 text-center text-sm text-slate-300">
          No phones match these filters.
        </p>
      )}
      <p className="mt-5 text-xs text-slate-400">Sample catalogue prices in LKR. Device images in this grid are illustrations.</p>
    </>
  );
}
