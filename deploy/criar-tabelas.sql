create table intraday (
	ticker        varchar,
	datetime      timestamp,
	openv         float,
	highv         float,
	lowv          float,
	closev        float,
	volume        bigint,
	primary key (ticker, datetime)
)