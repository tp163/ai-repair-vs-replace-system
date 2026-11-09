import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { phones } from '../catalogue-data';
import PhoneDetails from '../phone-details';

export function generateStaticParams() {
  return phones.map(({ id }) => ({ id }));
}

export default async function PhonePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const phone = phones.find((item) => item.id === id);
  if (!phone) notFound();

  return (
    <main className="mx-auto w-full max-w-7xl px-4 pt-6 pb-14 sm:px-8 sm:pt-8">
      <Link href="/find-a-phone" className="mb-6 inline-flex items-center gap-2 text-sm text-cyan-300 hover:text-white">
        <ArrowLeft className="size-4" aria-hidden="true" />
        All phones
      </Link>
      <PhoneDetails phone={phone} />
    </main>
  );
}
