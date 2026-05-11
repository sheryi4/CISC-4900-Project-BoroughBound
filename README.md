# CISC-4900-Project
Project for CISC 4900
BoroughBound

Let’s be real: national apps don't know the BQE like we
do. BoroughBound was built for the people who actually
live here—the ones tired of being 'ghosted' by drivers
because they’re heading to deep Brooklyn or the Bronx.
We know exactly where the subway gaps are and how to
navigate around the gridlock. No corporate fluff, just
local drivers getting you across the five boroughs
without the 'tourist' tax. We’re New York’s ride, not an
algorithm's.

Tools intended for use:
Python 3.14.2: Backend logic & API integration
Flask 3.1.x: Web framework for API endpoints
PostgreSQL 18.2: Database storage for rides, users, drivers
SQLAlchemy 2.0.46: Database Management
React 18: Frontend interface Google Maps API Latest Geolocation, route mapping
JSON : Messages, Alerts, Updates
Git & GitHub: Version control

***
Setup
To apply the database schema, do the following::

psql -U <uni> -h w4111a.eastus.cloudapp.azure.com proj1part2 -a -f schema/schema.sql    

***
Create virtualenv, activate it and do

pip install -r requirements.txt
	
***
Run
To run the development server, do

python server.py

from the appropriate folder.

