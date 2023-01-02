CREATE TABLE public.urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name text UNIQUE NOT NULL ,
    created_at timestamp DEFAULT now()
);

CREATE TABLE public.url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES public.urls (id) NOT NULL,
    status_code int,
    h1 text,
    title text,
    description text,
    created_at timestamp DEFAULT now()
);

CREATE VIEW public.urls_with_last_checks AS (
    SELECT
           urls.id,
           urls.name,
           coalesce(uc.last_checked::date::text, '') as last_checked,
           coalesce(uc.status_code::text, '') as status_code
    FROM public.urls
    LEFT JOIN (
        SELECT
           url_id,
           created_at AS last_checked,
           status_code,
           row_number() OVER (PARTITION BY url_id ORDER BY created_at DESC) rn
        FROM public.url_checks
        ) uc
        ON urls.id = uc.url_id
    WHERE uc.rn = 1
    ORDER BY urls.created_at DESC);