from flask import Flask, render_template, request, jsonify, redirect
import requests
from datetime import datetime

app = Flask(__name__)
pageTitle = "Weather Forecast"
@app.route('/')
def index():
    return render_template('get_weather.html', result="", pageTitle = pageTitle)


@app.route('/get_weather', methods=['GET','POST'])
def get_weather():
    if request.method == "POST":
        city = request.form['city']
        num_days = int(request.form['num_days'])

        # Make the request to the Weather API
        url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
        querystring = {"q": city, "days": num_days}
        headers = {
            "X-RapidAPI-Key": "1f67aed425mshbbc3cb4d2bf13fap14b3f4jsne50da4bb50e2",
            "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)

        weather_data = response.json()
        days = list(range(1, num_days+1))
        hours = list(range(24))
        days_count = len(days)

        return render_template('get_weather.html',pageTitle = pageTitle, weather_data=weather_data,
                               city=city,days=days, hours=hours, days_count=days_count)
    return   redirect("/")



if __name__ == '__main__':
    app.run(debug=True)

