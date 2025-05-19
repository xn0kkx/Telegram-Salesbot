-- Criar banco de dados
CREATE DATABASE telegrambot;

-- Criar usuário com senha segura
CREATE USER botuser WITH ENCRYPTED PASSWORD '7L5B^$gSiES1$u6#NJJs';

-- Conceder acesso ao banco
GRANT ALL PRIVILEGES ON DATABASE telegrambot TO botuser;

-- Conectar-se ao banco
\c telegrambot

-- Tornar botuser dono do schema public
ALTER SCHEMA public OWNER TO botuser;

-- Conceder permissões no schema
GRANT USAGE, CREATE ON SCHEMA public TO botuser;

-- Garantir privilégios futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO botuser;
