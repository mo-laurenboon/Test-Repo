import os
import requests
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

token = os.environ.get("WAQI_TOKEN")
if not token:
    raise SystemExit("Could not find data access token in environment")

London = requests.get(f"https://api.waqi.info/feed/@5724/?token={token}")
#Paris  = requests.get(f"https://api.waqi.info/feed/@5722/?token={token}")

cities = [London]#, Paris]
raw_city_data = {}
filtered_city_dictionary = {}
target_date = datetime.now().strftime("%Y-%m-%d")

pollutants = ["o3", "pm10", "pm25"]
print_raw_dataset = False

for city in cities:
    raw_city_data[city] = city.json()
    city_name = raw_city_data[city]["data"]["city"]["name"]

    # filter through any nested or listed dictionaries to extract required data
    filtered = {
        "Status" : raw_city_data[city].get("status"),
        "AQI" : raw_city_data[city]["data"].get("aqi"),
        "Dominant pollutant": raw_city_data[city]["data"].get("dominentpol"),
        "Temperature" : raw_city_data[city]["data"]["iaqi"].get("t"),
        "Wind Speed" : raw_city_data[city]["data"]["iaqi"].get("w"),
        "forecast" : {}
    }

    #grab forecasts only for the correct date, flatten data out of a single>
    for pollutant in pollutants:
        forecast_dict = raw_city_data[city]["data"]["forecast"]["daily"].get(pollutant)
        match = [item for item in forecast_dict if item["day"] == target_date]
        remove_dict_from_list = match[0]
        for name, data in remove_dict_from_list.items():
            if not data:
                continue
            cleaned_match = {key:value for key, value in remove_dict_from_list.items() if key!="day"}
        filtered["forecast"][pollutant] = cleaned_match

    filtered_city_dictionary[city_name] = filtered

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("daily-air-quality-template.html")

#populate the html template
column_names = ["measure", "values"]
html = template.render(
    city_name = city_name,
    columns = column_names,
    data = filtered_city_dictionary
)

directory = Path(__file__).resolve().parent.parent / "air_quality_data"
directory.mkdir(exist_ok =True)
html_filename = Path(f"{city_name}_{target_date}.html")
json_filename = Path(f"{city_name}_{target_date}.json")
html_filepath = directory / html_filename
json_filepath = directory / json_filename

if html_filepath.exists() and json_filepath.exists():
    pass
else:
    with open(html_filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\npopulated html saved as {html_filename}")

    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(filtered_city_dictionary, f, indent=4)
    print(f"\ndictionary saved as {json_filename}")