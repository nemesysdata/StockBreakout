create table intraday (
	ticker        varchar,
	datetime      timestamp,
	openv         float,
	highv         float,
	lowv          float,
	closev        float,
	volume        bigint,
	primary key (ticker, datetime)
);

create table if not exists stocks_intraday (
	ticker        STRING,
	datetime      TIMESTAMP(3),
	openv         float,
	highv         float,
	lowv          float,
	closev        float,
	volume        float
);

create table if not exists breakouts (
	ticker        		varchar,
	datetime      		timestamp,
	openv         		float,
	highv         		float,
	lowv          		float,
	closev        		float,
	volume        		float,
	o_to_c 		  		  float,
	OC_20D_Mean	  		float,
	OC_Perc_20D_Mean	float,
	MaxOC_Prev10D		  float,
	Vol_20D_Mean		  float,
	Vol_Perc_20D_Mean	float,
	breakout			    boolean,
	primary key (ticker, datetime) not enforced
);

