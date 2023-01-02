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