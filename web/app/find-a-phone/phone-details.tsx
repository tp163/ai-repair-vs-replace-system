'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight, Battery, Camera, ChevronDown, HardDrive, Monitor } from 'lucide-react';
import { formatPrice, type Phone } from './catalogue-data';
import PhoneIllustration from './phone-illustration';
import { phonePhotos } from './phone-photos';

function PhoneGallery({ phone }: { phone: Phone }) {
  const [photoIndex, setPhotoIndex] = useState(0);
  const modelName = `${phone.brand} ${phone.model}`;
  const photos = phonePhotos[modelName] ?? [];
  const photo = photos[photoIndex];

  return (
    <figure aria-label={`${modelName} gallery`} className="min-w-0">
      <div className="relative aspect-[4/3] overflow-hidden rounded-3xl border border-white/10 bg-[radial-gradient(ellipse_at_center,#233a65,#0c1328_75%)] sm:aspect-[3/2] lg:aspect-[4/3]">
        {photo ? (
          <Image
            key={photo.file}
            src={`/phones/${photo.file}.webp`}
            alt={`${modelName} — ${photo.view}`}
            fill
            loading="eager"
            sizes="(min-width: 1280px) 640px, (min-width: 1024px) 52vw, 95vw"
            className="object-contain"
          />
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-slate-300">
            <PhoneIllustration phone={phone} className="h-[75%] max-w-[80%]" />
            <p className="text-sm font-semibold">Device illustration</p>
          </div>
        )}
        {photo && (
          <span className="absolute bottom-3 left-3 rounded-full bg-slate-950/85 px-3 py-1 text-xs font-semibold text-white sm:bottom-4 sm:left-4">
            {photo.view}
          </span>
        )}
      </div>

      {photos.length > 1 && (
        <div role="group" aria-label="Gallery views" className="mt-3 flex flex-wrap gap-2.5">
          {photos.map((view, index) => (
            <button
              key={view.file}
              type="button"
              aria-label={`Show ${view.view.toLowerCase()}`}
              aria-pressed={photoIndex === index}
              onClick={() => setPhotoIndex(index)}
              className={`relative size-16 overflow-hidden rounded-xl border bg-slate-900 sm:size-20 ${photoIndex === index ? 'border-cyan-300 ring-2 ring-cyan-300/45' : 'border-white/10 opacity-75 hover:opacity-100'}`}
            >
              <Image src={`/phones/${view.file}.webp`} alt="" width={80} height={80} className="size-full object-contain" />
            </button>
          ))}
        </div>
      )}
      {photo && (
        <figcaption className="mt-3 text-xs leading-relaxed text-slate-400">
          <a href={photo.source} className="underline underline-offset-4 hover:text-cyan-200">
            Image by {photo.creator}
          </a>
          {' · '}
          <a href={photo.licenseUrl} className="underline underline-offset-4 hover:text-cyan-200">
            {photo.license}
          </a>
          {' · Resized'}
        </figcaption>
      )}
    </figure>
  );
}

export default function PhoneDetails({ phone }: { phone: Phone }) {
  const highlights = [
    { name: 'Display', value: `${phone.display_size_in}″ ${phone.display_type}`, icon: Monitor },
    { name: 'Battery', value: `${phone.battery_mah.toLocaleString('en-LK')} mAh`, icon: Battery },
    { name: 'Main camera', value: `${phone.camera_mp} MP`, icon: Camera },
    { name: 'Memory', value: `${phone.ram_gb} GB RAM`, icon: HardDrive },
  ];
  const specs = [
    ['Operating system', phone.os],
    ['Release year', phone.release_year],
    ['Refresh rate', `${phone.refresh_rate_hz} Hz`],
    ['Connectivity', phone.has_5g ? '5G' : '4G'],
  ];

  return (
    <section aria-labelledby="selected-phone" className="grid items-start gap-6 lg:grid-cols-[1.15fr_1fr] lg:gap-8">
      <PhoneGallery phone={phone} />
      <div className="min-w-0 rounded-3xl border border-white/10 bg-[#0c1328] p-5 sm:p-7 lg:p-8">
        <p className="font-mono text-xs font-semibold tracking-widest text-cyan-300 uppercase">{phone.brand}</p>
        <h1 id="selected-phone" className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">{phone.model}</h1>
        <div className="mt-5 border-b border-white/10 pb-5">
          <p className="text-xs font-medium text-slate-400">Sample catalogue price</p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-cyan-300">{formatPrice(phone.price_lkr)}</p>
        </div>

        <div className="mt-5">
          <p className="text-sm font-semibold text-slate-200">Catalogue configuration</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            <li className="rounded-lg border border-cyan-300/35 bg-cyan-300/10 px-3 py-1.5 text-sm font-semibold text-cyan-100">
              {phone.storage_gb} GB storage
            </li>
            <li className="rounded-lg border border-white/15 px-3 py-1.5 text-sm text-slate-200">{phone.has_5g ? '5G' : '4G'}</li>
          </ul>
        </div>

        <dl className="mt-5 grid grid-cols-2 gap-2.5">
          {highlights.map(({ name, value, icon: Icon }) => (
            <div key={name} className="rounded-xl border border-white/10 bg-slate-950/40 px-3 py-3">
              <dt className="flex items-center gap-1.5 text-xs text-slate-400">
                <Icon className="size-4 shrink-0 text-cyan-300" aria-hidden="true" />
                {name}
              </dt>
              <dd className="mt-1 text-sm font-semibold text-white">{value}</dd>
            </div>
          ))}
        </dl>

        <details className="group mt-5 border-y border-white/10">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-2 py-3 text-sm font-semibold text-white [&::-webkit-details-marker]:hidden">
            More specifications
            <ChevronDown className="size-4 text-cyan-300 group-open:rotate-180" aria-hidden="true" />
          </summary>
          <dl className="space-y-2 pb-4 text-sm">
            {specs.map(([label, value]) => (
              <div key={label} className="flex justify-between gap-3">
                <dt className="text-slate-400">{label}</dt>
                <dd className="text-white">{value}</dd>
              </div>
            ))}
          </dl>
        </details>
        <Link
          href="/diagnose"
          className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-300 px-4 py-3 text-center text-sm font-bold text-slate-950 hover:bg-cyan-200"
        >
          Diagnose my current phone <ArrowRight className="size-4 shrink-0" aria-hidden="true" />
        </Link>
      </div>
    </section>
  );
}
