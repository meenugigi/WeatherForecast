from flask import Flask, render_template, request, jsonify, redirect
import requests
from datetime import datetime
from zeep import Client

app = Flask(__name__)
pageTitle = "Weather Forecast"

weather_data = None
days = []
hours = list(range(24))
days_count = 0
city = None;
three_day_min_max_cel_list = []

@app.route('/')
def index():
    return render_template('get_weather.html', result="", pageTitle = pageTitle)


@app.route('/get_weather', methods=['GET','POST'])
def get_weather():
    global weather_data, days, city

    if request.method == "POST":
        # city for data requested
        city = request.form['city']
        # num of days of data requested
        num_days = int(request.form['num_days'])

        # Make request to the Weather API
        url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
        querystring = {"q": city, "days": num_days}
        headers = {
            "X-RapidAPI-Key": "1f67aed425mshbbc3cb4d2bf13fap14b3f4jsne50da4bb50e2",
            "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        # stroing the response as weather_data
        weather_data = response.json()
        days = list(range(1, num_days+1))
        days_count = len(days)

        # call helper method to fetch current, min and max temp in fahrenheit
        current_temp_fah, current_max_temp_fah, current_min_temp_fah, temp_to_convert = (
            _helper_get_current_forecast_fah(days, weather_data))

        # call helper method to fetch 'num_days' min and max temp in fahrenheit
        three_day_min_max_fah_list = _helper_get_three_day_minmax(days, weather_data)
        # format temp to store data in format XX.X
        formatted_list = [f'{float(value):.1f}' for value in three_day_min_max_fah_list]
        # call helper to create a list containing a sublist storing all forecast values for each day
        three_day_forecast_list = _helper_get_three_day_forecast(days, formatted_list, weather_data)

        return render_template('get_weather.html',pageTitle = pageTitle, weather_data=weather_data,
                               city=city,days=days, hours=hours, days_count=days_count, hourly_forecast_header="HOURLY FORECAST",
                               temp_scale = "F", current_temp=current_temp_fah, current_max_temp=current_max_temp_fah,
                               current_min_temp=current_min_temp_fah, three_day_forecast_list=three_day_forecast_list,
                               button_value="View in °C", three_day_forecast_header="-DAY FORECAST")
    return   redirect("/")




@app.route("/get_weather_in_celsius", methods=['GET','POST'])
def get_weather_in_celsius():
    global weather_data, days, city
    three_day_min_max_cel_list = []
    try:
        # call helper method to fetch current, min and max temp in fahrenheit
        current_temp_fah, current_max_temp_fah, current_min_temp_fah, current_day_temp_to_convert = (
            _helper_get_current_forecast_fah(days, weather_data))

        # call helper method to fetch 'num_days' min and max temp in fahrenheit
        three_day_min_max_fah_list = _helper_get_three_day_minmax(days, weather_data)


        temp_in_cel_list=[]
        # Make API call to convert Fahrenheit to Cesius
        if request.method == "POST":
            service_url = "https://www.w3schools.com/xml/tempconvert.asmx?WSDL"
            client = Client(service_url)
            # convert current day's current, min and max temp to Celsius
            for temp in current_day_temp_to_convert:
                request_data = {
                    'Fahrenheit': temp
                }
                temp_in_cel_list.append(client.service.FahrenheitToCelsius(**request_data))

            # convert 'num_days' min and max temp to Celsius
            for each_day in three_day_min_max_fah_list:
                request_data = {
                    'Fahrenheit': each_day
                }
                three_day_min_max_cel_list.append(client.service.FahrenheitToCelsius(**request_data))
            print('three_day_min_max_fcel_list', three_day_min_max_cel_list)
            # format temp to store data in format XX.X
            formatted_list = [f'{float(value):.1f}' for value in three_day_min_max_cel_list]
            # call helper to create a list containing a sublist storing all forecast values for each day
            three_day_forecast_list = _helper_get_three_day_forecast(days, formatted_list, weather_data)
            print(three_day_forecast_list)

            return render_template('get_weather.html', pageTitle=pageTitle, weather_data=weather_data,
                                   city=city, days=days, hours=hours, days_count=days_count,
                                   hourly_forecast_header="HOURLY FORECAST", temp_scale = "C",
                                   current_temp=round(float(temp_in_cel_list[0]),1),
                                   current_max_temp=round(float(temp_in_cel_list[1]),1),
                                   current_min_temp=round(float(temp_in_cel_list[2]),1),
                                   three_day_forecast_list=three_day_forecast_list, button_value="View in °F", three_day_forecast_header="-DAY FORECAST")
        return redirect("/")
    except Exception as e:
        # Handle the exception here, e.g., log the error or render an error page.
        return render_template('get_weather.html',pageTitle=pageTitle, error_message="Please enter form details.")



@app.route("/get_weather_in_fahrenheit", methods=['GET','POST'])
def get_weather_in_fahrenheit():
    global weather_data, days, city, three_day_min_max_cel_list
    try:
        # call helper method to fetch current, min and max temp in fahrenheit
        current_temp_fah, current_max_temp_fah, current_min_temp_fah, current_day_temp_to_convert = (
            _helper_get_current_forecast_fah(days, weather_data))

        # call helper method to fetch 'num_days' min and max temp in fahrenheit
        three_day_min_max_fah_list = _helper_get_three_day_minmax(days, weather_data)

        # format temp to store data in format XX.X
        formatted_list = [f'{float(value):.1f}' for value in three_day_min_max_fah_list]
        # call helper to create a list containing a sublist storing all forecast values for each day
        three_day_forecast_list = _helper_get_three_day_forecast(days, formatted_list, weather_data)

        return render_template('get_weather.html', pageTitle=pageTitle, weather_data=weather_data,
                               city=city, days=days, hours=hours, days_count=days_count,
                               hourly_forecast_header="HOURLY FORECAST", temp_scale = "F",
                               current_temp=current_temp_fah, current_max_temp=current_max_temp_fah,
                               current_min_temp=current_min_temp_fah,
                               three_day_forecast_list=three_day_forecast_list, button_value="View in °C", three_day_forecast_header="-DAY FORECAST")
    except Exception as e:
        # Handle the exception here, e.g., log the error or render an error page.
        return render_template('get_weather.html', pageTitle=pageTitle,error_message="Please enter form details.")
# return redirect("/")

def _helper_get_three_day_forecast(days, three_day_min_max_cel_list, weather_data):
    three_day_forecast_list = []
    # formatting the flat list into sublists containing 2 values each
    # each sublist contains 2 values: min temp and max temp
    for i in range(0, len(three_day_min_max_cel_list), 2):
        each_day = three_day_min_max_cel_list[i:i + 2]
        three_day_forecast_list.append(each_day)
    # print(three_day_forecast_list)
    # inserting other values into each sublist containing min temp and max temp values
    for day, (max_temp, min_temp) in zip(days, three_day_forecast_list):
        date = weather_data['forecast']['forecastday'][day - 1]['date']
        sunrise = weather_data['forecast']['forecastday'][day - 1]['astro']['sunrise']
        sunset = weather_data['forecast']['forecastday'][day - 1]['astro']['sunset']
        condition = weather_data['forecast']['forecastday'][day-1]['day']['condition']['text']
        uv = weather_data['forecast']['forecastday'][day-1]['day']['uv']
        avghumidity = weather_data['forecast']['forecastday'][day-1]['day']['avghumidity']
        totalprecip = weather_data['forecast']['forecastday'][day-1]['day']['totalprecip_in']
        maxwind = weather_data['forecast']['forecastday'][day-1]['day']['maxwind_mph']
        chance_of_rain = weather_data['forecast']['forecastday'][day-1]['day']['daily_chance_of_rain']

        # Add sunrise and sunset to the corresponding each_day
        three_day_forecast_list[day - 1].extend([date, sunrise, sunset, condition, uv,avghumidity, totalprecip, maxwind, chance_of_rain])
    return three_day_forecast_list


def _helper_get_three_day_minmax(days, weather_data):
    three_day_min_max_fah_list = []
    for day in days:
        current_max_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['maxtemp_f']
        current_min_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['mintemp_f']
        three_day_min_max_fah_list.extend([current_max_temp_fah, current_min_temp_fah])
    return three_day_min_max_fah_list


def _helper_get_current_forecast_fah(days, weather_data):
    temp_to_convert =[]
    current_temp_fah = weather_data['current']['temp_f']
    for day in days:
        if day == 1:
            current_max_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['maxtemp_f']
            current_min_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['mintemp_f']

            temp_to_convert.extend([current_temp_fah, current_max_temp_fah, current_min_temp_fah])
    return  current_temp_fah, current_max_temp_fah, current_min_temp_fah, temp_to_convert


if __name__ == '__main__':
    app.run(debug=True)

