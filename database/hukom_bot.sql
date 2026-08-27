--
-- PostgreSQL database dump
--

\restrict ZiKgLy1Ikb9Elcf1pSuAmzhbTdOT5CBFEdVHxaccO9RFgC5juQZ1awrrfOp5qFN

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-08-27 23:24:47

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
-- TOC entry 5401 (class 0 OID 0)
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
-- TOC entry 5402 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- TOC entry 1062 (class 1247 OID 99710)
-- Name: case_analysis_answer_format; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.case_analysis_answer_format AS ENUM (
    'plaintext',
    'html',
    'markdown',
    'json'
);


ALTER TYPE public.case_analysis_answer_format OWNER TO postgres;

--
-- TOC entry 1041 (class 1247 OID 58462)
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
-- TOC entry 1032 (class 1247 OID 25624)
-- Name: oauth_provider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.oauth_provider AS ENUM (
    'google',
    'facebook',
    'apple'
);


ALTER TYPE public.oauth_provider OWNER TO postgres;

--
-- TOC entry 1038 (class 1247 OID 33886)
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
-- TOC entry 1059 (class 1247 OID 91499)
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'standard',
    'contributor',
    'admin'
);


ALTER TYPE public.user_role OWNER TO postgres;

--
-- TOC entry 307 (class 1255 OID 58552)
-- Name: _immutable_to_tsvector(regconfig, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._immutable_to_tsvector(config regconfig, document text) RETURNS tsvector
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
    SELECT to_tsvector(config, document);
$$;


ALTER FUNCTION public._immutable_to_tsvector(config regconfig, document text) OWNER TO postgres;

--
-- TOC entry 297 (class 1255 OID 91496)
-- Name: _set_user_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._set_user_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
	new.updated_at = NOW();
	return new;
end;
$$;


ALTER FUNCTION public._set_user_updated_at() OWNER TO postgres;

--
-- TOC entry 266 (class 1255 OID 99731)
-- Name: _update_case_analysis_versions_search_vector(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._update_case_analysis_versions_search_vector() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
	new.search_vector :=
		to_tsvector(
			'english',
			concat_ws(
				 ' ',
				 new.answer,
				 new.title
			)
		);

	return new;
end;
$$;


ALTER FUNCTION public._update_case_analysis_versions_search_vector() OWNER TO postgres;

--
-- TOC entry 295 (class 1255 OID 58555)
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
-- TOC entry 346 (class 1255 OID 91493)
-- Name: _update_user_search_vector(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public._update_user_search_vector() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	NEW.search_vector :=
		to_tsvector(
			'english',
			concat_ws(
				' ',
				NEW.first_name,
                NEW.last_name,
                NEW.email,
                NEW.provider::text
			)
		);

	RETURN NEW;
END;
$$;


ALTER FUNCTION public._update_user_search_vector() OWNER TO postgres;

--
-- TOC entry 289 (class 1255 OID 31353)
-- Name: immutable_english_tsvector(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.immutable_english_tsvector(text) RETURNS tsvector
    LANGUAGE sql IMMUTABLE
    AS $_$
    SELECT to_tsvector('pg_catalog.english', $1);
$_$;


ALTER FUNCTION public.immutable_english_tsvector(text) OWNER TO postgres;

--
-- TOC entry 267 (class 1255 OID 31354)
-- Name: immutable_enum_to_text(anyenum); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.immutable_enum_to_text(anyenum) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $_$
  SELECT $1::text;
$_$;


ALTER FUNCTION public.immutable_enum_to_text(anyenum) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 75016)
-- Name: case_analysis_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.case_analysis_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id uuid NOT NULL
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
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    answer_format public.case_analysis_answer_format NOT NULL,
    title text NOT NULL,
    search_vector tsvector
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
    file_type character varying(20) DEFAULT NULL::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    upload_status public.upload_status DEFAULT 'pending'::public.upload_status NOT NULL,
    upload_error text,
    document_type public.legal_document_type NOT NULL,
    upload_file_name uuid NOT NULL,
    search_vector tsvector,
    digest bytea NOT NULL,
    uploader_id uuid NOT NULL
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 99723)
-- Name: revoked_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revoked_tokens (
    jti uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL
);


ALTER TABLE public.revoked_tokens OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25631)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email text NOT NULL,
    profile_picture text,
    provider public.oauth_provider NOT NULL,
    provider_id text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    search_vector tsvector,
    role public.user_role NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 5221 (class 2606 OID 75026)
-- Name: case_analysis_sessions case_analysis_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_sessions
    ADD CONSTRAINT case_analysis_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 5234 (class 2606 OID 75092)
-- Name: case_analysis_version_facts case_analysis_version_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_pkey PRIMARY KEY (case_analysis_version_id, case_fact_version_id);


--
-- TOC entry 5229 (class 2606 OID 75080)
-- Name: case_analysis_versions case_analysis_versions_case_analysis_session_id_version_num_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_case_analysis_session_id_version_num_key UNIQUE (case_analysis_session_id, version_number);


--
-- TOC entry 5231 (class 2606 OID 75078)
-- Name: case_analysis_versions case_analysis_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 5225 (class 2606 OID 75059)
-- Name: case_fact_versions case_fact_versions_case_fact_id_version_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_case_fact_id_version_number_key UNIQUE (case_fact_id, version_number);


--
-- TOC entry 5227 (class 2606 OID 75057)
-- Name: case_fact_versions case_fact_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 5223 (class 2606 OID 75036)
-- Name: case_facts case_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_facts
    ADD CONSTRAINT case_facts_pkey PRIMARY KEY (id);


--
-- TOC entry 5213 (class 2606 OID 16765)
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- TOC entry 5207 (class 2606 OID 66697)
-- Name: documents documents_digest_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_digest_key UNIQUE (digest);


--
-- TOC entry 5209 (class 2606 OID 16727)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5211 (class 2606 OID 58549)
-- Name: documents documents_upload_file_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_upload_file_name_key UNIQUE (upload_file_name);


--
-- TOC entry 5237 (class 2606 OID 99729)
-- Name: revoked_tokens revoked_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revoked_tokens
    ADD CONSTRAINT revoked_tokens_pkey PRIMARY KEY (jti);


--
-- TOC entry 5217 (class 2606 OID 25650)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5219 (class 2606 OID 25648)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5205 (class 1259 OID 17823)
-- Name: document_title_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX document_title_idx ON public.documents USING btree (original_file_name);


--
-- TOC entry 5232 (class 1259 OID 99735)
-- Name: idx_case_analysis_version_search_vector; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_analysis_version_search_vector ON public.case_analysis_versions USING gin (search_vector);


--
-- TOC entry 5235 (class 1259 OID 99730)
-- Name: idx_revoked_tokens_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_revoked_tokens_expires_at ON public.revoked_tokens USING btree (expires_at);


--
-- TOC entry 5214 (class 1259 OID 25690)
-- Name: idx_users_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_provider ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5215 (class 1259 OID 25689)
-- Name: uq_users_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_users_provider_id ON public.users USING btree (provider, provider_id);


--
-- TOC entry 5247 (class 2620 OID 91497)
-- Name: users trg_set_user_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_set_user_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public._set_user_updated_at();


--
-- TOC entry 5248 (class 2620 OID 99732)
-- Name: case_analysis_versions trg_update_case_analysis_version_search_vector; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_case_analysis_version_search_vector BEFORE INSERT OR UPDATE ON public.case_analysis_versions FOR EACH ROW EXECUTE FUNCTION public._update_case_analysis_versions_search_vector();


--
-- TOC entry 5246 (class 2620 OID 58556)
-- Name: documents trg_update_document_search_vector; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_document_search_vector BEFORE INSERT OR UPDATE ON public.documents FOR EACH ROW EXECUTE FUNCTION public._update_document_search_vector();


--
-- TOC entry 5244 (class 2606 OID 75093)
-- Name: case_analysis_version_facts case_analysis_version_facts_case_analysis_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_case_analysis_version_id_fkey FOREIGN KEY (case_analysis_version_id) REFERENCES public.case_analysis_versions(id) ON DELETE CASCADE;


--
-- TOC entry 5245 (class 2606 OID 75098)
-- Name: case_analysis_version_facts case_analysis_version_facts_case_fact_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_version_facts
    ADD CONSTRAINT case_analysis_version_facts_case_fact_version_id_fkey FOREIGN KEY (case_fact_version_id) REFERENCES public.case_fact_versions(id) ON DELETE RESTRICT;


--
-- TOC entry 5243 (class 2606 OID 75081)
-- Name: case_analysis_versions case_analysis_versions_case_analysis_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_versions
    ADD CONSTRAINT case_analysis_versions_case_analysis_session_id_fkey FOREIGN KEY (case_analysis_session_id) REFERENCES public.case_analysis_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 5242 (class 2606 OID 75060)
-- Name: case_fact_versions case_fact_versions_case_fact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_fact_versions
    ADD CONSTRAINT case_fact_versions_case_fact_id_fkey FOREIGN KEY (case_fact_id) REFERENCES public.case_facts(id) ON DELETE CASCADE;


--
-- TOC entry 5241 (class 2606 OID 75037)
-- Name: case_facts case_facts_case_analysis_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_facts
    ADD CONSTRAINT case_facts_case_analysis_session_id_fkey FOREIGN KEY (case_analysis_session_id) REFERENCES public.case_analysis_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 5239 (class 2606 OID 17003)
-- Name: chunks chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE;


--
-- TOC entry 5240 (class 2606 OID 91514)
-- Name: case_analysis_sessions fk_case_analysis_session_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.case_analysis_sessions
    ADD CONSTRAINT fk_case_analysis_session_user FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 5238 (class 2606 OID 91507)
-- Name: documents fk_users_documents; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT fk_users_documents FOREIGN KEY (uploader_id) REFERENCES public.users(id);


-- Completed on 2026-08-27 23:24:47

--
-- PostgreSQL database dump complete
--

\unrestrict ZiKgLy1Ikb9Elcf1pSuAmzhbTdOT5CBFEdVHxaccO9RFgC5juQZ1awrrfOp5qFN

