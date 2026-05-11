ALTER TABLE Drivers ADD COLUMN reserved_trips integer; 
ALTER TABLE Drivers ADD COLUMN completed_trips integer;

CREATE FUNCTION driver_trips_update() RETURNS TRIGGER AS $dtrips_update$
	BEGIN 
		UPDATE Drivers SET reserved_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = NEW.driver AND T.status='reserved')
		WHERE uid = NEW.driver;
		UPDATE Drivers SET completed_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = NEW.driver AND T.status='completed')
		WHERE uid = NEW.driver; 
		RETURN NEW;
	END;
$dtrips_update$ LANGUAGE plpgsql;

CREATE TRIGGER dtrips_update
AFTER UPDATE OF status ON Trips
FOR EACH ROW
EXECUTE PROCEDURE driver_trips_update();

CREATE FUNCTION driver_trips_insert() RETURNS TRIGGER AS $dtrips_insert$
	BEGIN 
		UPDATE Drivers SET reserved_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = NEW.driver AND T.status='reserved')
		WHERE uid = NEW.driver;
		UPDATE Drivers SET completed_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = NEW.driver AND T.status='completed')
		WHERE uid = NEW.driver; 
		RETURN NEW;
	END;
$dtrips_insert$ LANGUAGE plpgsql;

CREATE TRIGGER dtrips_insert
AFTER INSERT ON Trips
FOR EACH ROW
EXECUTE PROCEDURE driver_trips_insert();

CREATE FUNCTION driver_trips_delete() RETURNS TRIGGER AS $dtrips_delete$
	BEGIN 
		UPDATE Drivers SET reserved_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = OLD.driver AND T.status='reserved')
		WHERE uid = OLD.driver;
		UPDATE Drivers SET completed_trips = (
			SELECT count(T.driver)
			FROM Trips T
			WHERE T.driver = OLD.driver AND T.status='completed')
		WHERE uid = OLD.driver; 
		RETURN NEW;
	END;
$dtrips_delete$ LANGUAGE plpgsql;

CREATE TRIGGER dtrips_delete
AFTER DELETE ON Trips
FOR EACH ROW
EXECUTE PROCEDURE driver_trips_delete();