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

INSERT INTO scc (username, password, condition) VALUES ("demo", "scrypt:32768:8:1$tXMhCEjielkxym0O$049576219980b28a0ca487ed3ceddde67b10dc4e031e2721f8b53aab09fae53c9441087c9c3b3203a7311be2eec5894a23ca59aae3d3f5a4766ecd5430fbfc15", "default");
