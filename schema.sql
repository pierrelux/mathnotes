drop table if exists entries;
drop table if exists tags;
drop table if exists tagsmap;

CREATE TABLE entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL,
  text text NOT NULL
);

CREATE TABLE tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(200) UNIQUE
);

CREATE TABLE tagsmap (
  note_id INTEGER,
  tag_id INTEGER,
  FOREIGN KEY(note_id) REFERENCES entries(id),
  FOREIGN KEY(tag_id) REFERENCES tags(id),
  PRIMARY KEY(note_id, tag_id)
);
