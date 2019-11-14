DROP TABLE IF EXISTS experiments;

CREATE TABLE experiments (
  path TEXT UNIQUE NOT NULL,
  tags TEXT
);
