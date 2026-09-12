-- ============================================================
-- Migração 001: Criação das tabelas iniciais
-- Sistema de Gestão de Estoque — Grande Vitória, ES
-- ============================================================

CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS suppliers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    contact     TEXT    NOT NULL DEFAULT '',
    cnpj        TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'employee')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS products (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    sku           TEXT    NOT NULL UNIQUE,
    name          TEXT    NOT NULL,
    description   TEXT    NOT NULL DEFAULT '',
    unit_price    REAL    NOT NULL CHECK (unit_price >= 0),
    quantity      INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    minimum_stock INTEGER NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    supplier_id   INTEGER NOT NULL REFERENCES suppliers(id),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        INTEGER NOT NULL REFERENCES products(id),
    user_id           INTEGER NOT NULL REFERENCES users(id),
    type              TEXT    NOT NULL CHECK (type IN ('entry', 'exit')),
    quantity          INTEGER NOT NULL CHECK (quantity > 0),
    resulting_balance INTEGER NOT NULL CHECK (resulting_balance >= 0),
    reason            TEXT    NOT NULL,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);