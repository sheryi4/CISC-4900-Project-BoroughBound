ALTER TABLE Trips ADD COLUMN drating REAL CHECK (drating >= 0 AND drating <= 5);
ALTER TABLE Trips ADD COLUMN prating REAL CHECK (prating >= 0 AND prating <= 5);

UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 35;
UPDATE Trips SET (prating, drating) = (4.0, 4.5) WHERE tid = 33;
UPDATE Trips SET (prating, drating) = (4.5, 5.0) WHERE tid = 34;
UPDATE Trips SET (prating, drating) = (3.0, 3.5) WHERE tid = 25;
UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 26;
UPDATE Trips SET (prating, drating) = (2.0, 3.5) WHERE tid = 27;
UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 28;
UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 29;
UPDATE Trips SET (prating, drating) = (1.5, 4.0) WHERE tid = 36;
UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 31;
UPDATE Trips SET (prating, drating) = (5.0, 5.0) WHERE tid = 30;
UPDATE Trips SET (prating, drating) = (0.5, 0.5) WHERE tid = 32;