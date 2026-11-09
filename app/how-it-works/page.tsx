import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export const metadata: Metadata = {
  title: 'How It Works | REVIVAI',
  description: 'See how to diagnose your phone, check the repair estimate, and explore replacement options.',
};

const diagnosisSteps = [
  {
    title: 'Describe the issue',
    description: 'Tell us what happened and what you noticed, such as a flickering screen or a phone that will not charge. You can also attach a photo.',
    image: 'describe-issue',
    alt: 'Hands typing a message on a smartphone',
    photographer: 'Chidera Faustina Okeke',
    photoUrl: 'https://unsplash.com/photos/hands-typing-on-a-smartphone-with-a-message-on-screen-SrgMu4Fvk7E',
  },
  {
    title: 'Confirm your phone',
    description: 'Enter your phone’s brand and model. Add its variant, such as the storage size, if you know it. Confirm the details to run the diagnosis.',
    image: 'confirm-phone',
    alt: 'A hand holding a blue smartphone with its rear cameras visible',
    photographer: 'Andrey Matveev',
    photoUrl: 'https://unsplash.com/photos/a-hand-holds-a-unique-smartphones-back-B0w1qNmDZfM',
  },
  {
    title: 'Review the diagnosis',
    description: 'See the likely fault, how confident the system is, and any safety warnings that apply. Some symptoms may need a closer look from a technician.',
    image: 'review-diagnosis',
    alt: 'A person holding a phone with a cracked screen',
    photographer: 'Rahul Himkar',
    photoUrl: 'https://unsplash.com/photos/a-person-holding-a-cell-phone-in-their-hand-jIK2TATWgFM',
  },
];

const nextOptions = [
  {
    label: 'Repair',
    title: 'Check the repair estimate',
    description: 'See the estimated repair cost in LKR when one is available for your phone and fault. Use the range when asking a repair shop for a quote.',
    image: 'repair-estimate',
    alt: 'A technician using a precision screwdriver to repair a phone',
    photographer: 'Revendo',
    photoUrl: 'https://unsplash.com/photos/a-person-using-a-screwdriver-to-fix-a-cell-phone-Q_I49DIzHu8',
  },
  {
    label: 'Replace',
    title: 'Explore replacement phones',
    description: 'See suggested phones and available prices. Compare them with the repair estimate to decide whether to fix your phone or replace it.',
    image: 'compare-phones',
    alt: 'Two iPhones sitting side by side on a table',
    photographer: 'Amanz',
    photoUrl: 'https://unsplash.com/photos/two-iphones-sitting-side-by-side-on-a-table-uumtSKNTjss',
  },
];

function WorkflowCard({
  card,
  label,
  option = false,
}: {
  card: (typeof diagnosisSteps)[number];
  label: string;
  option?: boolean;
}) {
  return (
    <li className="flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#0c1328]">
      <div className={`relative aspect-[16/10] bg-slate-800 ${option ? 'sm:aspect-[2/1]' : ''}`}>
        <Image
          src={`/how-it-works/${card.image}.webp`}
          alt={card.alt}
          fill
          sizes={option
            ? '(min-width: 1152px) 532px, (min-width: 640px) 50vw, 100vw'
            : '(min-width: 1152px) 350px, (min-width: 768px) 33vw, 100vw'}
          className="object-cover"
        />
        <span className="absolute top-3 left-3 rounded-full border border-white/20 bg-slate-950/85 px-3 py-1 text-xs font-semibold tracking-wide text-cyan-200">
          {label}
        </span>
      </div>
      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <h3 className="text-xl font-bold text-white">{card.title}</h3>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-300">{card.description}</p>
        <a
          href={card.photoUrl}
          className="mt-5 self-start text-xs text-slate-400 underline decoration-slate-500 underline-offset-4 hover:text-cyan-200"
        >
          Photo by {card.photographer} on Unsplash
        </a>
      </div>
    </li>
  );
}

export default function HowItWorksPage() {
  return (
    <div className="flex-1 bg-[#06091a] text-slate-100">
      <main className="mx-auto max-w-6xl px-5 pb-14 sm:px-8 sm:pb-20">
        <div className="border-b border-white/10 py-10 sm:py-14">
          <p className="font-mono text-xs font-semibold tracking-widest text-cyan-300 uppercase">The REVIVAI guide</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-white sm:text-6xl">How It Works</h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-slate-300">
            Find out what might be wrong with your phone, then weigh the cost of repairing it against the cost of replacing it.
          </p>
        </div>

        <section aria-labelledby="diagnosis-steps" className="mt-8 sm:mt-10">
          <h2 id="diagnosis-steps" className="text-2xl font-bold tracking-tight text-white">Get your diagnosis</h2>
          <ol className="mt-5 grid gap-5 md:grid-cols-3">
            {diagnosisSteps.map((card, index) => (
              <WorkflowCard key={card.image} card={card} label={`Step 0${index + 1}`} />
            ))}
          </ol>
        </section>

        <section aria-labelledby="next-options" className="mt-10 sm:mt-12">
          <h2 id="next-options" className="text-2xl font-bold tracking-tight text-white">Choose what to do next</h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-300">After diagnosis, you can explore either option or look at both.</p>
          <ul className="mt-5 grid gap-5 sm:grid-cols-2">
            {nextOptions.map((card) => (
              <WorkflowCard key={card.image} card={card} label={card.label} option />
            ))}
          </ul>
        </section>

        <div className="mt-10 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-cyan-400/25 bg-cyan-400/5 p-5 sm:p-7">
          <h2 className="text-xl font-bold text-white">Ready to check your phone?</h2>
          <Link href="/diagnose" className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-5 py-3 text-sm font-bold text-slate-950 hover:bg-cyan-200">
            Start a diagnosis <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </div>
      </main>
    </div>
  );
}
