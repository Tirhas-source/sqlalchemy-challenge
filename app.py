import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#database set up


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
base = automap_base()
#reflect the tables
base.prepare(engine, reflect=True)

#save references to each table
measurement = base.classes.measurement
station = base.classes.station

#creating a session link from Python
session = Session(engine)

#Flask set up

app= Flask(__name__)


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation data: /api/v1.0/precipitation<br/>"
        f"List of Stations in database: /api/v1.0/stations<br/>"
        f"Temperature for the past year: /api/v1.0/tobs<br/>"
        f"Temperature stat from a start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from a start to a end date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/<start>')
def startdate(start):
    session = Session(engine)
    querystart = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    alltobs = []
    for min,avg,max in querystart:
        tobsdict = {}
        tobsdict["Min"] = min
        tobsdict["Average"] = avg
        tobsdict["Max"] = max
        alltobs.append(tobsdict)

    return jsonify(alltobs)

@app.route('/api/v1.0/<start>/<stop>')
def getdates(start,stop):
    session = Session(engine)
    querydate = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()

    alltobs = []
    for min,avg,max in querydate:
        tobsdict = {}
        tobsdict["Min"] = min
        tobsdict["Average"] = avg
        tobsdict["Max"] = max
        alltobs.append(tobsdict)

    return jsonify(alltobs)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    lastdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    yearago = dt.date(lastdate.year -1, lastdate.month, lastdate.day)
    sel = [measurement.date,measurement.tobs]
    queryresulttobs = session.query(*sel).filter(measurement.date >= yearago).all()
    session.close()

    alltobs = []
    for date, tobs in queryresulttobs:
        tobsdict = {}
        tobsdict["Date"] = date
        tobsdict["Tobs"] = tobs
        alltobs.append(tobsdict)

    return jsonify(alltobs)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [stationtbl.station,stationtbl.name,stationtbl.latitude,stationtbl.longitude,stationtbl.elevation]
    querystation= session.query(*sel).all()
    session.close()

    stationslist = []
    for station,name,lat,lon,el in querystation:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stationslist.append(station_dict)

    return jsonify(stationslist)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [measurement.date,measurement.prcp]
    precipquery = session.query(*sel).all()
    session.close()

    precipitationlist = []
    for date, prcp in precipquery:
        prcpdict = {}
        prcpdict["Date"] = date
        prcpdict["Precipitation"] = prcp
        precipitationlist.append(prcpdict)

    return jsonify(precipitationlist)

if __name__ == '__main__':
    app.run(debug=True)