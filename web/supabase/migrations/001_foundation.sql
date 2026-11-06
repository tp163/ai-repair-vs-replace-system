-- Apply through Supabase SQL editor or migrations after reviewing in a development project.
create extension if not exists vector;
create table public.device_variants (
 id text primary key, brand text not null, model text not null, variant text not null,
 specifications jsonb not null default '{}', source_url text, checked_at timestamptz,
 verified boolean not null default false
);
create table public.market_offers (
 id uuid primary key default gen_random_uuid(), device_id text not null references public.device_variants(id),
 seller text not null, price_lkr numeric not null check(price_lkr>0), stock_status text not null default 'unknown'
 check(stock_status in ('available','unavailable','unknown')), source_url text not null, checked_at timestamptz not null
);
create table public.repair_records (
 id uuid primary key default gen_random_uuid(), device_id text not null references public.device_variants(id),
 fault_category text not null, part_quality text not null, provider text not null,
 min_lkr numeric not null check(min_lkr>=0), max_lkr numeric not null,
 parts_lkr numeric check(parts_lkr>=0), labour_lkr numeric check(labour_lkr>=0),
 source_url text not null, checked_at timestamptz not null, check(max_lkr>=min_lkr)
);
create table public.documents (
 id uuid primary key default gen_random_uuid(), title text not null, source_url text not null,
 device_id text references public.device_variants(id), approved boolean not null default false,
 checked_at timestamptz not null default now()
);
create table public.document_chunks (
 id uuid primary key default gen_random_uuid(), document_id uuid not null references public.documents(id) on delete cascade,
 content text not null, section_reference text not null,
 embedding vector -- Select a fixed dimension and index after choosing the embedding model.
);
create table public.cases (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
 device_id text not null references public.device_variants(id), confirmed boolean not null default false,
 symptoms text not null, status text not null default 'draft', result jsonb,
 created_at timestamptz not null default now()
);
create table public.case_events (
 id uuid primary key default gen_random_uuid(), case_id uuid not null references public.cases(id) on delete cascade,
 event_type text not null, payload jsonb not null, created_at timestamptz not null default now()
);
create table public.agent_runs (
 id uuid primary key default gen_random_uuid(), case_id uuid not null references public.cases(id) on delete cascade,
 agent text not null, version text not null, evidence jsonb not null default '[]', elapsed_ms integer check(elapsed_ms>=0),
 created_at timestamptz not null default now()
);
alter table public.device_variants enable row level security;
alter table public.market_offers enable row level security;
alter table public.repair_records enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.cases enable row level security;
alter table public.case_events enable row level security;
alter table public.agent_runs enable row level security;
create policy "Read verified variants" on public.device_variants for select using(verified);
create policy "Read offers" on public.market_offers for select using(true);
create policy "Read repair evidence" on public.repair_records for select using(true);
create policy "Read approved documents" on public.documents for select using(approved);
create policy "Read approved chunks" on public.document_chunks for select using(exists(select 1 from public.documents d where d.id=document_id and d.approved));
create policy "Own cases" on public.cases for all to authenticated using(auth.uid()=user_id) with check(auth.uid()=user_id);
create policy "Own events" on public.case_events for all to authenticated using(exists(select 1 from public.cases c where c.id=case_id and c.user_id=auth.uid())) with check(exists(select 1 from public.cases c where c.id=case_id and c.user_id=auth.uid()));
create policy "Read own runs" on public.agent_runs for select to authenticated using(exists(select 1 from public.cases c where c.id=case_id and c.user_id=auth.uid()));
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('case-photos','case-photos',false,2000000,array['image/jpeg','image/png','image/webp']) on conflict(id) do nothing;
create policy "Upload own photos" on storage.objects for insert to authenticated with check(bucket_id='case-photos' and (storage.foldername(name))[1]=auth.uid()::text);
create policy "Read own photos" on storage.objects for select to authenticated using(bucket_id='case-photos' and (storage.foldername(name))[1]=auth.uid()::text);
create policy "Delete own photos" on storage.objects for delete to authenticated using(bucket_id='case-photos' and (storage.foldername(name))[1]=auth.uid()::text);
