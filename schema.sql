CREATE TABLE Drivers(
	uid			serial,
	name		varchar(30),
	email		varchar(30),
	phone		char(10) CHECK (char_length(phone) = 10),
	home_addr	varchar(50),
	rating		real CHECK (rating >= 0 AND rating <= 5),
	dob			date,
	tlc_num		integer,
	lic_num		integer,
	PRIMARY KEY (uid),
	UNIQUE (email));

CREATE TABLE Passengers(
	uid 		serial,
	name 		varchar(30),
	email 		varchar(30),
	phone 		char(10) CHECK (char_length(phone) = 10),
	rating 		real CHECK (rating >= 0 AND rating <= 5),
	trips_taken	integer,
	PRIMARY KEY (uid),
	UNIQUE (email));

CREATE TABLE Addresses(
	uid 		integer,
	street1 	varchar(30),
	street2 	varchar(20),
	city 		varchar(20),
	state 		varchar(2),
	label 		varchar(20),
	zip 		char(5) CHECK (char_length(zip) = 5),
	PRIMARY KEY (uid,label),
	FOREIGN KEY (uid) REFERENCES Passengers ON DELETE CASCADE);

CREATE TABLE Vehicle_class(
	cname 			varchar(20),
	hourly_rate		real CHECK (hourly_rate > 0),
	mileage_rate	real CHECK (mileage_rate > 0),
	PRIMARY KEY (cname));

CREATE TABLE Vehicles(
	plate_no 	varchar(20),
	make 		varchar(20),
	model 		varchar(20),
	capacity 	integer,
	cname 		varchar(20) NOT NULL,
	uid 		integer NOT NULL,
	PRIMARY KEY (plate_no),
	FOREIGN KEY (uid) REFERENCES Drivers ON DELETE CASCADE,
	FOREIGN KEY (cname) REFERENCES Vehicle_class);


CREATE TABLE Trips(
	tid 		serial,
	date 		date,
	time 		time,
	distance 	real CHECK (distance > 0),
	status 		varchar(20),
	type 		varchar(20),
	est_amount 	real CHECK (est_amount > 0),
	pick_addr 	varchar(100),
	drop_addr 	varchar(100),
	driver 		integer NOT NULL,
	passenger 	integer NOT NULL,
	drating		real CHECK (drating >= 0 AND drating <= 5),
	prating		real CHECK (prating >= 0 AND prating <= 5),
	PRIMARY KEY (tid),
	FOREIGN KEY (driver) REFERENCES Drivers (uid),
	FOREIGN KEY (passenger) REFERENCES Passengers (uid));

CREATE TABLE Transactions(
	tran_id 	serial,
	pay_type 	varchar(20),
	auth_id 	integer,
	date_time	timestamp NOT NULL DEFAULT NOW(),
	amt_charged	real,
	tid 		integer NOT NULL,
	PRIMARY KEY (tran_id),
	FOREIGN KEY (tid) REFERENCES Trips (tid),
	UNIQUE(tid));
