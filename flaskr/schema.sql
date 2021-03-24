DROP TABLE IF EXISTS scc;

CREATE TABLE scc (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  condition TEXT NOT NULL,
  control_group TEXT,
  post_token TEXT
);
