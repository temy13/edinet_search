create table filenames (id serial, code varchar(255), filename varchar(255));
create table items (id serial, code varchar(255), filename varchar(255), key varchar(255), value text, ishtml boolean, origin_value text );
create table meta(id serial, filename varchar(255), publisher varchar(255), term varchar(255), term_from timestamp, term_to timestamp);
create table values(id serial, code varchar(255), filename varchar(255), value text, origin_value text, part integer);
