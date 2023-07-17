from logging import basicConfig
import folium
from flask import Blueprint, render_template, flash, request, redirect, url_for, session, abort
from flask_login import login_required, current_user
from __init__ import create_app, db
import pickle
from flask_bootstrap import Bootstrap
import pandas as pd
from models import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import User, Blogpost
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import cross_origin
import requests
import json                                                                                         
import re                                                                                         
import urllib.request                                                                                      
import os                                                                                           
import subprocess 

main = Blueprint('main', __name__)

model = pickle.load(open('model.pkl', 'rb'))
cat = pickle.load(open('cat.pkl', 'rb'))


@main.route('/')
def index():

    return render_template('index.html')
    # return render_template('index.html')


@main.route('/profile')  # profile page that return 'profile'
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/predict')
@login_required
def hello_world():
    return render_template("fire.html")


@main.route('/predict', methods=['POST', 'GET'])
def predict():
    float_features = [float(x) for x in request.form.values()]
    final = [pd.array(float_features)]
    print(float_features)
    print(final)
    prediction = model.predict_proba(final)
    output = '{0:.{1}f}'.format(prediction[0][1], 2)

    if output > str(0.5):
        return render_template('fire.html', pred='Your Forest is in Danger.\nProbability of fire occuring is {}'.format(output), bhai="kuch karna hain iska ab?")
    else:
        return render_template('fire.html', pred='Your Forest is safe.\n Probability of fire occuring is {}'.format(output), bhai="Your Forest is Safe for now")


@main.route("/rain", methods=['GET'])
@login_required
def rain():
    return render_template("rainfall.html")


@main.route("/rainfall", methods=['GET', 'POST'])
@login_required
def rainfall():
    if request.method == "POST":
        # DATE
        date = request.form['date']
        day = pd.to_datetime(date, format="%Y-%m-%dT", errors='ignore').day
        month = pd.to_datetime(date, format="%Y-%m-%dT", errors='ignore').month
        # MinTemp
        minTemp = float(request.form['mintemp'])
        # MaxTemp
        maxTemp = float(request.form['maxtemp'])
        # Rainfall
        rainfall = float(request.form['rainfall'])
        # Evaporation
        evaporation = float(request.form['evaporation'])
        # Sunshine
        sunshine = float(request.form['sunshine'])
        # Wind Gust Speed
        windGustSpeed = float(request.form['windgustspeed'])
        # Wind Speed 9am
        windSpeed9am = float(request.form['windspeed9am'])
        # Wind Speed 3pm
        windSpeed3pm = float(request.form['windspeed3pm'])
        # Humidity 9am
        humidity9am = float(request.form['humidity9am'])
        # Humidity 3pm
        humidity3pm = float(request.form['humidity3pm'])
        # Pressure 9am
        pressure9am = float(request.form['pressure9am'])
        # Pressure 3pm
        pressure3pm = float(request.form['pressure3pm'])
        # Temperature 9am
        temp9am = float(request.form['temp9am'])
        # Temperature 3pm
        temp3pm = float(request.form['temp3pm'])
        # Cloud 9am
        cloud9am = float(request.form['cloud9am'])
        # Cloud 3pm
        cloud3pm = float(request.form['cloud3pm'])
        # Cloud 3pm
        location = float(request.form['location'])
        # Wind Dir 9am
        winddDir9am = float(request.form['winddir9am'])
        # Wind Dir 3pm
        winddDir3pm = float(request.form['winddir3pm'])
        # Wind Gust Dir
        windGustDir = float(request.form['windgustdir'])
        # Rain Today
        rainToday = float(request.form['raintoday'])

        input_lst = [location, minTemp, maxTemp, rainfall, evaporation, sunshine,
                     windGustDir, windGustSpeed, winddDir9am, winddDir3pm, windSpeed9am, windSpeed3pm,
                     humidity9am, humidity3pm, pressure9am, pressure3pm, cloud9am, cloud3pm, temp9am, temp3pm,
                     rainToday, month, day]
        pred1 = cat.predict(input_lst)
        output = pred1
        if output == 0:
            return render_template("after_sunny.html")
        else:
            return render_template("after_rainy.html")
    return render_template("rainfall.html")
@main.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            new_city_obj = City(name=new_city)

            db.session.add(new_city_obj)
            db.session.commit()

    cities = City.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=8bb3fea9a544fdf41e98e03c4b56d9ae'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city.name)).json()

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'humidity': r['main']['humidity'],
            'pressure': r['main']['pressure'],
            'windspeed': r['wind']['speed'],
            'icon' : r['weather'][0]['icon'],

        }

        weather_data.append(weather)


    return render_template('weather.html', weather_data=weather_data)

@main.route('/weather_new')
def weather_new():
    return render_template('weather1.html')
    
##############################################################################
@main.route("/map")
def map():
    # this is base map
    map = folium.Map(
        location=[45.52336, -122.6750]
    )
    return map._repr_html_()

@main.route("/open-street-map")
def open_street_map():
    # this map using stamen toner
    map = folium.Map(
        location=[45.52336, -122.6750],
        tiles='Stamen Toner',
        zoom_start=13
    )

    folium.Marker(
        location=[45.52336, -122.6750],
        popup="<b>Marker here</b>",
        tooltip="Click Here!"
    ).add_to(map)
    
    return map._repr_html_()

@main.route("/map-marker")
def map_marker():
    # this map using stamen terrain
    # we add some marker here
    map = folium.Map(
        location=[45.52336, -122.6750],
        tiles='Stamen Terrain',
        zoom_start=12
    )

    folium.Marker(
        location=[45.52336, -122.6750],
        popup="<b>Marker here</b>",
        tooltip="Click Here!"
    ).add_to(map)

    folium.Marker(
        location=[45.55736, -122.8750],
        popup="<b>Marker 2 here</b>",
        tooltip="Click Here!",
        icon=folium.Icon(color='green')
    ).add_to(map)

    folium.Marker(
        location=[45.53236, -122.8750],
        popup="<b>Marker 3 here</b>",
        tooltip="Click Here!",
        icon=folium.Icon(color='red')
    ).add_to(map)

    return map._repr_html_()
##########################################################
# class area:
#     def __init__(self, key, name, lat, lng):
#         self.key  = key
#         self.name = name
#         self.lat  = lat
#         self.lng  = lng
# areas = (
#     area('hv',      'Happy Valley Elementary',   37.9045286, -122.1445772),
#     area('stanley', 'Stanley Middle',            37.8884474, -122.1155922),
#     area('wci',     'Walnut Creek Intermediate', 37.9093673, -122.0580063)
# )
# areas_by_key = {area.key: area for area in areas}


# @main.route("/map")
# def map():
#     return render_template('map1.html', area=areas)


# @main.route("/map/<area_code>")
# def show_rain(area_code):
#     area= areas_by_key.get(area_code)
#     if area:
#         return render_template('map.html', area = area)
#     else:
#         abort(404)





##############################################################################


# /<int:post_id>
@main.route('/upload')
@login_required
def upload():
    return render_template('base1.html')


app = create_app()
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Blogpost, db.session))
admin.add_view(ModelView(FileContents, db.session))
admin.add_view(ModelView(City, db.session))

if __name__ == '__main__':
    db.create_all(app=create_app())
    app.run(debug=True, port=5000)
