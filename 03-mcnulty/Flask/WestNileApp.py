import flask
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from catboost import CatBoostClassifier, Pool, cv

#---------- MODEL IN MEMORY ----------------#

# Connect to postgres sql server and load dataframes
cnx = create_engine('postgresql://ubuntu:ubuntu@18.236.147.215:5432/weather')
weather = pd.read_sql_query('''SELECT * FROM weather''',cnx,index_col="id")
trap_stations = pd.read_sql_query('''SELECT * FROM traps_stations''',cnx,index_col="id")

# Load up the fitted Catboost Model
fname = "WNVcatboost_model"
sss = CatBoostClassifier()
loaded_model = sss.load_model(fname)

# Function for identifying the closest trap to the chosen location
def find_closest_trap(lat, lng, df):
    loc = np.array([lat,lng])
    traps = df.groupby(["trap"]).agg("mean").reset_index()
    trap = traps[["latitude", "longitude"]].values
    return traps.iloc[np.argmin(((trap-loc[None,:])**2).sum(1)),0]


#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    with open("WNVWeb.html", 'r') as viz_file:
        return viz_file.read()

# Get an example and return it's score from the predictor model
@app.route("/prob", methods=["POST"])
def prob():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, predict probability and
    send it with a response
    """
    # Get decision score for our example that came with the request
    data = flask.request.json
    #data[]
    year = data["year"]
    Month = data["month"]
    Day = data["day"]
    species = data["species"]
    lat = data["lattitude"]
    lng = data["longitude"]

    # find the closest trap to the clicked location
    closest_trap = find_closest_trap(lat,lng,trap_stations)
    trap = trap_stations[(trap_stations.trap == closest_trap) & (trap_stations.species == species)]
    
    # add 0 in front of month
    month = "0"+ Month if len(Month) == 1 else Month
    day = "0"+ Day if len(Day) == 1 else Day
    date = year + "-" + month + "-" + day
    trap["date"] = date

    # convert datetime to str to match differing formats
    weather.station = weather.station.astype(str)
    trap.station = trap.station.astype(int).astype(str)
    weather.date = weather.date.astype(str)

    # merge trap & weather dataframes
    merged = trap.merge(weather,on=["date","station"],how="inner")

    # convert back datetime
    merged.date = pd.to_datetime(merged.date)

    # extract features from datetime and dewpoint
    merged['month'] = month
    merged['year'] = year
    merged['dry'] = merged['dewpoint'].subtract(merged.wetbulb)
    merged['week'] = merged['date'].map(lambda x: str(x.isocalendar()[1]))
    # add risk feature if month is between june and sept (peak virus season)
    merged['risk'] = 1 if (int(month) > 6) and (int(month) < 9) else 0

    # Reorder columns & Assign to X
    merged2 = merged.drop(["date", "year", "trap","species"],1)
    cols = ["month","week","longitude","latitude","tmax","tmin","tavg","depart","dewpoint",
        "wetbulb","heat","cool","sunrise","sunset","preciptotal","resultspeed","avgspeed",
        "month","dry","risk"]
    X = merged2[cols]
    
    # predict probability
    pred = loaded_model.predict_proba(X)
    prob = round(pred[0][1]*100,2)
    return flask.jsonify(prob)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
# app.run(host='0.0.0.0')
# app.run(debug=True)
