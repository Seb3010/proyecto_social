-- DDL para el esquema inicial del MVP (T04)
-- Define las tablas para el sistema de becas y usuarios administradores.

DROP TABLE IF EXISTS scholarships;
DROP TABLE IF EXISTS admin_users;

-- Tabla de becas (scholarships)
CREATE TABLE scholarships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    institution TEXT NOT NULL,
    description TEXT,
    requirements TEXT,
    deadline TEXT,
    location TEXT,
    link TEXT,
    is_published INTEGER DEFAULT 0, -- 0 = Borrador, 1 = Publicada
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios administradores (admin_users)
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
