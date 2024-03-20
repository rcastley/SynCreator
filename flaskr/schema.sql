DROP TABLE IF EXISTS scc;

CREATE TABLE scc (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  condition TEXT NOT NULL,
  realm TEXT,
  rum_token TEXT,
  ingest_token TEXT
);
