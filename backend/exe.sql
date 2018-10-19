create table filenames (id serial, code varchar(255), filename varchar(255));
create table items (id serial, code varchar(255), filename varchar(255), key varchar(255), value text, ishtml boolean );
create table meta(id serial, filename varchar(255), publisher varchar(255), term varchar(255), term_from timestamp, term_to timestamp);
