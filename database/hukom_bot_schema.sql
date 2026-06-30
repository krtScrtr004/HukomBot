--
-- PostgreSQL database dump
--

\restrict G4bpyDQHnjTounwe2rbLz1YYr0wKpiLB0mJRLcFaev66Q5io4b1CQXWjlwwqXez

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-06-30 14:19:44

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3 (class 3079 OID 25651)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5319 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 2 (class 3079 OID 16389)
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- TOC entry 5320 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- TOC entry 1020 (class 1247 OID 25624)
-- Name: oauth_provider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.oauth_provider AS ENUM (
    'google',
    'facebook',
    'apple'
);


ALTER TYPE public.oauth_provider OWNER TO postgres;

--
-- TOC entry 293 (class 1255 OID 25691)
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_updated_at() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 16728)
-- Name: chunks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chunks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    chunk_number integer NOT NULL,
    chunk_text text NOT NULL,
    embedding public.vector(768),
    section character varying(100) NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, ((COALESCE(chunk_text, ''::text) || ' '::text) || (COALESCE(section, ''::character varying))::text))) STORED
);


ALTER TABLE public.chunks OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16717)
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    file_type character varying(20) DEFAULT NULL::character varying,
    created_at timestamp without time zone DEFAULT now(),
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, ((title || ' '::text) || (file_type)::text))) STORED
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25631)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email text NOT NULL,
    display_name text,
    avatar_url text,
    provider public.oauth_provider NOT NULL,
    provider_id text NOT NULL,
    access_token text,
    refresh_token text,
    token_expires_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    last_login_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 5158 (class 2606 OID 16765)
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- TOC entry 5155 (class 2606 OID 16727)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5162 (class 2606 OID 25650)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5164 (class 2606 OID 25648)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5153 (class 1259 OID 17823)
-- Name: document_title_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX document_title_idx ON public.documents USING btree (title);


--
-- TOC entry 5156 (class 1259 OID 16774)
-- Name: documents_search_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX documents_search_idx ON public.documents USING gin (search_vector);


--
-- TOC entry 5159 (class 1259 OID 25690)
-- Name: idx_users_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_provider ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5160 (class 1259 OID 25689)
-- Name: uq_users_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_users_provider_id ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5166 (class 2620 OID 25692)
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- TOC entry 5165 (class 2606 OID 17003)
-- Name: chunks chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE;


-- Completed on 2026-06-30 14:19:44

--
-- PostgreSQL database dump complete
--

\unrestrict G4bpyDQHnjTounwe2rbLz1YYr0wKpiLB0mJRLcFaev66Q5io4b1CQXWjlwwqXez

