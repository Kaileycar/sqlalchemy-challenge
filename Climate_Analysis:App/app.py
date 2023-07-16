# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new modelase
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

### Home route ###
@app.route("/")
def Home():
    # List all available api routes
    return (
        f"Available Routes:<br>"
        f"<br>"
        f"Precipitation: " \
        f"/api/v1.0/precipitation<br>"
        f"Stations: " \
        f"/api/v1.0/stations<br>"
        f"Temperature Observations: " \
        f"/api/v1.0/tobs<br>"
        f"Any Start Date Temperature Statistics: " \
        f"/api/v1.0/start/<start><br>"
        f"Any Start to End Date Temperature Observations: " \
        f"/api/v1.0/start_end/<start>/<end><br>"
        f"<br>"
        f"NOTE: Start and End dates are YYYY-MM-DD"
    )

### Preciptation route ###
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query last 12 months of data
    year_ago = '2016-08-23'
    result = session.query(Measurement.date, Measurement.prcp). \
    filter(Measurement.date >= year_ago). \
    order_by(Measurement.date).all()

    # Close Session
    session.close()

    # Convert query to dictionary with date as key and prcp as value
    all_dates = []
    for item in result:
        date_dict = {}
        date_dict[item[0]] = item[1]
        all_dates.append(date_dict)
        
    # Return Json 
    return jsonify(all_dates)

### Station Route ###
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations from dataset
    results = session.query(Station.name, Station.station).all()

    # Convert into list
    # all_stations = list(np.ravel(station))

     # Close Session
    session.close()

    all_stations = []
    for name, station in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["station"] = station
        all_stations.append(station_dict)

    # Return Json
    return jsonify(all_stations)

### Tobs Route ###
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create variable for most active station
    most_active = session.query(Measurement.station, func.count(Measurement.id)). \
    group_by(Measurement.station). \
    order_by(func.count(Measurement.id).desc()).first()

    # Query dates and temp for most active station
    year_ago = '2016-08-23'
    active_station_temp = session.query(Measurement.date, Measurement.tobs). \
                  filter(Measurement.date >= year_ago). \
                  filter(Measurement.station == most_active[0]).all()
    
     # Close Session
    session.close()

    # Convert into list of dictionaries
    all_tobs = []
    for date, tobs in active_station_temp:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    # Return Json
    return jsonify(all_tobs)

### Start route ###
@app.route("/api/v1.0/start/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Fetch the min, max, and avg tobs for date >= to start
    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    
    start_date = session.query(*sel). \
                 filter(Measurement.date >= start).all()
    
     # Close Session
    session.close()
    
    # Convert into a list of dictionaries
    start_list = []
    for min, avg, max in start_date:
        start_dict = {}
        start_dict["Start Date"] = start
        start_dict["min"] = min
        start_dict["avg"] = avg
        start_dict["max"] = max
        start_list.append(start_dict)

    # Return Json
    return jsonify(start_list)

### Start and End Route ###
@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query min, abg, max tobs of a start and end date
    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    
    start_end_date = session.query(*sel). \
                 filter(Measurement.date >= start). \
                 filter(Measurement.date <= end).all()
    
     # Close Session
    session.close()
    
    # Convert into a list of dictionaries
    start_end_list = []
    for min, avg, max in start_end_date:
        start_end_dict = {}
        start_end_dict["Start Date"] = start
        start_end_dict["End Date"] = end
        start_end_dict["min"] = min
        start_end_dict["avg"] = avg
        start_end_dict["max"] = max
        start_end_list.append(start_end_dict)

    # Return Json
    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)