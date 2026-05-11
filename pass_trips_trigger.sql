CREATE FUNCTION passenger_trips_update() RETURNS TRIGGER AS $update_ptrips$
	BEGIN 
		UPDATE Passengers SET trips_taken = (
			SELECT count(T.passenger)
			FROM Trips T
			WHERE T.passenger = NEW.passenger AND T.status='completed')
		WHERE uid = NEW.passenger; 
		RETURN NEW;
	END;
$update_ptrips$ LANGUAGE plpgsql;

CREATE TRIGGER update_ptrips 
AFTER UPDATE OF status ON Trips
FOR EACH ROW
EXECUTE PROCEDURE passenger_trips_update();

