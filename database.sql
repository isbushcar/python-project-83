CREATE TABLE urls
(
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name text UNIQUE NOT NULL ,
    created_at timestamp DEFAULT now()
);