from flask import Flask, render_template, request, jsonify, redirect
import requests
from datetime import datetime
from zeep import Client

app = Flask(__name__)
pageTitle = "Weather Forecast"

# the weather daat retrieved through Weather API in JSON
weather_data = None
# list storing the number of days of data to be retrieved
days = []
# city for which weather data is retreived
city = None;
# list storing min and max temp in celsius for 'num_days'
three_day_min_max_cel_list = []

@app.route('/')
def index():
    return render_template('get_weather.html', pageTitle = pageTitle)


@app.route('/get_weather', methods=['GET','POST'])
def get_weather():
    """
        Fetches data from the Weather API for the city and days received through input form.
        Calls the get_weather_in_fahrenheit to display forecast data in fahrenheit.
        :param : none
        :return: get_weather.html template that displays the weather information.
    """
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
        weather_data = requests.get(url, headers=headers, params=querystring).json()
        days = list(range(1, num_days+1))

        return redirect("/get_weather_in_fahrenheit")
    return   redirect("/")

@app.route("/get_weather_in_fahrenheit", methods=['GET','POST'])
def get_weather_in_fahrenheit():
    """
        Displays the weather data on Fahrenheit temp scale.
        :param : none
        :return: get_weather.html template that displays the weather information.
    """
    try:
        # call helper method to fetch 'num_days' min and max temp in fahrenheit to display in the '`num_day` Forecast section'
        three_day_min_max_fah_list = _helper_get_three_day_minmax(days, weather_data)
        # call helper method to format temp in format xx.x
        formatted_list = _helper_format_temp_value(three_day_min_max_fah_list)
        # call helper method to create a list containing a sublist storing all forecast values for each day
        three_day_forecast_list = _helper_get_three_day_forecast(days, formatted_list, weather_data)

        return render_template('get_weather.html', pageTitle=pageTitle, weather_data=weather_data,
                               city=city, days=days, hours=list(range(24)), days_count=len(days),  low="L: ", high="H: ",
                               hourly_forecast_header="HOURLY FORECAST", current_condition=three_day_forecast_list[0][5],
                               temp_scale="°F", current_temp=weather_data['current']['temp_f'], current_max_temp=three_day_forecast_list[0][0],
                               current_min_temp=three_day_forecast_list[0][1], three_day_forecast_list=three_day_forecast_list,
                               button_value="View in °C", three_day_forecast_header="-DAY FORECAST")
    except Exception as e:
        return render_template('get_weather.html', pageTitle=pageTitle,error_message="Please enter form details.")



@app.route("/get_weather_in_celsius", methods=['GET','POST'])
def get_weather_in_celsius():
    """
        Displays data on page header and the 'num_days' forecast data on Celsius temp scale.
        Invokes SOAP service to convert Fahrenheit to Celsius using a public API.
        :param : none
        :return: get_weather.html template that displays the weather information in Celsius
    """
    global weather_data, days, city
    # clear list each time a call is made to this route.
    three_day_min_max_cel_list = []
    try:
        # call helper method to fetch 'num_days' min and max temp in fahrenheit to display in the '`num_day` Forecast section'
        three_day_min_max_fah_list = _helper_get_three_day_minmax(days, weather_data)
        # Make API call to convert Fahrenheit to Cesius
        if request.method == "POST":
            service_url = "https://www.w3schools.com/xml/tempconvert.asmx?WSDL"
            client = Client(service_url)
            current_temp = weather_data['current']['temp_f']
            # convert today's current temp to Celsius (displayed on page header)
            request_data = {
                'Fahrenheit': current_temp
            }
            current_temp_cel = client.service.FahrenheitToCelsius(**request_data)

            # convert 'num_days' min and max temp to Celsius (displayed on '`num_days` forecast' section.
            for each_day in three_day_min_max_fah_list:
                request_data = {
                    'Fahrenheit': each_day
                }
                three_day_min_max_cel_list.append(client.service.FahrenheitToCelsius(**request_data))
            # call helper method to format temp in format xx.x
            formatted_list = _helper_format_temp_value(three_day_min_max_cel_list)
            # call helper to create a list containing a sublist storing all forecast values for each day
            three_day_forecast_list = _helper_get_three_day_forecast(days, formatted_list, weather_data)

            return render_template('get_weather.html', pageTitle=pageTitle, weather_data=weather_data,
                                   city=city, days=days, hours=list(range(24)), days_count=len(days),
                                   hourly_forecast_header="HOURLY FORECAST", temp_scale = "°C", low="L: ", high="H: ",
                                   current_temp=round(float(current_temp_cel),1), current_condition = three_day_forecast_list[0][5],
                                   current_max_temp=round(float(three_day_forecast_list[0][0]),1),
                                   current_min_temp=round(float(three_day_forecast_list[0][1]),1),
                                   three_day_forecast_list=three_day_forecast_list, button_value="View in °F", three_day_forecast_header="-DAY FORECAST")
        return redirect("/")
    except Exception as e:
        return render_template('get_weather.html',pageTitle=pageTitle, error_message="Please enter form details.")



def _helper_format_temp_value(three_day_min_max_list):
    """
        Formats temp to store data in format xx.x
        :param : three_day_min_max_list : list storing 'num_days' min and max temp values
        :return: formatted_list : list storing temp in the format xx.x
    """
    formatted_list = []
    for temp in three_day_min_max_list:
        formatted_list.append(round(float(temp), 1))
    return formatted_list


def _helper_get_three_day_forecast(days, three_day_min_max_cel_list, weather_data):
    """
        Creates a list containing a sublist that stores the values for all forecast factors for each day
        Ex: [[11/03/2028, 6:45AM, 7:40PM, cloudy, 1, 81.0, 0.24, 16.8, 94], [......], [.......]]
        :param : days : number of days of forecast required. Equal to 'num_days'
                three_day_min_max_cel_list : min and max temp values formatted in the format xx.x for 'num_days'
                weather_data : weather data retreived from the weather API
        :return: three_day_forecast_list : list storing sublists that stores the values for all forecast factors for each day
    """
    three_day_forecast_list = []
    # formatting the flat list into sublists containing 2 values for min and max temp.
    for i in range(0, len(three_day_min_max_cel_list), 2):
        each_day = three_day_min_max_cel_list[i:i + 2]
        three_day_forecast_list.append(each_day)
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

        # Add all forecast factor values to the corresponding each_day sublist
        three_day_forecast_list[day - 1].extend([date, sunrise, sunset, condition, uv,avghumidity, totalprecip, maxwind, chance_of_rain])
    return three_day_forecast_list


def _helper_get_three_day_minmax(days, weather_data):
    """
        Creates a list containing the 'num_days' min and max temp values. This list is further used to convert values from F to C.
        :param : days : number of days of forecast required. Equal to 'num_days'
                weather_data : weather data retreived from the weather API
        :return: three_day_min_max_fah_list : list storing 'num_days' min and max temp in fahrenheit
    """
    three_day_min_max_fah_list = []
    for day in days:
        current_max_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['maxtemp_f']
        current_min_temp_fah = weather_data['forecast']['forecastday'][day - 1]['day']['mintemp_f']
        three_day_min_max_fah_list.extend([current_max_temp_fah, current_min_temp_fah])
    return three_day_min_max_fah_list




if __name__ == '__main__':
    app.run(debug=True)

