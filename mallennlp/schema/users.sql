DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alt_id INTEGER NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  fullname TEXT,
  nickname TEXT,
  role TEXT,
  email TEXT,
  phone TEXT,
  permissions_level INTEGER DEFAULT 1 NOT NULL
);
