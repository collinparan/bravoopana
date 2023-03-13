set search_path = postgres, public;

create schema extensions;

-- make sure everybody can use everything in the extensions schema
grant usage on schema extensions to public;
grant execute on all functions in schema extensions to public;

-- include future extensions
alter default privileges in schema extensions
   grant execute on functions to public;

alter default privileges in schema extensions
   grant usage on types to public;


create extension IF NOT EXISTS "uuid-ossp" WITH SCHEMA extensions;

create extension IF NOT EXISTS pgcrypto WITH SCHEMA extensions;