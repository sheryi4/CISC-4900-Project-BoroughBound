CREATE FUNCTION driver_rating_update() RETURNS TRIGGER AS $update_drating$
	BEGIN 
		UPDATE Drivers SET rating = (
			SELECT avg(T.drating) 
			FROM Trips T
			WHERE T.driver = NEW.driver)
		WHERE uid = NEW.driver; 
		RETURN NEW;
	END;
$update_drating$ LANGUAGE plpgsql;

CREATE TRIGGER update_drating 
AFTER UPDATE OF drating ON Trips
FOR EACH ROW
EXECUTE PROCEDURE driver_rating_update();

CREATE FUNCTION passenger_rating_update() RETURNS TRIGGER AS $update_prating$
	BEGIN
		UPDATE Passengers SET rating = (
			SELECT avg(T.prating)
			FROM Trips T
			WHERE T.passenger = NEW.passenger)
		WHERE uid = NEW.passenger;
		RETURN NEW;
	END;
$update_prating$ LANGUAGE plpgsql;

CREATE TRIGGER update_prating
AFTER UPDATE OF prating ON Trips
FOR EACH ROW
EXECUTE PROCEDURE passenger_rating_update();