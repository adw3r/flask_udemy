create table if not exists users
(
    id       integer primary key autoincrement,
    name     text    not null,
    password text    not null,
    expert   boolean not null,
    admin    boolean not null
);

create table if not exists questions
(
    id          integer primary key autoincrement,
    question    text not null,
    answer_text text,
    asked_by_id text not null,
    expert_id   text not null
);
