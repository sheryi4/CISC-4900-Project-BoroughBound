ALTER TABLE Trips ADD COLUMN review TEXT;

UPDATE Trips SET review = 'Frank was on time and his car was clean, but he was chatting on his phone for half of the trip.  That doesn''t seem safe, I would prefer my driver focused on the road' WHERE tid = 25;
UPDATE Trips SET review = 'Karen was great!  Arrived right on time, car was spotless, and we got to destination quickly.' WHERE tid=26;
UPDATE Trips SET review = 'My trips was ok.  I only gave a 3.5 rating because my driver took a longer route to get there then they should have.  I told him to take the FDR!' WHERE tid=27;
UPDATE Trips SET review = 'Barbara is a great driver!  Her car is clean and new, she was prefectly on time, and she somehow knew how to avoid all the traffic.  Plus, she''s a Mets fan!  We talked about their pitching issues the whole ride.' WHERE tid = 28;
UPDATE Trips SET review = 'My driver was great, got to my destination on time.  Nothing more to say.' WHERE tid= 29; 
UPDATE Trips SET review = 'I don''t know how you screen your drivers, but you need to do better!  Barbara was twenty minutes late, and her car was a mess!  On top of that, she almost crashed into a UPS truck!  This was by the far the worst experience I''ve had with your service.' WHERE tid = 32; 
UPDATE Trips SET review = 'Judith was pretty good.  I had no issues with my trip, and she has good choice in music.' WHERE tid = 33;
UPDATE Trips SET review = 'Craig is an awesome driver.  His car is pristine, and he has satellite radio.  He let me pick the station, which was nice.  Plus he had phone chargers, always appreciated.' WHERE tid = 34; 
UPDATE Trips SET review = 'Martha is the coolest driver.  She was early to pick me up, and she told me stories about growing up in NYC in the 70s!' WHERE tid = 35; 
UPDATE Trips SET review = 'I didn''t have a very good experience on this trip.  My driver was 10 minutes late, which I could forgive (traffic is traffic), but he was also extremely rude and his car was dirty.  If I want to deal with that kind of attitude, I''ll just take a taxi.  You really need to talk to your drivers abaout thd importance of being polite and maintaining their cars.' WHERE tid = 43;

