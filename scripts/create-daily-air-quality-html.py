import os
import requests
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def get_access_token(token_name):
    """
    Retreives relvent access token from GitHub secrets.

        :param token_name: The name of the desired token as stored in GitHub secrets.
        :returns: Token name.
        :raises SystemExit: Script fails if unable to access the required token.
    """
    token = os.environ.get(token_name)
    if not token:
        raise SystemExit("Could not find data access token in environment")
    return token


def filter_air_quality_data(raw_city_data, city):
    """
    Takes the raw data from the database and filters it to give the required fields as a dictionary format.

        :param raw_city_data: The raw dataset taken directly from the accessed database.
        :param city: The database repsonse for the desired city.
        :returns: The name of the city and its associated filtered data dictionary containing an empty nested dictionary
        for forecast data.
        :raises None: None.
    """
    city_name = raw_city_data[city]["data"]["city"]["name"]
    filtered_data = {
        "Status" : raw_city_data[city].get("status"),
        "AQI" : raw_city_data[city]["data"].get("aqi"),
        "Dominant pollutant": raw_city_data[city]["data"].get("dominentpol"),
        "Temperature" : raw_city_data[city]["data"]["iaqi"].get("t"),
        "Wind Speed" : raw_city_data[city]["data"]["iaqi"].get("w"),
        "forecast" : {}
    }
    return city_name, filtered_data


def get_pollutant_data(raw_city_data, city, target_date, filtered_data):
    """
    Sorts the nested pollution data dictionaries to give only the target date forecast, removes them from single item 
    lists and removes unwanted key-value pairs (e.g. the date entry).

        :param raw_city_data: The raw dataset taken directly from the accessed database.
        :param city: The database repsonse for the desired city.
        :param target_date: The date associated with the data taken from the database (set to take the current date).
        :param filtered_data: The filtered dataset for each city containing an empty nested dictionary for forecast 
        data.
        :returns: The final filtered dictionary dataset with the added pollution forecast. 
        :raises None: None.
    """
    pollutants = ["o3", "pm10", "pm25"]
    for pollutant in pollutants:
        forecast_dict = raw_city_data[city]["data"]["forecast"]["daily"].get(pollutant)
        match = [item for item in forecast_dict if item["day"] == target_date]
        remove_dict_from_list = match[0]
        #for name, data in remove_dict_from_list.items():
        for data in remove_dict_from_list.items():
            if not data:
                continue
            cleaned_match = {key:value for key, value in remove_dict_from_list.items() if key!="day"}
        filtered_data["forecast"][pollutant] = cleaned_match
    return filtered_data


def get_html_template(template_directory, template_name):
    """
    Initialises the environement to load the desired html template.

        :param template_directory: The name of the directory where the desired html template is stored.
        :param template_name: The name of the desried html template.
        :returns: Unpopulated html template. 
        :raises None: None
    """
    env = Environment(loader=FileSystemLoader(template_directory))
    template = env.get_template(template_name)
    return template


def render_html_template(city_name, filtered_city_dictionary):
    """
    Renders and populates the html template with data from the complete filtered data dictionary.

        :param city_name: The name of the city.
        :param filtered_city_dictionary: The final filtered dictionary dataset with the added pollution forecast. 
        :returns: Populated html file.
        :raises None: None
    """
    column_names = ["measure", "values"]
    template = get_html_template("templates", "daily-air-quality-template.html")
    html = template.render(
        city_name = city_name,
        columns = column_names,
        data = filtered_city_dictionary
    )
    return html


def create_directory_and_filenames(directory_name, city_name, target_date):
    """
    Creates the save directory for files and generates filenames for the populated html and json dictionary file using 
    the location and target date.

        :param directory_name: The desired name for the directory into which the files will be saved.
        :param city_name: The name of the city.
        :param target_date: The date associated with the data taken from the database (set to take the current date).
        :returns: The complete filepath and filename of the new html and json files.
        :raises None: None
    """
    directory = Path(__file__).resolve().parent.parent/directory_name
    directory.mkdir(exist_ok =True)

    html_filename = Path(f"{city_name}_{target_date}.html")
    json_filename = Path(f"{city_name}_{target_date}.json")

    html_filepath = directory / html_filename
    json_filepath = directory / json_filename
    return html_filepath, json_filepath


def save_files(city_name, target_date, filtered_city_dictionary):
    """
    Saves the files to their predefined filepaths.

        :param city_name: The name of the city.
        :param target_date: The date associated with the data taken from the database (set to take the current date).
        :param filtered_city_dictionary: The final filtered dictionary dataset with the added pollution forecast.
        :returns: None
        :raises None: None
    """
    html = render_html_template(city_name, filtered_city_dictionary)
    html_filepath, json_filepath = create_directory_and_filenames("air_quality_data", city_name, target_date)

    if html_filepath.exists() and json_filepath.exists():
        print(f"summary files for {target_date} already exists... skipping save")
    else:
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Populated html saved as {html_filepath}...")

        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(filtered_city_dictionary, f, indent=4)
        print(f"Dictionary saved as {json_filepath}...")


def main():
    """
    Executes the main body of the script.
        :returns: None
        :raises None: None
    """
    token =  get_access_token("WAQI_TOKEN")
    London = requests.get(f"https://api.waqi.info/feed/@5724/?token={token}") 

    cities = [London]
    raw_city_data = {}
    filtered_city_dictionary = {}
    target_date = datetime.now().strftime("%Y-%m-%d")

    for city in cities:
        raw_city_data[city] = city.json()
        city_name, filtered_data = filter_air_quality_data(raw_city_data, city)
        filtered_city_dictionary[city_name] = get_pollutant_data(raw_city_data, city, target_date, filtered_data)
    save_files(city_name, target_date, filtered_city_dictionary)


if __name__ == "__main__":
    main()
