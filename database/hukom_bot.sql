--
-- PostgreSQL database dump
--

\restrict gxee4Yg1tHzPT7XDT5zs4mqbnbK9eVkhTcIs5oHfQGPILVzhNybfPEQLRfp4L48

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-07-17 21:46:55

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
-- TOC entry 5384 (class 0 OID 0)
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
-- TOC entry 5385 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- TOC entry 1038 (class 1247 OID 58462)
-- Name: legal_document_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.legal_document_type AS ENUM (
    'contract',
    'non_disclosure_agreement',
    'service_agreement',
    'employment_contract',
    'lease_agreement',
    'partnership_agreement',
    'memorandum_of_agreement',
    'memorandum_of_understanding',
    'articles_of_incorporation',
    'bylaws',
    'board_resolution',
    'shareholder_agreement',
    'minutes_of_meeting',
    'complaint',
    'affidavit',
    'subpoena',
    'court_order',
    'judgment',
    'motion',
    'summons',
    'last_will_and_testament',
    'deed_of_sale',
    'power_of_attorney',
    'trust_deed',
    'birth_certificate',
    'marriage_contract',
    'permit',
    'license',
    'government_issued_id',
    'tax_declaration',
    'promissory_note',
    'deed_of_mortgage',
    'loan_agreement',
    'invoice',
    'receipt',
    'patent',
    'trademark_registration',
    'copyright_registration',
    'certification',
    'waiver',
    'notice',
    'other',
    'addendum_amendment',
    'franchise_agreement',
    'indemnity_agreement',
    'secretary_certificate',
    'general_information_sheet',
    'pleading',
    'brief_memorandum',
    'supreme_court_decision',
    'court_of_appeals_decision',
    'deed_of_donation',
    'prenuptial_agreement',
    'tax_clearance',
    'certificate_of_registration',
    'revenue_regulation',
    'revenue_memorandum_circular',
    'executive_order',
    'municipal_ordinance',
    'republic_act',
    'audited_financial_statement',
    'ip_assignment',
    'constitution'
);


ALTER TYPE public.legal_document_type OWNER TO postgres;

--
-- TOC entry 1029 (class 1247 OID 25624)
-- Name: oauth_provider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.oauth_provider AS ENUM (
    'google',
    'facebook',
    'apple'
);


ALTER TYPE public.oauth_provider OWNER TO postgres;

--
-- TOC entry 1035 (class 1247 OID 33886)
-- Name: upload_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.upload_status AS ENUM (
    'pending',
    'ongoing',
    'completed',
    'failed'
);


ALTER TYPE public.upload_status OWNER TO postgres;

--
-- TOC entry 305 (class 1255 OID 58552)
-- Name: _immutable_to_tsvector(regconfig, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._immutable_to_tsvector(config regconfig, document text) RETURNS tsvector
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
    SELECT to_tsvector(config, document);
$$;


ALTER FUNCTION public._immutable_to_tsvector(config regconfig, document text) OWNER TO postgres;

--
-- TOC entry 293 (class 1255 OID 58555)
-- Name: _update_document_search_vector(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._update_document_search_vector() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	NEW.search_vector :=
		to_tsvector(
			'english',
			concat_ws(
				' ',
				NEW.original_file_name,
                NEW.document_type::text,
                NEW.file_type,
                NEW.upload_status::text
			)
		);

	RETURN NEW;
END;
$$;


ALTER FUNCTION public._update_document_search_vector() OWNER TO postgres;

--
-- TOC entry 287 (class 1255 OID 31353)
-- Name: immutable_english_tsvector(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.immutable_english_tsvector(text) RETURNS tsvector
    LANGUAGE sql IMMUTABLE
    AS $_$
    SELECT to_tsvector('pg_catalog.english', $1);
$_$;


ALTER FUNCTION public.immutable_english_tsvector(text) OWNER TO postgres;

--
-- TOC entry 265 (class 1255 OID 31354)
-- Name: immutable_enum_to_text(anyenum); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.immutable_enum_to_text(anyenum) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $_$
  SELECT $1::text;
$_$;


ALTER FUNCTION public.immutable_enum_to_text(anyenum) OWNER TO postgres;

--
-- TOC entry 301 (class 1255 OID 25691)
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
-- TOC entry 224 (class 1259 OID 75016)
-- Name: case_analysis_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_analysis_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.case_analysis_sessions OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 75086)
-- Name: case_analysis_version_facts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_analysis_version_facts (
    case_analysis_version_id uuid NOT NULL,
    case_fact_version_id uuid NOT NULL
);


ALTER TABLE public.case_analysis_version_facts OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 75065)
-- Name: case_analysis_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_analysis_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_analysis_session_id uuid NOT NULL,
    version_number integer NOT NULL,
    answer text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.case_analysis_versions OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 75042)
-- Name: case_fact_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_fact_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_fact_id uuid NOT NULL,
    version_number integer NOT NULL,
    fact text NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.case_fact_versions OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 75027)
-- Name: case_facts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_facts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_analysis_session_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.case_facts OWNER TO postgres;

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
    original_file_name text CONSTRAINT documents_title_not_null NOT NULL,
    file_type character varying(20) DEFAULT NULL::character varying,
    created_at timestamp without time zone DEFAULT now(),
    upload_status public.upload_status DEFAULT 'pending'::public.upload_status NOT NULL,
    upload_error text,
    document_type public.legal_document_type NOT NULL,
    upload_file_name uuid NOT NULL,
    search_vector tsvector,
    digest bytea NOT NULL
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
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, ((((COALESCE(display_name, ''::text) || ' '::text) || COALESCE(email, ''::text)) || ' '::text) || COALESCE(public.immutable_enum_to_text(provider), ''::text)))) STORED
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 5211 (class 2606 OID 75026)
-- Name: case_analysis_sessions case_analysis_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_sessions
    ADD CONSTRAINT case_analysis_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 5223 (class 2606 OID 75092)
-- Name: case_analysis_version_facts case_analysis_version_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_pkey PRIMARY KEY (case_analysis_version_id, case_fact_version_id);


--
-- TOC entry 5219 (class 2606 OID 75080)
-- Name: case_analysis_versions case_analysis_versions_case_analysis_session_id_version_num_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_case_analysis_session_id_version_num_key UNIQUE (case_analysis_session_id, version_number);


--
-- TOC entry 5221 (class 2606 OID 75078)
-- Name: case_analysis_versions case_analysis_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 5215 (class 2606 OID 75059)
-- Name: case_fact_versions case_fact_versions_case_fact_id_version_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_case_fact_id_version_number_key UNIQUE (case_fact_id, version_number);


--
-- TOC entry 5217 (class 2606 OID 75057)
-- Name: case_fact_versions case_fact_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 5213 (class 2606 OID 75036)
-- Name: case_facts case_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_facts
    ADD CONSTRAINT case_facts_pkey PRIMARY KEY (id);


--
-- TOC entry 5202 (class 2606 OID 16765)
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- TOC entry 5196 (class 2606 OID 66697)
-- Name: documents documents_digest_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_digest_key UNIQUE (digest);


--
-- TOC entry 5198 (class 2606 OID 16727)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5200 (class 2606 OID 58549)
-- Name: documents documents_upload_file_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_upload_file_name_key UNIQUE (upload_file_name);


--
-- TOC entry 5206 (class 2606 OID 25650)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5208 (class 2606 OID 25648)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5194 (class 1259 OID 17823)
-- Name: document_title_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX document_title_idx ON public.documents USING btree (original_file_name);


--
-- TOC entry 5203 (class 1259 OID 25690)
-- Name: idx_users_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_provider ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5204 (class 1259 OID 25689)
-- Name: uq_users_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_users_provider_id ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5209 (class 1259 OID 31365)
-- Name: users_search_vector_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_search_vector_idx ON public.users USING gin (search_vector);


--
-- TOC entry 5230 (class 2620 OID 58556)
-- Name: documents trg_update_document_search_vector; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_document_search_vector BEFORE INSERT OR UPDATE ON public.documents FOR EACH ROW EXECUTE FUNCTION public._update_document_search_vector();


--
-- TOC entry 5231 (class 2620 OID 25692)
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- TOC entry 5228 (class 2606 OID 75093)
-- Name: case_analysis_version_facts case_analysis_version_facts_case_analysis_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_case_analysis_version_id_fkey FOREIGN KEY (case_analysis_version_id) REFERENCES public.case_analysis_versions(id) ON DELETE CASCADE;


--
-- TOC entry 5229 (class 2606 OID 75098)
-- Name: case_analysis_version_facts case_analysis_version_facts_case_fact_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_case_fact_version_id_fkey FOREIGN KEY (case_fact_version_id) REFERENCES public.case_fact_versions(id) ON DELETE RESTRICT;


--
-- TOC entry 5227 (class 2606 OID 75081)
-- Name: case_analysis_versions case_analysis_versions_case_analysis_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_case_analysis_session_id_fkey FOREIGN KEY (case_analysis_session_id) REFERENCES public.case_analysis_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 5226 (class 2606 OID 75060)
-- Name: case_fact_versions case_fact_versions_case_fact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_case_fact_id_fkey FOREIGN KEY (case_fact_id) REFERENCES public.case_facts(id) ON DELETE CASCADE;


--
-- TOC entry 5225 (class 2606 OID 75037)
-- Name: case_facts case_facts_case_analysis_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_facts
    ADD CONSTRAINT case_facts_case_analysis_session_id_fkey FOREIGN KEY (case_analysis_session_id) REFERENCES public.case_analysis_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 5224 (class 2606 OID 17003)
-- Name: chunks chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE;


-- Completed on 2026-07-17 21:46:56

--
-- PostgreSQL database dump complete
--

\unrestrict gxee4Yg1tHzPT7XDT5zs4mqbnbK9eVkhTcIs5oHfQGPILVzhNybfPEQLRfp4L48

