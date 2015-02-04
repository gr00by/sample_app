drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  url text not null,
  filename text not null,
  mimetype text not null,
  size numeric not null

);