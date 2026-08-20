create table if not exists public.fotos (
    id uuid primary key default gen_random_uuid(),
    estudante text not null,
    legenda text not null,
    imagem_path text not null unique,
    imagem_url text not null,
    criado_em timestamptz not null default now()
);

alter table public.fotos enable row level security;

grant select, insert on public.fotos to anon, authenticated;

create policy "Leitura publica das fotos"
on public.fotos for select
to anon, authenticated
using (true);

create policy "Insercao publica das fotos"
on public.fotos for insert
to anon, authenticated
with check (true);

insert into storage.buckets (id, name, public)
values ('fotos', 'fotos', true)
on conflict (id) do update set public = true;

create policy "Leitura publica do bucket de fotos"
on storage.objects for select
to anon, authenticated
using (bucket_id = 'fotos');

create policy "Upload publico no bucket de fotos"
on storage.objects for insert
to anon, authenticated
with check (bucket_id = 'fotos');