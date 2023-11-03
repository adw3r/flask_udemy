create table if not exists members
(
    id       integer primary key autoincrement,
    name text not null,
    email text not null,
    level text not null
);
