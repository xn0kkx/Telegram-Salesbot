-- Criar banco de dados
CREATE DATABASE telegrambot;

-- Criar usuário com senha segura
CREATE USER botuser WITH ENCRYPTED PASSWORD '7L5B^$gSiES1$u6#NJJs';

-- Conceder acesso ao banco
GRANT ALL PRIVILEGES ON DATABASE telegrambot TO botuser;

-- Conectar ao banco
\c telegrambot

-- Tornar o usuário dono do schema
ALTER SCHEMA public OWNER TO botuser;

-- Conceder permissões
GRANT USAGE, CREATE ON SCHEMA public TO botuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO botuser;

-- Criar tabela com novos campos
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    payment_id TEXT,
    payment_status TEXT,
    plano_valor REAL,
    bot_id BIGINT,
    gateway TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
